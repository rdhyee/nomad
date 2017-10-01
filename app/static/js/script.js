


// ======= GOOGLE MAPS ===========

  // Virginia locations
  var westva = {lat: 38.7624, lng: -79.7170677};
  var sweetbriar = {lat: 37.5551696, lng: -79.098562};

  // Baltimore locations
  var baltLocations = [
    {lat: 39.3146481, lng: -76.6419097}, 
    {lat: 39.336027, lng: -76.574490}, 
    {lat: 39.278518, lng: -76.640065}, 
    {lat: 39.277858, lng: -76.542218}, 
    {lat: 39.351572, lng: -76.641438}
  ];
  var baltCenter = {lat: 39.314246, lng: -76.601955};
  var markers = [];
  var map;

function initMap() {

  map = new google.maps.Map(document.getElementById('background-map'), {
    zoom: 12,
    center: baltCenter,
    styles: mapStyleDiscreet
  });

  for (var i=0; i < baltLocations.length; i++) {
    markers.push(
      new google.maps.Marker({
        position: new google.maps.LatLng(baltLocations[i].lat, baltLocations[i].lng),
        map: map,
        icon: normalIcon()
      })
    );
  }
}

function normalIcon() {
  return {
    url: 'img/ic_marker_inactive.svg'
  };
}
function highlightedIcon() {
  return {
    url: 'img/ic_marker_active.svg'
  };
}

var activeDetail = false;

$(document).ready(function() {
  $('.results-box .result').hover(
    // mouse in
    function () {
      var index = $('.results-box .result').index(this);
      markers[index].setIcon(highlightedIcon());

    },
    // mouse out
    function () {
      var index = $('.results-box .result').index(this);
      markers[index].setIcon(normalIcon());
    }
  );
  $('.results-box .result').click(
    function () {
      if (activeDetail == false) {
        // open detail panel
        activeDetail = true;
        $('.right-bar').addClass("active");
        // recenter map on current marker
        var index = $('.results-box .result').index(this);
        console.log(markers[index].position);
        map.setCenter(markers[index].position);
      } else {
        // close detail panel
        activeDetail = false;
        $('.right-bar').removeClass("active");
      }
    })
});


