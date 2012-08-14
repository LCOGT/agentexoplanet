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
