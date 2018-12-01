// An Indicator shows source, sky and calibrator circles overlaid on a thumbnail
function Indicator(inp){

	this.im = new Image();
	this.width;
	this.height;
	this.src;
	this.holder = { id:'imageholder', img: 'imageholder_small', svg:'svgcanvas' };
	this.svg;
	this.sources;
	this.inp = inp;	// Web pages define x,y to start at the top left but FITS is bottom left. The input and output of y will be in FITS definition.
	this.opacity = {on:0.6,off:0.001}

	// Overwrite defaults with variables passed to the function
	if(typeof inp!="object") return;
	if(typeof inp.id=="string"){
		this.holder.id = inp.id;
		this.holder.img = inp.id+'_'+this.holder.img;
		this.holder.svg = inp.id+'_'+this.holder.svg;
	}
	if($('#'+this.holder.id).length==0) return;

	this.src = (typeof inp.src=="string") ? inp.src : $('#'+this.holder.id+' img').attr('src');
	this.width = (typeof inp.width=="number") ? inp.width : $('#'+this.holder.id).outerWidth();
	this.height = (typeof inp.height=="number") ? inp.height : $('#'+this.holder.id).outerHeight();
	this.form = inp.form;

	if(typeof inp.callback=="function") this.callback = inp.callback;

	if(this.src){
		// Keep a copy of this so that we can reference it in the onload event
		var _object = this;
		// Define the onload event before setting the source otherwise Opera/IE might get confused
		this.im.onload = function(){ _object.loaded(); if(_object.callback) _object.callback.call(); }
		this.im.src = this.src

		if($('#'+this.holder.svg).length==0) $('#'+this.holder.id).append('<div id="'+this.holder.svg+'"></div>');

		this.pos = $('#'+this.holder.id).position();
	} else {
    console.log("Failed")
  }
}


// We've loaded the image so now we can proceed
Indicator.prototype.loaded = function(){
	// Apply width/height depending on what input we have
	if(!this.height && this.width) this.height = this.im.height*this.width/this.im.width;	// Only defined width so work out appropriate height
	if(!this.width && this.height) this.width = this.im.width*this.height/this.im.height;	// Only defined height so work out appropriate width
	if(!this.width) this.width = this.im.width;	// No width defined so get it from the image
	if(!this.height) this.height = this.im.height;	// No height defined so get it from the image

	$('#'+this.holder.id).css({'position':'relative','z-index':0,overflow:'hidden',width:this.width,'height':this.height});
	$('#'+this.holder.svg).css({'position':'absolute','left':'0px','top':'0px','width':this.width,'height':this.height,'z-index':2});

	this.svg = Raphael(this.holder.svg, this.width, this.height);

	// Now draw all the other calibrator circles
	this.sources = this.svg.set();

	c = defaultColours();

	// When provided as input the y-axis values are all inverted
	for(var o = 0; o < this.inp.circles.length ; o++){
		if(this.inp.circles[o].type=="source") fill = c.source.bg
		else if(this.inp.circles[o].type=="sky") fill = c.sky.bg
		else if(this.inp.circles[o].type=="calibrator") fill = c.calibrator.bg
		this.sources.push(this.svg.circle(this.inp.circles[o].x*this.width, (this.height-(this.inp.circles[o].y)*this.height), this.inp.circles[o].r*this.width).attr({fill: fill,stroke: "none","stroke-width": 0,opacity: (this.inp.circles[o].used==true ? this.opacity.on : this.opacity.off)}));
	}
}

Indicator.prototype.hide = function(i){ if(typeof i=="number") this.sources[i].attr('opacity',this.opacity.off); }
Indicator.prototype.show = function(i){ if(typeof i=="number") this.sources[i].attr('opacity',this.opacity.on); }
