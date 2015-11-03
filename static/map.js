



$(document).ready(function () {
	document.querySelector("google-map").addEventListener('api-load', function(e) {
      map.init();
  });
	$("#tButton").click(function() {
		st = "Thu, 01 Jan 1970 05:00:00 GMT";
		end = "Sat, 01 Jan 2050 05:00:00 GMT";
		radius = 10;
		tags = [];
		
		if($('#startTimePicker').data("DateTimePicker").date() != null){
		st = $('#startTimePicker').data("DateTimePicker").date().toDate().toUTCString();
		}
		start = $('#startTimePicker');
		
		if($('#endTimePicker').data("DateTimePicker").date() != null){
		end = $('#endTimePicker').data("DateTimePicker").date().toDate().toUTCString();
		}
		
		if( $('#radius').val() != ""){
			radius = $('#radius').val();
		}
		
		temp = $('#tags').val();
		if(temp.length != 0){
		temp = temp.replace(/ /g,'');
		temp = temp.toLowerCase();
		tags = temp.split(',');
		}
		filterBy(st, end, radius,tags);
	})
});


var map = {
	mapElement: null,
	map: null,
	markers: null,
	zoom: null,
	leftBound: null,
	rightBound: null,
	bottomBound: null,
	topBound: null,

	init: function() {
		map.mapElement = document.querySelector("google-map");
		map.map = map.mapElement.map;
		map.zoom = map.map.getZoom();
		map.markers = document.querySelectorAll("google-map-marker")


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



function filterBy(startTime, endTime, rad, tags) {
	$.getJSON($SCRIPT_ROOT + '/filter', {
        start: startTime,
        end: endTime,
        radius: rad,
        tags: JSON.stringify(tags)        
      }, 
      function(data) {
        for(var i = 0; i < map.markers.length; i++) {
        	if(isIn(map.markers[i], data) == null) {
        		map.markers[i].marker.setMap(null);
        	}
        }
        for(var i = 0; i < data.length; i++) {
        	console.log(data);
        	temp = isIn(data[i], map.markers);
        	if(temp != null) {
        		temp.marker.setMap(map.map);
        	}
        	else {
        		var m = document.createElement('google-map-marker');

				m.longitude = data[i].location.longitude;
				m.latitude = data[i].location.latitude;
				m.title = data[i].title;
				var h3 = document.createElement("h3");
				var a = document.createElement("a");
				a.href = "/event/" + data[i].id;
				a.innerText = data[i].title;
				h3.appendChild(a);
				m.appendChild(h3);
				var p1 = document.createElement("p");
				p1.innerText = data[i].description;
				m.appendChild(p1);
				var p2 = document.createElement("p");
				var sd  = new Date(data.start_date);
				var ed = new Date(data.end_date);
				p2.innerText = sd + " -- " + ed;
				m.appendChild(p2);
				var p3 = document.createElement("p");
				p3.innerText = data[i].location.address;
				m.appendChild(p3);
				map.mapElement.appendChild(m);
        	}
        }

      });

}

function isIn(m, l) {
	for(var i = 0; i < l.length; i++) {
		if(l[i].title.trim() == m.title.trim()) {
			return l[i];
		}
	}
	return null;
}
