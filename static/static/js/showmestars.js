	function relative_time(parsed_date) {
		var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
		var delta = parseInt((relative_to.getTime() - parsed_date) / 1000);
		//delta = delta - (relative_to.getTimezoneOffset() * 60);
		if (delta < 60) return 'less than a minute ago';
		else if(delta < 120) return 'about a minute ago';
		else if(delta < (45*60)) return (parseInt(delta / 60)).toString() + ' minutes ago';
		else if(delta < (90*60)) return 'about an hour ago';
		else if(delta < (24*60*60)) {
			h = (parseInt(delta / 3600)).toString()
			if(h == 1) return 'about ' + h + ' hour ago';
			else return 'about ' + h + ' hours ago';
		} else if(delta < (48*60*60)) return '1 day ago';
		else return (parseInt(delta / 86400)).toString() + ' days ago';
	}
	
	var planetarium;

	function spinOff(){
		planetarium.az_step = 0;
		if(typeof timer_az!='undefined') clearTimeout(timer_az);
	}
	
    $(document).ready(function() {
		planetarium = new $.virtualsky({id:'starmap',projection:'stereo',latitude:20.707500,longitude:-156.255800,az:180,live:true,constellations:true,gridlines_az:true,callback:{geo:geoIP,mouseenter:spinOff},base:mediaurl,credit:false});
		var objects = [['M1','The Crab Nebula - the remnant from a star which exploded in the year 1054',83.633125,22.014472],['M13','',250.4234750,36.4613194],['M27','Planetary Nebula',299.9015792,22.7210417],['M31','The Andromeda Galaxy',10.684708,41.26875],['M42','The Orion Nebula',83.8220833,-5.3911111],['M56','Globular cluster',289.1482083,30.1834722],['M57','Planetary nebula',283.3961625,33.0291750],['Omega Cen','Globular cluster',201.6970000,-47.4794722],['The Pleiades','Also known as the Seven Sisters',56.8500000,24.1166667],['M101','The Pinwheel Galaxy',210.8021250,54.3480833],['NGC2818','A planetary nebula',139.0069000,-36.6274333],['NGC 6946','Spiral galaxy',308.7180500,60.1536778],['NGC 7331','Spiral galaxy',339.2670917,34.4159194],['NGC 6826','Planetary nebula',296.2006250,50.5250722]];

		for(i = 0 ; i < objects.length ; i++) planetarium.addPointer({ra:objects[i][2],dec:objects[i][3],label:objects[i][0],html:objects[i][1],colour:'rgba(150,150,255,0.5)'});

		planetarium.draw();
		//planetarium.az_step = -0.05;
		//planetarium.moveIt();

		$(".tweet").tweet({
			avatar_size: 32,
			count: 10,
			query: "#showmestars",
			loading_text: "searching twitter...",
			refresh_interval: 30,
			template: '{avatar}<a href="{user_url}">{screen_name}<\/a>:{join}{text}{join}{time}'
		});
		$(".hosttweet").tweet({
			avatar_size: 32,
			count: 7,
			username:["spaceambassador","lcogt","faulkesnorth","faulkessouth"],
			loading_text: "searching twitter...",
			filter: function(t){ return ! /^@\w+/.test(t["tweet_raw_text"]); },
			refresh_interval: 30,
			template: '{avatar}<a href="{user_url}">{screen_name}<\/a>:{join}{text}{join}{time}'
		});
		if($('ul.observations img').length > 0){
			imageLoadError('ul.observations img');
		}
    	var pause = 30000;
    	
		function newContent() {
			var st = $(".updatetime:first").attr('stamp');
			var csrf_token = 0;
			$.get("/showmestars/newimage/?stamp="+st, function(data){
				$("ul.observations-front li.blankitem").remove();
				$("ul.observations-front").prepend(data);
				$("ul.observations-front li").removeClass("endofline");
				$("ul.observations-front li:nth-child(4n+1)").addClass("endofline");
				if($('ul.observations-front img').length > 0){
					imageLoadError('ul.observations-front img');
				}
				if(data && data.indexOf("img") > 0){
					$("ul.observations-front li:eq(1)").css('display','none').fadeIn(1500);
					if($("#emptyobs").length > 0){
						// Remove the warning message
						$("#emptyobs").fadeOut(2000).queue(function() {
							$(this).remove();
						});
					}
				}
			});
			loadObservations();
		}
		function loadObservations(){
/*
			$.getJSON('http://lcogt.net/observations/user/56.json?callback=?',function(data) {
				var obs = data.observation;
				for(var i = 0; i < obs.length ; i++){
					relative = relative_time(new Date(Date.parse(obs[i].time.creation)))
					a = planetarium.addPointer({ra:obs[i].ra,dec:obs[i].dec,label:obs[i].label+' ('+relative+')',img:obs[i].image.thumb,url:obs[i]._about,credit:obs[i].observer.label,colour:'rgb(255,255,255)'})
				}
				planetarium.draw();
			});
*/
		}
        function imageLoadError(el){
            $(el).each(function(){
                    // Work	around for error function reporting of file load failure
                    this.src = this.src;
                    $(this).bind('error',function() {
                     	this.src = "/agentexoplanet/media/images/thumb_missing.png";
                     	this.alt = "Image unavailable";
                            this.onerror = "";
                            return true;
                    })
            });
        }
        function reloadImages() {
            $(".livestatic").each(function() {
                url = $(this).attr("src");
                $(this).attr("src", url.split("?")[0] + "?" + Math.random());
            });
        }
        setInterval(reloadImages, pause);
        interval = setInterval(newContent, pause);
		loadObservations();
		if($("ul.observations-front li img").length == 0){
			$("ul.observations-front").before('<div id="emptyobs">No observations have been made yet. This page will automatically refresh every 30 seconds to show new images.<\/div>')
		}
    });
	function geoIP(){
		if($('#'+this.id+'_geoip').length == 0){
			var eg = "e.g. Cardiff, UK";
			$('#'+this.id+'_geo').append('<br /><form id="'+this.id+'_geoip"><input id="'+this.id+'_location" value="'+eg+'" style="width:12em;"> <input id="'+this.id+'_geoip_btn" type="submit" value="Search" /><br /><span id="'+this.id+'_geoip_message"></span></form>');
			// Store current state of the keyboard variable
			// When we're in the input field, we don't want to change the sky
			$('#'+this.id+'_location').bind('focus',{sky:this},function(e){
				e.data.sky.keyboard = false;
				if($('#'+e.data.sky.id+'_location').val() == eg) $('#'+e.data.sky.id+'_location').val('');
			}).bind('blur',{sky:this,key:this.keyboard},function(e){
				e.data.sky.keyboard = e.data.key;
				if(!$('#'+e.data.sky.id+'_location').val()){
					$('#'+e.data.sky.id+'_location').val(eg);
					$('#'+e.data.sky.id+'_geoip_message').html('');
					e.data.sky.centreDiv(e.data.sky.id+'_geo');
				}
			});
			$('#'+this.id+'_geoip').bind('submit',{sky:this},function(e){
				e.preventDefault();
				if($('#'+e.data.sky.id+'_location').val() == eg){
					$('#'+e.data.sky.id+'_geoip_message').html('You need to enter a place to search for.');
					return false;
				}
				var _object = e.data.sky;
				$('#'+e.data.sky.id+'_geoip_message').html('Trying to identify location...')
				loc = escape($('#'+e.data.sky.id+'_location').val());
				$.ajax({
					dataType: "json", 
					url:'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20geo.places%20where%20text%3D%22'+loc+'%22&format=json&diagnostics=true&callback=?',
					context: _object,
					success: function(data){
						place = data.query.results.place;
						sky = e.data.sky;
						if(place.length > 1){
							$('#'+sky.id+'_geoip_message').html('Found several possibilities:<ul>');
							for(i = 0; i < place.length ; i++){
								placestring = place[i].name+', '+place[i].admin1.content+', '+place[i].country.content;
								$('#'+sky.id+'_geoip_message').append('<li><a href="#" id="geoip_loc_'+i+'">'+placestring+'</a></li>');
								$('#geoip_loc_'+i).bind('click',{sky:sky,place:place[i]},function(e){
									sky = e.data.sky;
									sky.latitude = parseFloat(e.data.place.centroid.latitude);
									sky.longitude = parseFloat(e.data.place.centroid.longitude);
									$('#'+sky.id+'_lat').val(sky.latitude);
									$('#'+sky.id+'_long').val(sky.longitude);
									sky.draw();
								})
							}
							$('#'+sky.id+'_geoip_message').append('</ul>');
							sky.centreDiv(sky.id+'_geo');
						}else{
							if(data.query.results.place.centroid){
								lat = data.query.results.place.centroid.latitude;
								lon = data.query.results.place.centroid.longitude;
								place = data.query.results.place.placeTypeName.content+' in '+data.query.results.place.country.content
								this.latitude = parseFloat(lat);
								this.longitude = parseFloat(lon);
								$('#'+this.id+'_lat').val(this.latitude);
								$('#'+this.id+'_long').val(this.longitude);
								$('#'+this.id+'_geoip_message').html(place);
								this.draw();
							}else{
								$('#'+this.id+'_geoip_message').html('Failed to find the location');
							}
						}
					}
				});
			});
		}
	}
