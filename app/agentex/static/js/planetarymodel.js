function PlanetaryModel(inp){
	this.svg;
	this.svg2;

	// Constants
	this.au = 1.496e11;
	this.G = 6.67e-11;
	this.wide = $('#mainplotholder').outerWidth();
	this.tall = Math.round((this.wide/3)/16)*16;

	this.mass = (inp && typeof inp.mass==="number") ? inp.mass : 1;	// in solar masses
	this.period = (inp && typeof inp.period==="number") ? inp.period : 1;	// in days
	this.name = (inp && typeof inp.name==="string") ? inp.name : "";

	// Scaling
	this.metres2px = 0;
	this.au_px = 0;

	// Define some planetary system objects
	this.sun = { radius: 1392000000, mass: 1.9891e30, svg:'', x:0,y:0 };
	this.jupiter = { radius: 71492000, mass: 1.8986e27, svg:'', x:0,y:0 };
	this.star = { radius: 0, mass: this.mass*1.9891e30, svg:'', x:0,y:0 };
	this.planet = { radius: 0, a: 0, period: this.period*86400, svg:'', x:0,y:0 };
	this.marker = { a: 0.01*this.au, svg:'' };
	this.label = { a: 0.01*this.au, svg:'' };

	this.orbiting = false;
	this.disabled = false;

	this.init(inp);

	return this;
}
PlanetaryModel.prototype.init = function(ranges){
	this.t_trans = ranges.transit;	// Transit length in seconds
	this.dip = ranges.dip;	// Depth of dip

	if(this.dip > 0){
		$('#relativesizes').show();
		this.planet.a = Math.pow(((this.planet.period*this.planet.period*this.star.mass*this.G)/(4*Math.PI*Math.PI)),1/3);

		this.defineMarker(this.planet.a);

		this.metres2px = (this.wide*0.45)/this.planet.a;
		this.au_px = this.au*this.metres2px;

		this.star.radius = this.planet.a*(this.t_trans*Math.PI)/this.planet.period;
		this.planet.radius = Math.sqrt(this.dip)*this.star.radius;

		this.star.x = this.wide/2;
		this.star.y = this.tall/2;
		this.planet.y = this.star.y;

		this.r_p_scaled = (this.planet.radius/this.star.radius)*(this.t_trans*this.planet.a*Math.PI/this.planet.period);

		// Set things up for the animation
		this.time = { timer: 0, ID: "", total: 160, path: [] };
		var r = (this.planet.a*this.metres2px);
		for(var i = 0; i < this.time.total ; i++) this.time.path.push(this.star.x + r*Math.sin(2*Math.PI*i/this.time.total - Math.PI/2));


		if(typeof this.svg=="undefined"){
			this.svg = Raphael("planetillustration", this.wide, this.tall);
			this.line = this.svg.path("M0 "+this.star.y+"L"+this.wide+" "+this.star.y).attr({stroke:'#000000',"stroke-width": 1,"stroke-dasharray":["--"],"stroke-opacity": 0.7});
			this.marker.svg = this.svg.path("M"+(this.star.x+this.marker.a*this.metres2px)+" "+(this.star.y-5)+"L"+(this.star.x+this.marker.a*this.metres2px)+" "+(this.star.y+5)).attr({stroke:'#000000',"stroke-width": 1,"stroke-opacity": 0.7});
			this.label.svg = this.svg.text((this.star.x+this.label.a*this.metres2px),(this.star.y+15),(this.label.a/this.au).toFixed(2)+' AU');
			this.star.svg = this.svg.circle(this.star.x,this.star.y,this.star.radius*this.metres2px).attr({fill: 'r#ffdd00-#ddbb00',stroke: '#bb9900',"stroke-width": 2,"stroke-dasharray":["--"],"fill-opacity": 0.95});
			this.planet.svg = this.svg.circle(this.star.x-this.planet.a*this.metres2px,this.planet.y,this.planet.radius*this.metres2px).attr({fill: '#444444',stroke:'#000000',"stroke-width": 2,"stroke-dasharray":["-"],"fill-opacity": 0.95});
			this.start();

		}else{
			if(!this.orbiting){
				this.star.svg.attr({cx:this.star.x,cy:this.star.y});
				this.planet.svg.attr({cx:this.star.x-(this.planet.a*this.metres2px),cy:this.planet.y});
				this.start();
			}
			this.star.svg.animate({r: (this.star.radius*this.metres2px)},500);
			this.planet.svg.animate({r: (this.planet.radius*this.metres2px)},500);
			this.marker.svg.animate({x: this.star.x+(this.marker.a*this.metres2px)},500);
			this.label.svg.animate({x: this.star.x+(this.label.a*this.metres2px)},500);
		}

    $('#transit_duration').html((this.t_trans/86400).toFixed(3));
    $('#brightness_dip').html((this.dip).toFixed(3));
    $('#ratio_radius').html((this.planet.radius/this.star.radius).toFixed(2));
    $('#planet_r_km').html(Math.round(this.planet.radius/100000)*100);
    $('#planet_r_jup').html((this.planet.radius/this.jupiter.radius).toFixed(2));
		$('.transitperiod').html((this.period).toFixed(3)+" days");
		$('.transitlength').html((this.t_trans/3600).toFixed(3)+" hours");
		$('.transitdip').html((this.dip*100).toFixed(2)+"%");
		$('.transitscale').html((this.planet.radius/this.star.radius).toFixed(2));
		$('.transitorbit').html((Math.round(this.planet.a/1000000)*1000)+" km");
		$('.transitorbitau').html((this.planet.a/this.au).toFixed(3)+" AU");
		$('.transitplanetradius').html((Math.round(this.planet.radius/100000)*100)+" km");

		//get the top offset of the target anchor
		var target_offset = $("#relativesizes").offset();
		var target_top = target_offset.top;

		// Correct animation to only go as far as necessary so we don't
		// try to go beyond the bottom of the page
		tall_win = $(window).height();
		tall_doc = $(document).height();
		t = target_top;
		if(tall_doc-target_top < tall_win) t = tall_doc - tall_win;

		$('#nextstep').removeClass('fancybtndisable');

	}else this.stop();
}
PlanetaryModel.prototype.defineMarker = function(a){
	a = this.au*Math.floor(100*a/this.au)/100;
	this.marker.a = a;
	this.label.a = a;
}
PlanetaryModel.prototype.start = function(){
	this.orbiting = true;
	var _obj = this;
	this.time.ID = setInterval(function(){ _obj.orbit(); },50);
}
PlanetaryModel.prototype.stop = function(){
	this.orbiting = false;
}
PlanetaryModel.prototype.toggleOrbit = function(){
	this.orbiting = !this.orbiting;
}
PlanetaryModel.prototype.disable = function(){
	this.disabled = true;
	var _obj = this;
	if(this.disableID) clearTimeout(this.disableID);
	this.disableID = setTimeout(function(){ _obj.disabled = false; },2000);
}
PlanetaryModel.prototype.orbit = function() {
	if(this.orbiting && !this.disabled){
		this.time.timer++;
		if(this.time.timer >= this.time.total){
			this.orbiting = false;
			clearInterval(this.time.ID);
			var _obj = this;
			setTimeout(function(){ _obj.start(); },5000);
			this.time.timer = 0;
		}
		this.planet.svg.attr({cx: this.time.path[this.time.timer]});
		if(this.time.timer == this.time.total/2) this.planet.svg.toBack();
		if(this.time.timer == 0) this.planet.svg.toFront();
	}
}
