

function initMap() {
	var mapElement = document.querySelector("google-map");
  	console.log(mapElement.map);
  	google.maps.event.addListener(mapElement.map, 'zoom_changed', function() {
    	console.log(mapElement.map.getBounds().getSouthWest());
    	console.log("DER");
    });
    console.log("DER");

}


$(document).ready(function () {
	document.querySelector("google-map").addEventListener('api-load', function(e) {
      initMap();
  });
	$("#tButton").click(function() {
		st = $('#datetimepicker6').data("DateTimePicker").date().toDate().toUTCString();
		end = $('#datetimepicker7').data("DateTimePicker").date().toDate().toUTCString();
		console.log(st);
		console.log(end);
		filterBy(st, end);
	})
});


var map = {
	mapElement: null,
	map: null,
	zoom: null,
	leftBound: null,
	rightBound: null,
	bottomBound: null,
	topBound: null,

	init: function() {
		map.mapElement = document.querySelector("google-map");
		map.map = map.mapElement.map;
		map.zoom = map.map.getZoom();
		

	},

	updateBounds: function() {
		map.leftBound = map.map.getBounds.getSouthWest().lng();
		map.bottomBound = map.map.getBounds.getSouthWest().lat();
		map.rightBound = map.map.getBounds.getNorthEast().lng();
		map.topBound = map.map.getBounds.getNorthEast().lat();
	},

	move: function() {
		map.updateBounds();
		filterBy(map.leftBound, map.rightBound, map.bottomBound, map.topBound);

		$.getJSON($SCRIPT_ROOT + '/mapmove', {
        	lb: map.leftBound,
        	rb: map.rightBound,
        	bb: map.bottomBound,
        	tb: map.topBound,
        	name: response.name
      	}, function(data) {
        	console.log("RESULT: " + data);
      	});
	}
};



function filterBy(startTime, endTime) {
	$.getJSON($SCRIPT_ROOT + '/filter', {
        start: startTime,
        end: endTime
      }, 
      function(data) {
        console.log("RESULT: " + data);
      });

}