    	$(function(){
    	
    		//State Machine Factory
			var createFSMFactory = function(init,handler){
				return StateMachine.create({
				  initial: 'A',
				  events: [
				    { name: 'init',  from: 'A',                             to: 'B' },
				    { name: 'test',  from: 'B',                             to: 'C'},
				    { name: 'pass',  from: 'C',                             to: 'B'},
				    { name: 'test',  from: 'D',								to: 'C'},
				    { name: 'fail',  from: 'C',                             to: 'D'},
				  ],
				  callbacks: {
				    oninit:  function(event, from, to, msg) { handler[event](msg); },
				    ontest:  function(event, from, to, msg) { handler[event](msg); },
				    onpass:  function(event, from, to,msg)      { handler[event](msg); },
				    onfail:  function(event, from, to,msg)      { handler[event](msg);  }
				  }
				});				
			
			};
			

			//Maps related goodness
			
			//Styling Custom
	   		var styles = [ { "featureType": "landscape", "stylers": [ { "color": "#dddddd" }, { "visibility": "simplified" }, { "saturation": 1 }, 

			{ "lightness": 45 } ] },{ "featureType": "road", "elementType": "geometry", "stylers": [ { "visibility": "simplified" }, { 
			
			"color": "#ffffff" } ] },{ "featureType": "road", "elementType": "labels.text", "stylers": [ { "visibility": "on" } ] },{ 
			
			"featureType": "poi", "elementType": "geometry", "stylers": [ { "visibility": "off" } ] },{ "featureType": "water", 
			
			"stylers": [ { "color": "#c8c8c8" } ] },{ "featureType": "road.highway", "elementType": "labels", "stylers": [ { 
			
			"visibility": "off" } ] },{ "featureType": "poi", "stylers": [ { "visibility": "off" } ] },{ "featureType": 
			
			"road.arterial", "stylers": [ { "visibility": "off" } ] },{ "featureType": "transit", "stylers": [ { "visibility": "off" } 
			
			] },{ "featureType": "administrative.country", "elementType": "geometry.stroke", "stylers": [ { "visibility": "simplified" 
			
			}, { "color": "#ffffff" } ] },{ "featureType": "administrative.neighborhood", "elementType": "labels", "stylers": [ { 
			
			"visibility": "off" } ] },{ "featureType": "landscape", "elementType": "geometry", "stylers": [ { "weight": 0.1 }, { 
			
			"visibility": "simplified" }, { "color": "#dddddd" }, { "lightness": 45 } ] },{ "featureType": "administrative",
			
			"elementType": "labels.text", "stylers": [ { "weight": 0.1 }, { "color": "#787878" } ] },{ "featureType": 
			
			"administrative", "elementType": "labels.icon", "stylers": [ { "visibility": "off" } ] }];
				   
	   
		    var mapOptions = {
	          center: new google.maps.LatLng(-34.397, 150.644),
	          zoom: 8,
	          mapTypeId: google.maps.MapTypeId.ROADMAP,
	          styles:styles,
	          scrollwheel:false
	        };
	        var map = new google.maps.Map(document.getElementById("map"),
	            mapOptions);
	       
			 
			var redicon = 
		    new google.maps.MarkerImage(
		      '/static/img/marker_icon_pink.png', 
		      new google.maps.Size(30, 38),
		      // The origin for this image is 0,0.
		      new google.maps.Point(0,0),
		      // The anchor for this image is the base of the flagpole at 0,32.
		      new google.maps.Point(12, 38));
		    var blueicon = 
		    new google.maps.MarkerImage(
		      '/static/img/marker_icon_blue.png', 
		      new google.maps.Size(30, 38),
		      // The origin for this image is 0,0.
		      new google.maps.Point(0,38),
		      // The anchor for this image is the base of the flagpole at 0,32.
		      new google.maps.Point(12, 38));
		    
			var createMarkerFactory = function(map,label){
				var marker = new MarkerWithLabel({
			      draggable: true,
			      map: map,
			      labelContent: label,
			      labelAnchor: new google.maps.Point(22, 0),
			      labelClass: "labels", // the CSS class for the label
			      labelStyle: {opacity: 0.75},
			    });
			
			    var iw = new google.maps.InfoWindow({
			      content: "Home For Sale"
			    });
			     
			    google.maps.event.addListener(marker, "click", function (e) { iw.open(map, marker); });
				return marker;
			}
			
			var updatePosition= function(marker,lat,lng){
				var latlng = new google.maps.LatLng(lat,lng);								
				marker.setPosition(latlng);
			}
			
			var updateIcon = function(marker,state){
				if(state == 10.1 || state == 10.1-3.2 || (state >= 10.4 && state <=10.7)|| (state >= 10.4-3.2 && state <=10.7-3.2)){
                        marker.setIcon(redicon); 
               	}else if ((state >= 9.7 && state <=10.0) || (state >= 10.2 && state <=10.3) ||
	                (state >= 9.7-3.2 && state <=10.0-3.2) ||(state >= 10.2-3.2 && state <=10.3-3.2)){
	                marker.setIcon(blueicon); 	                
               	}
                else{
                    marker.setIcon(blueicon);
      	        }
			};
			
			var markers = {};
			var handle = function(data){					
					if(data.latitude  && data.longitude){
						if (!markers.hasOwnProperty(data['deviceID']) ){
							markers[data['deviceID']] = createMarkerFactory(map,data.deviceID);					
						}					
						updatePosition(markers[data['deviceID']], parseFloat(data.latitude),parseFloat(data.longitude));
						if(data.statusCode){
							updateIcon(markers[data['deviceID']]), parseInt(data.statusCode));
						}
					}										
				};
				
			var handleData= function(data){	 	
				if(dataPacket instanceof Array){
			       			for(var p in dataPacket){
			       				handle(dataPacket[p]);
			       			}
			       		}else{
			       			handle(dataPacket);
			       		}				
			};
    	
    		
    		var ws = new WebSocket('ws://localhost:9999/update');
			var bid = $('#bid');	
			var dataBuffer=''; //holds temporary data if stream is sending > 4096 bytes
			ws.onopen = function()
		    {
		        // Web Socket is connected, send data using send()
		        //ws.send("Message to send");
		        //alert("Message is sent...");
		    };
		    ws.onmessage = function (event) 
		    { 
		     try{
		     		var buffer = $.parseJSON(event.data);		     		
		     		var lines = buffer.split(/\r?\n/g);
			       	var bytes = parseInt(lines[0]);
			       	dataBuffer+= lines[1];		
			       	/*ensure a full packet is sent by server before calling, still no account for out of order messaging*/       						       	
			       	if(bytes >2 && bytes <4096){
			       		
			       		dataPacket = $.parseJSON(dataBuffer);
			       		handleData(dataPacket);
			       		dataBuffer = '';			       			
			        }
			       	lines = null;
			       	
		       }catch(err)
		       {
		       		//we need to release the databuffer, we may have lost the event :(
			  		dataBuffer = '';
		       }


		    };
		    ws.onclose = function()
		    { 
		       // websocket is closed.
		        alert("Connection is closed..."); 
		    };
		    
		    
		})