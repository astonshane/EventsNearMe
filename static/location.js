$("document").ready(function() {
		navigator.geolocation.getCurrentPosition(showMap, showError);
		//bootbox.alert("hi");
	});
	
		
	function showMap(position) {
		var map = document.querySelector('google-map');
		map.latitude = position.coords.latitude;
		map.longitude = position.coords.longitude;
		  
		$("google-map").append('<google-map-marker latitude=' + position.coords.latitude + ' longitude=' + position.coords.longitude +' title="You"></google-map-marker>'); 
		}
	
	function showMap2(lat,lng) {
		var map = document.querySelector('google-map');
		map.latitude = lat
		map.longitude = lng;
		  
		$("google-map").append('<google-map-marker latitude=' + lat + ' longitude=' + lng +' title="You"></google-map-marker>'); 
		}
		
	function showError(error) {	
		//Make element visable		
		bootbox.prompt("Enter your 5 digit zip", function(result) {                
			if (result === null || result < 10000 || result > 99999) {                                             
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
