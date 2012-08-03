// Elements with the class "accessible" are intended for people who don't 
// have Javascript enabled. If we are here they obviously do have Javascript.
document.write('<style type="text/css"> .accessible { display: none; }</style>');

// Requires jQuery to be loaded.
var showhelp = false;
function addHelpHint(el,msg,align,talign){
	// Check for existence of the style "helpityhint". If it doesn't exist, we provide a default
	if($("style:contains('.helpityhint')").length < 1) $("head").append("<style type='text/css'> .helpityhint { box-shadow: 0px 0px 8px rgb(255,0,0)!important; -moz-box-shadow: 0px 0px 8px rgb(255,0,0)!important; -webkit-box-shadow: 0px 0px 8px rgb(255,0,0)!important; cursor: help!important; z-index: 20; } <\/style>");
	// Attach our message as data and attach mouse events
	el.data('help',msg).bind('mouseover',function(e){
		if(showhelp){
			$(this).addClass('helpityhint');
			bubblePopup({id:'helptooltip',el:$(this),html:$(this).data('help'),'padding':10,'align':align,'textalign':talign,z:20});
		}
	}).bind('mouseout',function(){
		if(showhelp){
			$(this).removeClass('helpityhint');
			// We need to allow people to click on links in the help tool tip
			// Give them 1s to get to it and cancel the fadeOut. Then they 
			// can click to hide it.
			$('#helptooltip').bind('mouseover',function(){ $(this).clearQueue(); }).bind('click',function(){ $(this).hide(); });
			$('#helptooltip').delay(1000).fadeOut(500);
		}
	});
}

// Create a popup bubble attached to an element. Requires an object with:
// id = the name to use for the popup
// el = the jQuery element to attach a popup to
// html = the content
// animate = true, false
// align = how to attach the popup ("auto", "left", "right", "top", "bottom", "center")
// fade = ms to fade
// dismiss = true, false
function bubblePopup(inp) {

	// Setup - check for existence of values
	if(typeof inp!="object") return false;
	if(typeof inp.id!="string")	return false;
	if(inp.el){
		if(typeof inp.el=="object" && inp.el.length > 0){
			var w = inp.el.outerWidth();
			var w2 = w/2;
			var h = inp.el.outerHeight();
			var h2 = h/2;
			var x = inp.el.offset().left+w2;	// The centre of the element
			var y = inp.el.offset().top+h2;	// The centre of the element
			if(w < 100) w = 100;	// We don't want the info bubble box to be to narrow
		}else{
			var x = (typeof inp.el.x=="number") ? inp.el.x : -1;
			var y = (typeof inp.el.y=="number") ? inp.el.y : -1;
			var w = (typeof inp.el.w=="number") ? inp.el.w : 0;
			var h = (typeof inp.el.h=="number") ? inp.el.h : 0;
			var w2 = w/2;
			var h2 = h/2;
		}
	}else{
		return false;
	}
	var onpop = "";
	if(typeof inp.onpop=="function") onpop = inp.onpop;
		
	if(x < 0 || y < 0) return false;
	var extra = (typeof inp.button=="boolean") ? '<br /><input type="submit" onclick="$(\'\#'+id+'\').remove()" value="OK">' : '';
	var id = inp.id;
	var el = $('#'+id);
	if(typeof inp.html!="string"){
		if(el.length == 0) return false;
		else inp.html = el.html();
	}
	var animate = (typeof inp.animate=="boolean") ? inp.animate : false;
	var dismiss = (typeof inp.dismiss=="boolean") ? inp.dismiss : false;
	var fade = (typeof inp.fade=="number") ? inp.fade : -1;
	var wide = (typeof inp.w=="number") ? inp.w : w;
	var tall = (typeof inp.h=="number") ? inp.h : -1;
	var z = (typeof inp.z=="number") ? inp.z : 10;	// The z-index
	var arr = (typeof inp.arrow=="number") ? inp.arrow : 30;
	var padding = (typeof inp.padding=="number") ? inp.padding : 4;
	var align = (typeof inp.align=="string") ? inp.align : "auto";
	var talign = (typeof inp.textalign=="string") ? inp.textalign : "center";
	var style = (typeof inp.style=="string") ? " "+inp.style : (el ? " "+el.attr('class') : "");

	// Check for existence of the style "poppitypin". If it doesn't exist, we provide a default
	if($("style:contains('.poppitypin')").length < 1) $("head").append("<style type='text/css'> .poppitypin { padding:10px!important; background-color: white; } .poppitypin:hover { z-index:100!important; }<\/style>");

	if(el.length > 0) el.remove();
	$('body').append('<div id="'+id+'" class="poppitypin chat-bubble'+style+'"><div class="chat-bubble-arrow-border"><\/div><div class="chat-bubble-arrow"><\/div><div class="chat-bubble-html">'+inp.html+extra+'</div><\/div>');
	el = $('#'+id);

	var line = (el.css('borderWidth')) ? parseInt(el.css('borderWidth')) : 1;
	var colour = (el.css('borderLeftColor')) ? el.css('borderLeftColor') : "rgb(100,100,100)";
	var tcolour = (typeof inp.color=="string") ? inp.color : ((el.css('color')) ? el.css('color') : "");
	var bg = (typeof inp.bg=="string") ? inp.bg : ((el.css('background-color')) ? el.css('background-color') : "white");
	$('#'+id+'.chat-bubble').css( {'background-color':bg,'color':tcolour,'border':line+'px solid '+colour,'margin':'0px auto','padding':padding+'px','position':'absolute','width':w+'px','border-radius':'10px','-moz-border-radius':'10px','-webkit-border-radius':'10px','box-shadow':'0 0 20px '+colour,'-moz-box-shadow':'0 0 20px '+colour,'-webkit-box-shadow':'0 0 20px '+colour,'text-align':talign,'z-index':z});

	if(!style) el.css({'position':'absolute','z-index':z,'border':line+'px solid '+colour,'opacity':0});

	if(tall >= 0) el.css('height',tall+'px')
	if(wide >= 0) el.css('width',wide+'px')

	wide = el.outerWidth();
	tall = el.outerHeight();

	var y2 = (y - h2 - tall - arr - padding);

	if(align == "auto"){
		align = "top";
		if((y - h2 - tall - arr - padding) < window.scrollY){
			align = "bottom";
			if(y + h2 + tall + arr + padding > $(window).height()){
				align = "right";
				if(x + wide + arr + padding > $(window).width()) align = "left";
				// Check that this will fit on the screen
				if(x - w2 - wide - arr - padding < 0){
					wide = (x - w2 - arr - padding*2 - line*2)*0.9;
					el.css('width',wide+'px!important');
					$('#'+id+'.chat-bubble').css('width',wide+'px')
					wide = el.outerWidth(true);
				}
			}
		}
	}

	if(align == "right"){
		l = x + w2 + padding + arr/2;
		lorig = x;
		t = y - tall/2;
		torig = t;
		$('#'+id+' div.chat-bubble-arrow-border').css({'left':'-'+(arr*0.5+line)+'px','border-width':Math.round(arr/2)+'px '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px 0'});
		$('#'+id+' div.chat-bubble-arrow').css({'left':'-'+(arr*0.5-parseInt(line/2))+'px','border-width':Math.round(arr/2)+'px '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px 0'});
		$('#'+id+' div.chat-bubble-arrow-border').css({'border-color': "transparent "+colour+" transparent transparent",'border-style': 'solid','height':0,'width':0,'position':'absolute','top':parseInt((tall-arr)/2 - line)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'border-color': "transparent white transparent transparent",'border-style': 'solid','height':0,'width':0,'position':'absolute','top':parseInt((tall-arr)/2 - line)+'px'});
		/* Fix for IE6 transparency */
		if($.browser.msie && parseInt($.browser.version, 10)=="6") $('div.chat-bubble-arrow').css({'_border-top-color': 'pink','_border-bottom-color': 'pink','_border-left-color':'pink','_filter':'chroma(color=pink)'});
	}else if(align == "left"){
		l = x - w2 - padding - wide - arr/2;
		lorig = x - wide;
		t = y - tall/2;
		torig = t;
		$('#'+id+' div.chat-bubble-arrow-border').css({'right':'-'+(arr*0.5+line)+'px','border-width':Math.round(arr/2)+'px 0 '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'right':'-'+(arr*0.5-parseInt(line/2))+'px','border-width':Math.round(arr/2)+'px 0 '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px'});
		$('#'+id+' div.chat-bubble-arrow-border').css({'border-color': "transparent transparent transparent "+colour,'border-style': 'solid','height':0,'width':0,'position':'absolute','top':parseInt((tall-arr)/2 - line)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'border-color': "transparent transparent transparent white",'border-style': 'solid','height':0,'width':0,'position':'absolute','top':parseInt((tall-arr)/2 - line)+'px'});
		/* Fix for IE6 transparency */
		if($.browser.msie && parseInt($.browser.version, 10)=="6") $('div.chat-bubble-arrow').css({'_border-top-color': 'pink','_border-bottom-color': 'pink','_border-right-color':'pink','_filter':'chroma(color=pink)'});
	}else if(align == "top"){
		l = x - wide/2;
		lorig = l;
		t = y - h2 - padding - tall - arr/2;
		torig = y - tall;
		$('#'+id+' div.chat-bubble-arrow-border').css({'bottom':'-'+(arr*0.5+line)+'px','border-width':Math.round(arr/2)+'px '+Math.round(arr/2)+'px 0 '+Math.round(arr/2)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'bottom':'-'+(arr*0.5-parseInt(line/2))+'px','border-width':Math.round(arr/2)+'px '+Math.round(arr/2)+'px 0 '+Math.round(arr/2)+'px'});
		$('#'+id+' div.chat-bubble-arrow-border').css({'border-color': colour+" transparent transparent transparent",'border-style': 'solid','height':0,'width':0,'position':'absolute','left':parseInt((wide-arr)/2 - line)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'border-color': "white transparent transparent transparent",'border-style': 'solid','height':0,'width':0,'position':'absolute','left':parseInt((wide-arr)/2 - line)+'px'});
		/* Fix for IE6 transparency */
		if($.browser.msie && parseInt($.browser.version, 10)=="6") $('div.chat-bubble-arrow').css({'_border-left-color': 'pink','_border-bottom-color': 'pink','_border-right-color':'pink','_filter':'chroma(color=pink)'});
	}else if(align == "bottom"){
		l = x - wide/2;
		lorig = l;//715.9000244140625 250.5 184 32 222 112 88.5
		t = y + h2 + padding + arr/2 - line;
		torig = y + tall;
		$('#'+id+' div.chat-bubble-arrow-border').css({'top':'-'+(arr*0.5+line)+'px','border-width':'0px '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'top':'-'+(arr*0.5-parseInt(line/2))+'px','border-width':'0px '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px '+Math.round(arr/2)+'px'});
		$('#'+id+' div.chat-bubble-arrow-border').css({'border-color': "transparent transparent "+colour+" transparent",'border-style': 'solid','height':0,'width':0,'position':'absolute','left':parseInt((wide-arr)/2 - line)+'px'});
		$('#'+id+' div.chat-bubble-arrow').css({'border-color': "transparent transparent "+bg+" transparent",'border-style': 'solid','height':0,'width':0,'position':'absolute','left':parseInt((wide-arr)/2 - line)+'px'});
		/* Fix for IE6 transparency */
		if($.browser.msie && parseInt($.browser.version, 10)=="6") $('div.chat-bubble-arrow').css({'_border-left-color': 'pink','_border-top-color': 'pink','_border-right-color':'pink','_filter':'chroma(color=pink)'});
	}else if(align == "center" || align == "centre"){
		l = x - wide/2;
		lorig = l;
		t = y - tall/2;
		torig = t;
		$('#'+id+' div.chat-bubble-arrow-border').hide();
		$('#'+id+' div.chat-bubble-arrow').hide();
	}else{
		return;
	}
	if(animate) el.css({'left':lorig,'top':torig,opacity: 0.0}).animate({opacity: 1,'left':l,'top':t},500)
	else el.css({'left':l,'top':t,opacity: 1}).show()
	if(fade > 0) el.delay(fade).fadeOut(fade);
	if(dismiss) el.bind('click',{onpop:onpop},function(e){ $(this).hide(); if(e.data.onpop){ e.data.onpop.call(); }});
}
function showMessage(){
	if($("#message").length==0) $(".page").prepend('<div id="message"></div>')
	$("#message").html(data.message).addClass("error").show();
	$('#message').bind('click',function(e){ $(this).fadeOut(500); } );
}

function defaultColours(){
	colours = { source: {text:"",bg:""},sky: {text:"",bg:""},calibrator: {text:"",bg:""} }
	for(var i = 0; i < document.styleSheets.length; i++) {
		try{
			var sheet = document.styleSheets[i];
			rules = sheet.rules||sheet.cssRules;
			if(rules){
				for(var j = 0; j < rules.length; j++) {
					if(rules[j].selectorText){
						if(rules[j].selectorText.toLowerCase()==".source") colours.source = {bg:stripOpacity(rules[j].style.backgroundColor),text:rules[j].style.color};
						if(rules[j].selectorText.toLowerCase()==".calibrator") colours.calibrator = {bg:stripOpacity(rules[j].style.backgroundColor),text:rules[j].style.color};
						if(rules[j].selectorText.toLowerCase()==".sky") colours.sky = {bg:stripOpacity(rules[j].style.backgroundColor),text:rules[j].style.color};
					}
				}
			}
		}catch(e){
			// If we can't access the stylesheet (probably because it is on another domain) do nothing!
		};
	}
	return colours;
}
function stripOpacity(c){
	if(c.indexOf("rgba") != 0) return c;
	var rgb = c.substring(c.indexOf("(")+1,c.length).split(",");
	return 'rgb('+rgb[0]+','+rgb[1]+','+rgb[2]+')';
}
function unixtohours(timestamp){
	var date = new Date(timestamp);
	// hours part from the timestamp
	var hours = date.getUTCHours();
	// minutes part from the timestamp
	var minutes = date.getUTCMinutes();
	if (hours <=9) hours = "0"+hours;
	if (minutes <= 9 ) minutes = "0"+minutes;
	return hours+":"+minutes;
}

function toggleHelp(el){
	showhelp = !showhelp;
	if(!showhelp){
		$('.helpityhint').removeClass('helpityhint')
		$(el).removeClass('helpactive');
		$('#helptooltip').remove()
	}else{
		$(el).addClass('helpactive');
		msg = ($('#help').html()) ? $('#help').html() : 'Move your mouse over different parts of the page to see specific help.'
		bubblePopup({id:'helptooltip',el:$(el),w:200, align:'left',html:msg,'padding':10,dismiss:true});
	}
	return false;
}


function positionHelperLinks(){
	var tp = 70;
	var p = $('.page').position();
	var top = p.top + tp;
	var tall = $('#mylink').outerHeight();
	var padd = parseInt($('.page').css('padding-right'))/2;

	$('#helplink').css({position:'absolute',left:(p.left+$('.page').outerWidth()+padd),top:(top-tall-5)});
	$('.tablink').css({position:'absolute',left:(p.left+$('.page').outerWidth()+padd)})
	$('#mylink').css({top:top});
	$('#avlink').css({top:top+tall+5});
	$('#sulink').css({top:top+tall+tall+10});
}


// Bind resize event
$(window).resize(function(){
	
	// Re-position helper links mylink
	positionHelperLinks();
});

$(document).ready(function(){
	var tp = 70;
	//$('.accessible').hide();	// These elements are intended for people who don't have Javascript enabled.

	// Set up alternatve graph tabs
	if($('#mylink').length > 0){
		var h = '<div id="mylink" class="tablink'+(($('#mylink').hasClass('tabactive')) ? ' tabactive':'')+'">'+$('#mylink').html()+'<\/div>';
		if($('#avlink').length > 0) h += '<div id="avlink" class="tablink'+(($('#avlink').hasClass('tabactive')) ? ' tabactive':'')+'">'+$('#avlink').html()+'<\/div>';
		if($('#sulink').length > 0) h += '<div id="sulink" class="tablink'+(($('#sulink').hasClass('tabactive')) ? ' tabactive':'')+'">'+$('#sulink').html()+'<\/div>';
		$('#mylink').remove();
		$('#avlink').remove();
		$('#sulink').remove();
		$('body #main').append(h);
		positionHelperLinks();
	}

	if(typeof helper=="boolean" && helper){
		$('body #main').append('<div id="helplink" class="tablink">?<\/div>')
		var p = $('.page').position();
		var tall = $('#helplink').outerHeight();
		//$('#helplink').css({position:'absolute',left:(p.left+$('.page').outerWidth()+(parseInt($('.page').css('padding-left'))-16)),top:p.top+tp-tall-5}).bind('click',function(){ toggleHelp(this); });
		setTimeout(positionHelperLinks,500)
	}
	$('.fancybtndisable').live('click',function(e){
		e.preventDefault();
	});

});
