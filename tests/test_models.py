# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

import flask_login.utils

from app.models import Person, RideRequest, Role

from .factories import CarpoolFactory, PersonFactory


@pytest.mark.usefixtures('db')
class TestPerson:
    """Person tests."""

    def test_created_at_defaults_to_datetime(self, db):
        """Test creation date."""
        person = Person(social_id='foo', email='foo@bar.com')
        db.session.add(person)
        db.session.commit()
        assert bool(person.created_at)
        assert isinstance(person.created_at, dt.datetime)

    def test_factory(self, db):
        """Test person factory."""
        person = PersonFactory(email='foo@bar.com')
        db.session.commit()
        assert bool(person.social_id)
        assert bool(person.email)
        assert bool(person.created_at)

    def test_get_id(self):
        person = PersonFactory()
        assert person.get_id() == person.uuid

    def test_gender_string(self):
        person = PersonFactory(gender='Female')
        assert person.gender_string() == person.gender

    def test_gender_string_self_describe(self):
        person = PersonFactory(gender='Self-described', gender_self_describe='self-described gender')
        assert person.gender_string() == '{} as {}'.format(person.gender, person.gender_self_describe)

    def test_roles(self):
        """Add a role to a user."""
        role = Role(name='admin')
        person = PersonFactory()
        assert role not in person.roles
        assert not person.has_roles('admin')

        person.roles.append(role)
        assert role in person.roles
        assert person.has_roles('admin')


@pytest.mark.usefixtures('db')
class TestCarpool:
    """Carpool tests."""

    def test_get_ride_requests_query(self, db):
        """Test get ride requests query"""
        carpool_1 = CarpoolFactory()
        carpool_2 = CarpoolFactory()

        person = PersonFactory()

        ride_request_1 = RideRequest(
            person = person,
            carpool = carpool_1,
        )
        ride_request_2 = RideRequest(
            person = person,
            carpool = carpool_1,
            status = 'approved',
        )
        ride_request_3 = RideRequest(
            person = person,
            carpool = carpool_2,
            status = 'rejected',
        )

        db.session.add_all([
            carpool_1,
            carpool_2,
            person,
            ride_request_1,
            ride_request_2,
            ride_request_3,
        ])
        db.session.commit()

        all_ride_requests = \
            carpool_1.get_ride_requests_query().all()

        assert len(all_ride_requests) == 2
        assert all_ride_requests[0] is ride_request_1
        assert all_ride_requests[1] is ride_request_2

        approved_ride_requests = \
            carpool_1.get_ride_requests_query([ 'approved' ]).all()

        assert len(approved_ride_requests) == 1
        assert approved_ride_requests[0] is ride_request_2

    def test_get_current_user_ride_request_not_logged_in(self):
        """Test get curent user ride request when user is not logged in"""
        carpool = CarpoolFactory()
        assert carpool.get_current_user_ride_request() == None

    def test_get_current_user_ride_request_logged_in(self, db, monkeypatch):
        """Test get curent user ride request when user is logged in"""
        carpool = CarpoolFactory()

        person_1 = PersonFactory()
        person_2 = PersonFactory()

        ride_request_1 = RideRequest(
            person = person_2,
            carpool = carpool,
        )
        ride_request_2 = RideRequest(
            person = person_1,
            carpool = carpool,
        )

        db.session.add_all([
            carpool,
            person_1,
            person_2,
            ride_request_1,
            ride_request_2,
        ])
        db.session.commit()

        monkeypatch.setattr(
            flask_login.utils,
            '_get_user',
            lambda: person_1,
        )

        assert carpool.get_current_user_ride_request() is ride_request_2

    def test_current_user_is_driver_not_logged_in(self):
        """Test current user is driver property when user is not logged in"""
        carpool = CarpoolFactory()
        assert carpool.current_user_is_driver == False

    def test_current_user_is_driver_logged_in(self, db, monkeypatch):
        """Test current user is driver property when user is logged in"""
        person_1 = PersonFactory()
        person_2 = PersonFactory()

        carpool_1 = CarpoolFactory(driver = person_1)
        carpool_2 = CarpoolFactory(driver = person_2)

        db.session.add_all([
            person_1,
            person_2,
            carpool_1,
            carpool_2,
        ])
        db.session.commit()

        monkeypatch.setattr(
            flask_login.utils,
            '_get_user',
            lambda: person_1,
        )

        assert carpool_1.current_user_is_driver == True
        assert carpool_2.current_user_is_driver == False

    def test_get_when_no_requests(self, db):
        """Test get riders when no ride requests have been made"""
        carpool = CarpoolFactory()
        assert len(carpool.get_riders(['approved'])) == 0

    def test_get_riders(self, db):
        """Test get riders"""
        carpool_1 = CarpoolFactory()
        carpool_2 = CarpoolFactory()

        person_1 = PersonFactory()
        person_2 = PersonFactory()

        ride_request_1 = RideRequest(
            person = person_1,
            carpool = carpool_1,
            status = 'approved',
        )
        ride_request_2 = RideRequest(
            person = person_2,
            carpool = carpool_1,
            status = 'approved',
        )
        ride_request_3 = RideRequest(
            person = person_1,
            carpool = carpool_2,
            status = 'rejected',
        )
        ride_request_4 = RideRequest(
            person = person_2,
            carpool = carpool_2,
            status = 'approved',
        )

        db.session.add_all([
            carpool_1,
            carpool_2,
            person_1,
            person_2,
            ride_request_1,
            ride_request_2,
            ride_request_3,
            ride_request_4,
        ])
        db.session.commit()

        assert len(carpool_1.get_riders(['rejected'])) == 0

        approved_carpool_1_riders = carpool_1.get_riders(['approved'])
        assert len(approved_carpool_1_riders) == 2
        assert approved_carpool_1_riders[0] is person_1
        assert approved_carpool_1_riders[1] is person_2

        rejected_carpool_2_riders = carpool_2.get_riders(['rejected'])

        assert len(rejected_carpool_2_riders) == 1
        assert rejected_carpool_2_riders[0] is person_1

        approved_rejected_carpool_2_riders = carpool_2.get_riders(['approved', 'rejected'])

        assert len(approved_rejected_carpool_2_riders) == 2
        assert approved_rejected_carpool_2_riders[0] is person_1
        assert approved_rejected_carpool_2_riders[1] is person_2

    def test_riders_and_potential_riders_properties(self, db):
        """Test riders and potential riders properties"""
        carpool = CarpoolFactory()

        person_1 = PersonFactory()
        person_2 = PersonFactory()

        ride_request_1 = RideRequest(
            person = person_1,
            carpool = carpool,
            status = 'approved',
        )
        ride_request_2 = RideRequest(
            person = person_2,
            carpool = carpool,
            status = 'requested',
        )

        db.session.add_all([
            carpool,
            person_1,
            person_2,
            ride_request_1,
            ride_request_2,
        ])
        db.session.commit()

        assert len(carpool.riders) == 1
        assert carpool.riders[0] is person_1

        assert len(carpool.riders_and_potential_riders) == 2
        assert carpool.riders_and_potential_riders[0] is person_1
        assert carpool.riders_and_potential_riders[1] is person_2
