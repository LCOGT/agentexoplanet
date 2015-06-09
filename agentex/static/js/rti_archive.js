// This is the Javascript for the RTI "Search Public Archive" form
// First we check if jQuery exists. If it doesn't we won't do anything.
if (jQuery) {
	// A counter to keep track of how many js files we've loaded
	var loaded = 0;
	var obs_img = '';

	// We don't want to do anything until the document is loaded as 
	// we have to make sure we have chance to get the rti_path from 
	// the document (Drupal includes it after this js file).
	$(document).ready(function(){
		// If rti_path still doesn't exist we shall make it empty but not undefined
		if(typeof rti_path=="undefined") rti_path = '';
		// Load the jquery.ui files and check if we've loaded them all
		$.getScript("/"+rti_path+"/ui/minified/jquery.ui.core.min.js",function(){ loaded++; loaded_rti();});
		$.getScript("/"+rti_path+"/ui/minified/jquery.ui.widget.min.js",function(){ loaded++; loaded_rti();});
		$.getScript("/"+rti_path+"/ui/minified/jquery.ui.datepicker.min.js",function(){ loaded++; loaded_rti();});
		$('head').append('<link rel="stylesheet" href="/'+rti_path+'/jquery-ui.css" type="text/css" />');
		if($('img.observation-image').length > 0){
			// Check for failure to load images and use a dummy image
            imageLoadError('img.observation-image');
		}
		if($('.thumbnail img').length > 0){
            imageLoadError('.thumbnail img');
		}
		if($('.stream img').length > 0){
		    imageLoadError('.stream img');
		}
		$('.observer').each(function(){
			var html = $(this).html()
			if(html.length > 13) $(this).html(html.substring(0,11)+"...");
		});
		if($('input.searchbox').length > 0){
			$('input.searchbox').val($('input.searchbox').attr('title')).css({'color':'#999'}).focus(function(){
				if($(this).val() == $(this).attr('title')) $(this).val('').css({'color':'black'});
			}).blur(function(){
				if($(this).val() == "") $(this).val($(this).attr('title')).css({'color':'#999'});
			});
		}
	});
    function imageLoadError(el){
        $(el).each(function(){
                // Work	around for error function reporting of file load failure
                this.src = this.src;
                $(this).bind('error',function() {
                 	this.src = "http://lcogt.net/files/imagecache/large/egomez/no-image_120.png";
                 	this.alt = "Image unavailable";
                        this.onerror = "";
                        return true;
                })
        });
    }
	function show_first_hint(){
    	$("#archive-helphint").html("Enter the name of a single astronomical object e.g. <em>Orion Nebula</em>. Note that this is a simple text search so if you enter, say, <em>Saturn</em> the results will include both the planet and NGC7009 (Saturn Nebula).").show();
    	var t = $('#edit-ObName').position().top;
	    $("#archive-helper").css({"position":"absolute","margin-top":t+"px","width":$("#archive-col2").width()-$("#archive-helper-arrow").outerWidth()}).show();
    }
	function loaded_rti(){
		// If we've loaded all the jquery.ui files we will add the functions
		if(loaded < 3) return true;

		if($('#edit-ObName').length > 0){
			// Add the focus help for the object name field
			$('#edit-ObName').focus();
        	show_first_hint();
			$("#edit-ObName").focus(function(){
        	    show_first_hint();
			});
			// Set the behaviour for leaving the field
			$("#edit-ObName").blur(function(){ $("#archive-helper").hide(); });

			$("#archive-daterange").click(function(){
				$("#archive-helphint").html("Do you want to limit your search to a particular range of dates?").show();
				var t = $(this).position().top-10;
				$("#archive-helper").css({"position":"absolute","margin-top":t+"px"}).show();
			});
			$("#archive-datetime").hide();
			$("#archive-objecttype-info").hide();
			$("input[name=\'DateRange\']").change(function(){
				if ($(this).val() == "select") $("#archive-datetime").show();
				else $("#archive-datetime").hide();
				$(this).blur();
			});
			$("input[name=\'DateRange\']").focus(function(){
				if ($(this).val() == "select") $("#archive-datetime").show();
				else $("#archive-datetime").hide();
				$(this).blur();
			});
			$("#edit-StartDate-wrapper").click(function(){ 
				$("#archive-helphint").html("Select the first date to be included in the search.").show();
				var t = $("#edit-StartDate-year").position().top-10;
				$("#archive-helper").css({"position":"absolute","margin-top":t+"px"}).show();
			});
			$("#edit-StartDate-wrapper").blur(function(){ $("#archive-helper").hide(); });
			$("#edit-EndDate-wrapper").click(function(){
				$("#archive-helphint").html("Select the last date to be included in the search.").show();
				var t = $("#edit-EndDate-year").position().top-10;
				$("#archive-helper").css({"position":"absolute","margin-top":t+"px"}).show();
			});
			$("#edit-EndDate-wrapper").blur(function(){ $("#archive-helper").hide(); });
			$("#edit-telid").click(function(){
				$("#archive-helphint").html("Choose the telescope that you wish to find results for. If you have no preference, leave this option set to &quot;All&quot;.").show();
				var t = $(this).position().top-10;
				$("#archive-helper").css({"position":"absolute","margin-top":t+"px"}).show();
			});
			$("#edit-telid").blur(function(){ $("#archive-helper").hide(); });
			$("#edit-filter").click(function(){
				$("#archive-helphint").html("Do you only want to see observations taken with a <a href=\"http://lcogt.net/en/network/instrumentation/filtertypes\">specific filter</a>? If so, select it here.").show();
				var t = $(this).position().top-10;
				$("#archive-helper").css({"position":"absolute","margin-top":t+"px"}).show();
			});
			$(function(){
				// initialise the "Select date" link
				// associate the link with a date picker
				$("#StartDate-pick").datepicker({
					buttonImage: "/"+rti_path+"/images/calendar.gif",
					buttonImageOnly: true,
					showOn: "button",
					minDate:"01/01/2004",
					maxDate:"+0d",
					onSelect:function(dateText, inst){
						updateSelects(dateText,"edit-StartDate-");
					},
					beforeShow:function(input, inst){
						var d = new Date(
							$("#edit-StartDate-year").val(),
							$("#edit-StartDate-month").val()-1,
							$("#edit-StartDate-day").val()
						);
						$(input).datepicker( "setDate" , d );
					}
				});
				
				$("#EndDate-pick").datepicker({
					buttonImage: "/"+rti_path+"/images/calendar.gif",
					buttonImageOnly: true,
					showOn: "button",
					minDate:"01/01/2004",
					maxDate:"+0d",
					onSelect:function(dateText, inst){
						updateSelects(dateText,"edit-EndDate-");
					},
					beforeShow:function(input, inst){
						var d = new Date(
							$("#edit-EndDate-year").val(),
							$("#edit-EndDate-month").val()-1,
							$("#edit-EndDate-day").val()
						);
						$(input).datepicker( "setDate" , d );
					}
				});
				
				var updateSelects = function (selectedDate,el){
					var selectedDate = new Date(selectedDate);
					$("#"+el+"day option[value=" + selectedDate.getDate() + "]").attr("selected", "selected");
					$("#"+el+"month option[value=" + (selectedDate.getMonth()+1) + "]").attr("selected", "selected");
					$("#"+el+"year option[value=" + (selectedDate.getFullYear()) + "]").attr("selected", "selected");
				}
			});
		}

	}
	var http_request = false;
	var lookup_query = "";
	
	if (Drupal.jsEnabled) {
		$(document).ready(function() {
			if($('#edit-ObName').length > 0){
				$("#edit-ObName").blur(function(){
					// We only want to fire off a request if the name has changed
					if($('#edit-ObName').val() != lookup_query){
						lookup_query = $('#edit-ObName').val()
						rti_archive_lookUP(lookup_query);
					}
				});
			}
		});
	}
	
	function rti_archive_lookUP(val) {
		if(val){
			var el = document.getElementById("lookupresults")
			if(el){
				$('#archive-objecttype-info').show();
				el.innerHTML = "<p style=\"font-size:0.8em;\">Attempting to find details of "+val+"...</p>"
			}
			var headID = document.getElementsByTagName("head")[0];         
			var newScript = document.createElement('script');
			newScript.type = 'text/javascript';
			newScript.src = 'http://www.strudel.org.uk/lookUP/json/?name='+val+'&callback=rti_archive_getLookUPResults';
			headID.appendChild(newScript);
		}
	}
	
	function rti_archive_getLookUPResults(jData) {
		if(jData == null){
			alert("There was a problem parsing search results");
			return;
		}
		var equinox = jData.equinox;
		var target = jData.target;
		var coordsys = jData.coordsys;
		var ra = jData.ra
		var dec = jData.dec;
		var gal = jData.galactic;
		var category = jData.category;
		var service = jData.service;
		var image = jData.image;
		var el = document.getElementById("lookupresults")
		if(el){
			if(!ra){
					var str = target.name+" was not found. Are you sure it exists?";
			}else{
				if(target.suggestion){
					var str = target.name+" was not found. Did you mean <a href='#' onClick=\"iDidMean('"+target.suggestion+"')\">"+target.suggestion+"</a>?";
				}else{
					var str = target.name;
					if(category.avmdesc) str += " ("+category.avmdesc+")";
					if(ra && dec){
						if(ra.h < 10 && ra.h.length == 1) ra.h = "0"+ra.h;
						if(ra.m < 10) ra.m = "0"+ra.m;
						if(ra.s < 10) ra.s = "0"+(Math.round(ra.s*10)/10);
						str += " is ";
					}
					if(service.name == "SkyBot") str += "currently ";
					if(ra && dec) str += "at "+ra.h+":"+ra.m+":"+ra.s+", "+dec.d+":"+dec.m+":"+(Math.round(dec.s*100)/100)
					//if(ra && dec) str += " "+equinox+"";
					str += ".";
					angle = (category.avmdesc == "Constellation") ? 45 : 1.25;
					wikizoom = (category.avmdesc == "Constellation") ? 1 : 6;
					//if(service) str += " Find out <a href=\""+service.href+"\">more info about "+target.name+" from "+service.name+"</a>.";
					str += "";
				}
			}
			el.innerHTML = str
		}
	}
	function iDidMean(object) {
		$('#edit-ObName').val(object)
		rti_archive_lookUP(object);
	}
	
	// Javascript for results thumbnails
	$(document).ready(function(){
		$(".observation-results li").each(function(index) {
			$(this).find('.thumbnail a').after('<a href="" class="more-info-hint" id="more-info-hint-'+index+'">i</a>');
			$(this).bind('mouseenter',function(){
				//$(".more-info-hint").hide("fast");
				//$("#more-info-hint-"+index).show();
			}).bind('mouseleave',function(){
				//$(".more-info-hint").hide("fast");
				//$("#more-info-hint-"+index).hide();
			});
			$("#more-info-hint-"+index).bind('click',{idx:index,img:$(this).find('img').attr('src'),link:$(this).find('a').attr('href'),observer:$(this).find('.observer').attr('title')},function(event){
				if($('.show-details').size() == 0) $('body').append('<div class="show-details"></div>');
				var img = event.data.img.replace("_120.jpg","_150.jpg");
				var img_full = event.data.img.replace("_120.jpg",".jpg");
				$('.show-details').html('<div class="show-details-close">&times;</div><a href="'+event.data.link+'" title="Click for full size version"><img src="'+img+'" style="width:150px;height:150px;" /></a>'+$('.observation-results li .more-info').eq(event.data.idx).html()+'<div class="observer">Observer: <a href="'+$('a.observer').eq(event.data.idx).attr('href')+'">'+event.data.observer+'</a></div>');
				centreDiv('.show-details');
				if ($('.show-details').is(':visible')){
					$('.show-details').fadeOut("fast");
				}else{
					$('.show-details').fadeIn("fast");
				}
				$('.show-details-close').bind("click",function(){
					$('.show-details').fadeOut("slow");
				});
				return false;
			});
		});
	});
	
	centreDiv = function(el){
		var wide = $(window).width();
		var tall = $(window).height();
		$(el).css({left:(wide-$(el).outerWidth())/2,top:($(window).scrollTop()+(tall-$(el).outerHeight())/2)});
	}
}