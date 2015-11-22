//Get the user's location info
$("document").ready(function() {
  navigator.geolocation.getCurrentPosition(function(positions){
	  showMap2(positions.coords.latitude, positions.coords.longitude);
	  }, showError);
});

//Make sure all the maps-markers are sperate
$( window ).load(function() {
  seperateMarkers();
});

//Function to separate markers that are too close on the map
function seperateMarkers() {
  var mrks = $("google-map-marker");
  for(var i = 0; i < mrks.length; i++)
  {
    for(var j = i+1; j < mrks.length; j++)
    {
      var d = dist(mrks[i],mrks[j]);
      if( d < .01)
      {
        //Adjust these according to zoom
		mrks[j].latitude = Number(mrks[j].latitude) + .0002;
		mrks[j].longitude = Number(mrks[j].longitude) + .0002;
      }

    }
  }
}

//Distance between 2 <google-map-markers>
function dist(x,y) {
  lat1 = x.latitude;
  lat2 = y.latitude;
  lon1 = x.longitude;
  lon2 = y.longitude;

  var p = 0.017453292519943295;    // Math.PI / 180
  var c = Math.cos;
  var a = 0.5 - c((lat2 - lat1) * p)/2 +
  c(lat1 * p) * c(lat2 * p) * (1 - c((lon2 - lon1) * p))/2;

  return 12742 * Math.asin(Math.sqrt(a)); // 2 * R; R = 6371 km
}

//Call back function for getCurrentPosition, updates <google-map> to user's lat lng
function showMap(position) {
  var map = document.querySelector('google-map');
  map.latitude = position.coords.latitude;
  map.longitude = position.coords.longitude;

  console.log(document.cookie);
  document.cookie = "lat=" + position.coords.latitude;
  document.cookie = "lng=" + position.coords.longitude;
  //$("google-map").append('<google-map-marker latitude=' + position.coords.latitude + ' longitude=' + position.coords.longitude +' title="You"></google-map-marker>');
}

//Updates map to inputed lat lng
function showMap2(lat,lng) {
  var map = document.querySelector('google-map');
  map.latitude = lat
  map.longitude = lng;
  document.cookie = "lat=" + lat;
  document.cookie = "lng=" + lng;
  //$("google-map").append('<google-map-marker latitude=' + lat + ' longitude=' + lng +' title="You"></google-map-marker>');
}

//Callback function for getCurrentPosition, prompt's user to enter location manually
function showError(error) {
  bootbox.prompt("Enter your 5 digit zip", function(result) {
  if (result === null) {
	//Default to some random location
    showMap2(37.2350,115.8111); 
  }
  else {
    var url = 'http://maps.googleapis.com/maps/api/geocode/json?address=';
    url = url + result;
    $.getJSON( url, function( data ) {
    lat = data['results'][0]['geometry']['location']['lat'];
    lng = data['results'][0]['geometry']['location']['lng'];
    showMap2(lat,lng);
	});
  }
  });
}
