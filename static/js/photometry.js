// Web pages define x,y to start at the top left but FITS is bottom left. The input and output of y will be in FITS definition.
//photo = new Photometry({id:'photometric',src:"{{data.image}}",form:'entryform',width:width,source:{x:s_x,y:s_y,r:start_r},sky:{x:b_x,y:b_y,r:start_r,label:'Sky'},calibrator:{x:c_x[0],y:c_y[0],r:start_r},zoom:2,callback:photoReady,calibrators:calibrators});

// To do:
// 1) remove zoom on click.
// 2) make zoom apply to all elements (only one layer)
// 3) when zoomed the user can pan the image (using the rangelimiter?)
// 4) remove ability to resize the radius

function Photometry(inp){

	this.im = new Image();
	this.cur = {x:0,y:0};
	this.width;
	this.height;
	this.zoom = 2;
	this.src;
	this.holder = { id:'imageholder', img: 'imageholder_small', zoomed: 'imageholder_big', svg:'svgcanvas' };
	this.svg;
	this.calibrators;
	this.calibratorszoomed;
	this.source = {x:100,y:0,yfits:500,r:8,label:'Target',callback:''};
	this.sky = {x:100,y:0,yfits:550,r:this.source.r,label:'Sky',callback:''};
	this.calibrator = {x:[100,100,100],y:[0,0,0],yfits:[600,650,700],r:this.source.r,label:'Calibrator',callback:''};
	this.sizer = new Array();
	this.others = new Array();
	//this.suggested = new Array();
	//this.suggestedvisible = false;
	this.l = 0;
	this.t = 0;
	this.groupmove = false;

	// Overwrite defaults with variables passed to the function
	if(typeof inp=="object"){
		if(typeof inp.id=="string"){
			this.holder.id = inp.id;
			this.holder.img = inp.id+'_'+this.holder.img;
			this.holder.zoomed = inp.id+'_'+this.holder.zoomed;
			this.holder.svg = inp.id+'_'+this.holder.svg;
		}
		if(typeof inp.src=="string") this.src = inp.src;
		if(typeof inp.width=="number") this.width = inp.width;
		if(typeof inp.height=="number") this.height = inp.height;
		if(typeof inp.zoom=="number") this.zoom = inp.zoom;
		if(typeof inp.source=="object"){
			if(typeof inp.source.x=="number") this.source.x = inp.source.x;
			if(typeof inp.source.y=="number") this.source.yfits = inp.source.y;
			if(typeof inp.source.r=="number") this.calibrator.r = this.source.r = this.sky.r = inp.source.r;
			if(typeof inp.source.label=="string") this.source.label = inp.source.label;
		}
		if(typeof inp.sky=="object"){
			if(typeof inp.sky.x=="number") this.sky.x = inp.sky.x;
			if(typeof inp.sky.y=="number") this.sky.yfits = inp.sky.y;
			if(typeof inp.sky.r=="number") this.calibrator.r = this.source.r = this.sky.r = inp.sky.r;
			if(typeof inp.sky.label=="string") this.sky.label = inp.sky.label;
		}
		if(typeof inp.calibrator=="object"){
			if(typeof inp.calibrator.x=="object") this.calibrator.x = inp.calibrator.x;
			if(typeof inp.calibrator.y=="object") this.calibrator.yfits = inp.calibrator.y;
			if(typeof inp.calibrator.r=="number") this.calibrator.r = this.source.r = this.sky.r = inp.calibrator.r;
			if(typeof inp.calibrator.label=="string") this.calibrator.label = inp.calibrator.label;
		}
		if(typeof inp.calibrators=="object") this.others = inp.calibrators;
		//if(typeof inp.suggested=="object") this.suggested = inp.suggested;
		this.form = inp.form;
	}else{
		if(typeof inp=="string") this.src = inp;
	}
	if(typeof inp.callback=="function") this.callback = inp.callback;

	if(this.src){
		// Keep a copy of this so that we can reference it in the onload event
		var _object = this;
		// Define the onload event before setting the source otherwise Opera/IE might get confused
		this.im.onload = function(){ _object.loaded(); if(_object.callback) _object.callback.call(); }
		this.im.src = this.src

		if($('#'+this.holder.id).length==0) $('body').append('<div id="'+this.holder.id+'"></div>');
		if($('#'+this.holder.img).length==0) $('#'+this.holder.id).append('<div id="'+this.holder.img+'"><img src="'+this.src+'" alt="LCOGT image" /></div>');
		if($('#'+this.holder.zoomed).length==0) $('#'+this.holder.id).append('<div id="'+this.holder.zoomed+'" style="display:none;"><img src="'+this.src+'" alt="LCOGT image" /></div>');
		if($('#'+this.holder.svg).length==0) $('#'+this.holder.id).append('<div id="'+this.holder.svg+'"></div>');

		this.pos = $('#'+this.holder.id).position();
	}
}

// We've loaded the image so now we can proceed
Photometry.prototype.loaded = function(){
	// Apply width/height depending on what input we have
	if(!this.height && this.width) this.height = this.im.height*this.width/this.im.width;	// Only defined width so work out appropriate height
	if(!this.width && this.height) this.width = this.im.width*this.height/this.im.height;	// Only defined height so work out appropriate width
	if(!this.width) this.width = this.im.width;	// No width defined so get it from the image
	if(!this.height) this.height = this.im.height;	// No height defined so get it from the image

	$('#'+this.holder.id).css({'position':'relative','z-index':0,overflow:'hidden',width:this.width,'height':this.height});
	$('#'+this.holder.img).css({'position':'absolute','left':0,'top':0,'z-index':0});
	$('#'+this.holder.img+' img').css({width:this.width,'height':this.height});
	$('#'+this.holder.zoomed).css({'position':'absolute','left':'0px','top':'0px','z-index':1,display:'none'});
	$('#'+this.holder.zoomed+' img').css({width:this.width*this.zoom,'height':this.height*this.zoom});
	$('#'+this.holder.svg).css({'position':'absolute','left':'0px','top':'0px','width':this.width,'height':this.height,'z-index':2});

	this.svg = Raphael(this.holder.svg, this.width, this.height);
	this.scale = this.im.width/this.width;
	this.source.y = (this.im.height-this.source.yfits)
	this.calibrator.y = [(this.im.height-this.calibrator.yfits[0]),(this.im.height-this.calibrator.yfits[1]),(this.im.height-this.calibrator.yfits[2])]
	this.sky.y = (this.im.height-this.sky.yfits)
	this.colours = defaultColours();

	// Now draw all the other calibrator circles
	this.calibrators = this.svg.set();
	this.calibratorszoomed = this.svg.set();
	for(var i = 0; i < this.others.length ; i++){
		// When provided as input the y-axis values are all inverted
		o = { x: this.others[i].x/this.scale, y: (this.im.height-this.others[i].y)/this.scale, r : this.others[i].r/this.scale }
		style = {fill: this.colours.calibrator.bg,stroke: "none","stroke-width": 0,opacity: 0.3}
		this.calibrators.push(this.svg.circle(o.x, o.y, o.r).attr(style));
		this.calibratorszoomed.push(this.svg.circle(o.x*this.zoom, o.y*this.zoom, o.r*this.zoom).attr(style));
	}
	this.calibratorszoomed.hide()

/*
	// Now draw all the suggested calibrators
	this.suggestions = this.svg.set();
	this.suggestionszoomed = this.svg.set();
	for(var i = 0; i < this.suggested.length ; i++){
		// When provided as input the y-axis values are all inverted
		s = { x: this.suggested[i].x/this.scale, y: (this.im.height-this.suggested[i].y)/this.scale, r: this.suggested[i].r/this.scale }
		style = {"stroke": this.colours.calibrator.bg,"fill": "none","stroke-width": 2,opacity: 0.5}
		this.suggestions.push(this.svg.circle(s.x, s.y, s.r).attr(style));
		this.suggestions.push(this.svg.reticle(s.x,s.y,s.r*1.4,0.0).attr(style));
		this.suggestionszoomed.push(this.svg.circle(s.x*this.zoom, s.y*this.zoom, s.r*this.zoom).attr(style));
		this.suggestionszoomed.push(this.svg.reticle(s.x*this.zoom, s.y*this.zoom,s.r*1.4*this.zoom,0.0).attr(style));
	}
	if(!this.suggestedvisible){
		this.suggestions.hide();
		this.suggestionszoomed.hide();
	}
	*/

	this.sizer[0] = new Sizer(this,this.sky.x/this.scale,this.sky.y/this.scale,this.sky.r/this.scale,this.sky.label,$('#'+this.holder.zoomed),{colour:this.colours.sky.bg});
	this.sizer[1] = new Sizer(this,this.source.x/this.scale,this.source.y/this.scale,this.source.r/this.scale,this.source.label,$('#'+this.holder.zoomed),{colour:this.colours.source.bg,colourtext:this.colours.source.text});
	this.sizer[2] = new Sizer(this,this.calibrator.x[0]/this.scale,(this.calibrator.y[0])/this.scale,this.calibrator.r/this.scale,this.calibrator.label+' 1',$('#'+this.holder.zoomed),{colour:this.colours.calibrator.bg});
	this.sizer[3] = new Sizer(this,this.calibrator.x[1]/this.scale,(this.calibrator.y[1])/this.scale,this.calibrator.r/this.scale,this.calibrator.label+' 2',$('#'+this.holder.zoomed),{colour:this.colours.calibrator.bg});
	this.sizer[4] = new Sizer(this,this.calibrator.x[2]/this.scale,(this.calibrator.y[2])/this.scale,this.calibrator.r/this.scale,this.calibrator.label+' 3',$('#'+this.holder.zoomed),{colour:this.colours.calibrator.bg});
	this.sizer[4].isTwinOf([this.sizer[0],this.sizer[1],this.sizer[2],this.sizer[3]]);

}
Photometry.prototype.getView = function(){
	this.zoom = this.sizer[0].z

	if(this.zoom==1) return[0,0,1,1];
	else{
		el = $('#'+this.holder.zoomed);
		var p = el.position();
		var fw = el.outerWidth();
		var fh = el.outerHeight();
		var l = (-parseInt(p.left))/fw;
		var t = (-parseInt(p.top))/fh;
		var w = this.width/fw;
		var h = this.height/fh;
		return [l,t,w,h]
	}
}

Photometry.prototype.getX = function(key){
	var offset = parseInt(key) ? parseInt(key)-1 : 0;
	if(key == "sky")  return (this.sizer[0].x*this.scale);
	else if(key == "source") return (this.sizer[1].x*this.scale);
	else if(key.indexOf("calibrator")==0){
		offset = (key.length > 10) ? parseInt(key.substr(10))-1 : 0;
		return (this.sizer[2+offset].x*this.scale);
	}else return 0;
}
Photometry.prototype.getY = function(key,rev){
	var y = 0;
	if(key == "sky")  y = this.sizer[0].y;
	else if(key == "source") y = this.sizer[1].y;
	else if(key.indexOf("calibrator")==0){
		offset = (key.length > 10) ? parseInt(key.substr(10))-1 : 0;
		y = this.sizer[2+offset].y;
	}
	if(!rev) return this.im.height-y*this.scale;
	else return y*this.scale;
}
Photometry.prototype.getR = function(key){
	var offset = parseInt(key) ? parseInt(key)-1 : 0;
	if(key == "sky")  return (this.sizer[0].r*this.scale);
	else if(key == "source") return (this.sizer[1].r*this.scale);
	else if(key.indexOf("calibrator")==0){
		offset = (key.length > 10) ? parseInt(key.substr(10))-1 : 0;
		return (this.sizer[2+offset].r*this.scale);
	}else return 0;
}
Photometry.prototype.getXs = function(){
	var o = "";
	for(var i = 0; i < this.sizer.length ; i++){
		if(i > 0) o += ",";
		o += (this.sizer[i].x*this.scale);
	}
	return o;
}
Photometry.prototype.getYs = function(rev){
	var o = "";
	for(var i = 0; i < this.sizer.length ; i++){
		if(i > 0) o += ",";
		o += (!rev) ? (this.im.height-this.sizer[i].y*this.scale) : this.sizer[i].y*this.scale;
	}
	return o;
}
Photometry.prototype.getRs = function(key){
	var o = "";
	for(var i = 0; i < this.sizer.length ; i++){
		if(i > 0) o += ",";
		o += (this.sizer[i].r*this.scale);
	}
	return o;
}
Photometry.prototype.addCalibrator = function(x,y,fromfits){
	var i = this.sizer.length;
	if(i < 2) return;	// We should have at least 2 Sizer elements: 1 for sky and 1 for source 

	// Need to flip in the y-direction because of the FITS file input
	if(fromfits) y = (this.im.height-y);
	var x = (typeof x=="number") ? x/this.scale : (this.width/2);
	var y = (typeof y=="number") ? y/this.scale : (this.height/2);
	this.sizer[i] = new Sizer(this,x,y,this.sizer[i-1].r,this.calibrator.label+" "+(i-1),$('#'+this.holder.zoomed),{colour:this.colours.calibrator.bg});
	this.sizer[i].cloneEvents(this.sizer[i-1]);
	this.sizer[i].isTwinOf(this.sizer);
	var cal = i-1;
	// Do the form fields already exist? If they do, don't add them again!
	if($('#id_cal'+cal+'radius').length == 0){
		var html = '<div class="fieldWrapper"><label for="id_cal'+cal+'radius">Aperture Radius (calibrator '+cal+')</label><input type="text" name="cal'+cal+'radius" id="id_cal'+cal+'radius" /></div>';
		html += '<div class="fieldWrapper"><label for="id_cal'+cal+'xpos">Calibrator '+cal+' x position</label><input type="text" name="cal'+cal+'xpos" id="id_cal'+cal+'xpos" /></div>';
		html += '<div class="fieldWrapper"><label for="id_cal'+cal+'ypos">Calibrator '+cal+' y position</label><input type="text" name="cal'+cal+'ypos" id="id_cal'+cal+'ypos" /></div>';
		html += '<div class="fieldWrapper"><label for="id_cal'+cal+'counts">Calibrator '+cal+' counts</label><input type="text" name="cal'+cal+'counts" id="id_cal'+cal+'counts" /></div>';
		$('#'+this.form).append(html);
	}
	$('#calibrators').val(cal)
}
Photometry.prototype.removeCalibrator = function(x,y){
	if(this.sizer.length > 5){
		this.sizer[this.sizer.length-1].remove()
		this.sizer.pop();
		var n = $('#'+this.form+' .fieldWrapper').length;
		$('#'+this.form+' .fieldWrapper:gt('+(n-5)+')').remove()
	}
}
/*
Photometry.prototype.toggleSuggestions = function(){
	this.suggestedvisible = !this.suggestedvisible;
	if(this.suggestedvisible) this.suggestions.show();
	else this.suggestions.hide();
	this.suggestionszoomed.hide();
}*/
Photometry.prototype.onmove = function(){

	if(this.sizer[0].z > 1){
		p = $('#'+this.holder.zoomed).position();
		this.l = p.left;
		this.t = p.top;
//		this.calibratorszoomed.translate(10,10);
//		console.log('onmove',this.calibratorszoomed)
	}
}
Photometry.prototype.onzoom = function(){
	// Check the zoom level

	if(this.sizer[0].z==1){
		// We need to move the zoomed calibrators back
		this.calibratorszoomed.hide();
		this.calibratorszoomed.translate(-this.l,-this.t);
		this.calibrators.show();
/*
		this.suggestionszoomed.translate(-this.l,-this.t)
		if(this.suggestedvisible){
			this.suggestionszoomed.hide();
			this.suggestions.show();
		}else{
			this.suggestionszoomed.hide();
			this.suggestions.hide();
		}
		*/
	}else{
		p = $('#'+this.holder.zoomed).position();
		this.l = p.left;
		this.t = p.top;
		this.calibratorszoomed.translate(this.l,this.t);
		this.calibratorszoomed.show();
		this.calibrators.hide();
		/*
		this.suggestionszoomed.translate(this.l,this.t)
		if(this.suggestedvisible){
			this.suggestionszoomed.show();
			this.suggestions.hide();
		}else{
			this.suggestionszoomed.hide();
			this.suggestions.hide();
		}*/
	}
}
Photometry.prototype.bind = function(e,type,fn){
	if(typeof e!="string" || typeof fn!="function") return this;
	var min = max = 0;

	if(type=="onzoom"){
		var _obj = this;
		var _fn = fn;
		fn = function(args){ _fn.call(this,args); _obj.onzoom(); }
	}
	if(type=="onmove"){
		var _obj = this;
		var _fn = fn;
		fn = function(args){ _fn.call(this,args); _obj.onmove(); }
	}

	if(e == "sky"){ min = 0; max = 0; }
	else if(e == "source"){ min = 1; max = 1; }
	else if(e == "calibrator"){ min = 2; max = this.sizer.length-1; }

	for(i = min; i <= max ; i++) this.sizer[i].bind(type,fn);
	return this;
}
