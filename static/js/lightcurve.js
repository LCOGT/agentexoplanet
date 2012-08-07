function Lightcurve(inp){
	this.data = [];
	this.dataplot = [];
	this.dmean = [];
	this.dstd = [];
	this.dlow = [];
	this.dlow2 = [];
	this.dhigh = [];
	this.dhigh2 = [];
	this.dcal = [];
	this.fullcal = [];
	this.dsource = [];
	this.dmine = [];
	this.ids = [];
	this.dataset2 = [];
	this.used = [];
	this.mypoints = false;
	this.datahighest;
	this.options = {
		series: {
			lines: { show: false },
			points: { show: true },
			shadowSize: 0
		},
		xaxis:{
			mode:"time",
			timeformat:"%H:%M",
			minTickSize: [1, "hour"],
			axisLabel:'Time of Observation (Universal Time)',
			axisLabelUseCanvas: true
		},
		yaxis: {
			axisLabel: 'Relative Brightness',
			axisLabelUseCanvas: true
		},
		grid: { hoverable: true, clickable: true }
	};
	// Custom variables
	this.authenticated = (typeof inp.authenticated=="boolean") ? inp.authenticated : false;
	this.id = (typeof inp.id=="string") ? inp.id : "#mainplot";
	this.type = (typeof inp.type=="string") ? inp.type : "calibrators";
	this.framenum = (typeof inp.framenum=="number") ? inp.framenum : 0;
	this.period = (typeof inp.period=="number") ? inp.period : 0;
	this.msg = {nodata: ((typeof inp.msg.nodata=="string") ? inp.msg.nodata : "<p>You have no data points yet</p>"), login: ((typeof inp.msg.login=="string") ? inp.msg.login : "Please login to edit") };
	this.url = (inp.url) ? {edit: ((typeof inp.url.edit=="string") ? inp.url.edit : ""), json: ((typeof inp.url.json=="string") ? inp.url.json : ""), xhr: ((typeof inp.url.xhr=="string") ? inp.url.xhr : "") } : { edit:'',json:'',xhr:'' };
	this.data = (typeof inp.data=="object") ? inp.data : "";
	this.cal = (typeof inp.cal=="object") ? inp.cal : { order: 0, name: "" };
	this.mainplot = $(this.id);
	this.options = (typeof inp.options=="object") ? inp.options : {};
	
	// Set defaults for graph options
	if(!this.options.series) this.options.series = {};
	if(!this.options.series.lines) this.options.series.lines = { show : false };
	if(!this.options.series.points) this.options.series.points = { show : true };
	if(!this.options.series.shadowSize) this.options.series.shadowSize = 0;
	if(!this.options.xaxis) this.options.xaxis = {};
	if(!this.options.xaxis.mode) this.options.xaxis.mode = "time";
	if(!this.options.xaxis.timeformat) this.options.xaxis.timeformat = "%H:%M";
	if(!this.options.xaxis.minTickSize) this.options.xaxis.minTickSize = [1, "hour"];
	if(!this.options.xaxis.axisLabel) this.options.xaxis.axisLabel = 'Time of Observation (Universal Time)';
	if(!this.options.xaxis.axisLabelUseCanvas) this.options.xaxis.axisLabelUseCanvas = true;
	if(!this.options.yaxis) this.options.yaxis = {};
	if(!this.options.yaxis.axisLabel) this.options.yaxis.axisLabel = 'Relative Brightness';
	if(!this.options.yaxis.axisLabelUseCanvas) this.options.yaxis.axisLabelUseCanvas = true;
	if(!this.options.grid) this.options.grid = {};
	if(!this.options.grid.hoverable) this.options.grid.hoverable = true;
	if(!this.options.grid.clickable) this.options.grid.clickable = true;
	
	this.init();

	if(this.type == "old"){	
		$("a.mypoints").click(function(){
			if (mypoints == false){
				$.plot(mainplot,[
				{ data: dmine, points :{show:true}, color: "rgb(255,50,50)",clickable: true,hoverable:true },
						{ data: dmean, points :{show:true}, color: "rgb(51,153,255)",clickable: false,hoverable:false }], options);
				mypoints = true;
				$(".showmypoints").css('display', 'block');
				$(".hidemypoints").css('display', 'none');
				$('a#restrictdata').removeClass('fancybtndisable').show();
				limit.show();
			}else if (mypoints == true){
				$.plot(mainplot,[{ data: dmine, points :{show:true}, color: "rgb(255,50,50)" }], options);
				mypoints = false;
				$(".showmypoints").css('display', 'none');
				$(".hidemypoints").css('display', 'block');
				$('a#restrictdata').addClass('fancybtndisable').hide();
				limit.hide();
			}
		});
		this.mainplot.bind("plotclick", {me:this}, function (event, pos, item) {
			if (item) {
				if (item.seriesIndex == 0) window.location = event.data.me.url.edit+event.data.me.dmine[item.dataIndex][2];
				else $("#clickdata").html("Thats the average data point. You can't edit it");
			}
		}).bind("plothover", {me:this}, function (event, pos, item) {
			if(item){
				if (item.seriesIndex == 0){
					url = event.data.me.url.edit+event.data.me.dmine[item.dataIndex][2]
					if(event.data.me.authenticated) bubblePopup({id:'editmsg',el:{x:item.pageX,y:item.pageY,w:5,h:5},w:80,html:"<a href='"+url+"'>Edit " + unixtohours(item.datapoint[0]) + "<\/a>",'padding':2})
					else bubblePopup({id:'editmsg',el:{x:item.pageX,y:item.pageY,w:5,h:5},w:80,html:event.data.me.msg.login,'padding':2})
					$('#editmsg').bind('click',function(){ $(this).hide(); })
				}else{
					$("#clickdata").html("Thats the average data point. You can't edit it");
				}
			}
		});
	
		$("a#restrictdata").bind('click',{me:this},function(){ event.data.me.calibrate_data(); });
	}else if(this.type=="calibrators" || this.type=="super"){
		this.mainplot.bind("plotclick", {me:this}, function (event, pos, item) {
			if (item) {
				window.location = event.data.me.url.edit+event.data.me.ids[item.dataIndex];
			}
		}).bind("plothover", {me:this}, function (event, pos, item) {
			if(item){
				url = event.data.me.url.edit+event.data.me.ids[item.dataIndex]
				if(event.data.me.authenticated) bubblePopup({id:'editmsg',el:{x:item.pageX,y:item.pageY,w:5,h:5},w:90,html:"<a href='"+url+"'>Edit " + unixtohours(item.datapoint[0]) + "<\/a>",'padding':2})
				else bubblePopup({id:'editmsg',el:{x:item.pageX,y:item.pageY,w:5,h:5},w:80,html:event.data.me.msg.login,'padding':2})
				$('#editmsg').bind('click',function(){ $(this).hide(); })
			}
		});
	}else if(this.type=="average"){
/*
		this.mainplot.bind("plotclick", {me:this}, function (event, pos, item) {
			if(item) {
				window.location = event.data.me.url.edit+event.data.me.data.id[item.dataIndex];
			}
		}).bind("plothover", {me:this}, function (event, pos, item) {
			if(item){
				url = event.data.me.url.edit+event.data.me.data[item.dataIndex].id
				if(event.data.me.authenticated) bubblePopup({id:'editmsg',el:{x:item.pageX,y:item.pageY,w:5,h:5},w:90,html:"<a href='"+url+"'>Edit " + unixtohours(item.datapoint[0]) + "<\/a>",'padding':2})
				else bubblePopup({id:'editmsg',el:{x:item.pageX,y:item.pageY,w:5,h:5},w:80,html:event.data.me.msg.login,'padding':2})
				$('#editmsg').bind('click',function(){ $(this).hide(); })
			}
		});
*/
	}	
}

Lightcurve.prototype.init = function(){

	if($('a#restrictdata').length > 0) $('a#restrictdata').addClass('fancybtndisable').hide();
	
	var _obj = this;

	if(typeof this.data=="object"){
//console.log('Using existing data ',this.data)
		this.data2plot();
		this.update();
	}else{
		$.getJSON(this.url.xhr,function(data){
//console.log('It is AJAXing ',data)
			_obj.data = data;
			_obj.data2plot();
			_obj.update();
		});
	}	
}
Lightcurve.prototype.data2plot = function(){
	d = this.data;
	if(this.type=="calibrators"){
		if(typeof this.data.source=="undefined"){
			if(d.length == 0) bubblePopup({id:'editmsg',el:$(this.id),w:200,align:'center',html:this.msg.nodata,'padding':2})
			else{
				cals = d[0].data.calibrator;
				var tempdata = new Array(cals.length);
				var temptimes = [];
				this.ids = [];
				if(this.used.length == 0){
					this.used = new Array(cals.length);
					for(var c=0 ; c < cals.length ; c++) this.used[c] = true;
				}

				for(var c=0 ; c < cals.length ; c++){
					tempdata[c] = [];
					for(var i=0 ; i < d.length ; i++){

						numerator = d[i].data.source[0]-d[i].data.background[0];
						cal = d[i].data.calibrator[c];
						denominator = cal-d[i].data.background[0];
						if(typeof cal=="number"){
							if(c == 0){
								this.ids.push(d[i].id);
								temptimes.push(Number(d[i].datestamp)*1000)
							}
							tempdata[c].push(numerator/denominator);
						}
					}
				}
				this.dataplot = new Array(cals.length);
				for(var c=0 ; c < cals.length ; c++){
					this.dataplot[c] = [];
					norm = 1;
					var points = tempdata[c].length;
					if(points > 6) norm = (tempdata[c][0]+tempdata[c][1]+tempdata[c][2]+tempdata[c][points-3]+tempdata[c][points-2]+tempdata[c][points-1])/6;
					else norm = max(tempdata[c]);
					for(var i=0 ; i < points ; i++) this.dataplot[c].push([temptimes[i], tempdata[c][i]/norm,this.ids[i]]);
				}
				tempdata = "";
				tempids = "";
				temptimes = "";
			}
		}else{
			this.dataplot = new Array(d.calibration.length);
			if(this.used.length == 0){
				this.used = new Array(d.calibration.length);
				for(var c=0 ; c < d.calibration.length ; c++) this.used[c] = true;			
			}
			if(d.source.length == 0) bubblePopup({id:'editmsg',el:$(this.id),w:200,align:'center',html:this.msg.nodata,'padding':2})
			for(var c=0 ; c < d.calibration.length ; c++){
				this.dataplot[c] = [];
				for(var i=0 ; i < d.calibration[c].length ; i++){
					if(c == 0) this.ids.push(d.id[i]);
					n = Number(d.calibration[c][i]);
					if(n > 0) this.dataplot[c].push([Number(d.datestamps[i])*1000, Number(d.calibration[c][i]),d.id[i]]);
					else this.dataplot[c].push([Number(d.datestamps[i])*1000, null,d.id[i]]);
				}
			}
		}
	}else if(this.type=="super"){
		if(typeof d.dates=="undefined"){
			// Data in page
			this.dmean = new Array(d.length);
			this.dm = new Array(d.length);
			this.dstd = new Array(d.length);
			for(i=0;i<d.length;i++){
				this.dmean[i] = ([Number(d[i].datestamp)*1000,Number(d[i].data.mean)]);
				this.dm[i] = {x:Number(d[i].datestamp)*1000,y:Number(d[i].data.mean),err:Number(d[i].data.std)};
				this.dstd[i] = (Number(d[i].data.std));
				//this.ids.push(val.id);
			}
		}else{
			// Data via request

			this.dmean = new Array(d.dates.length);
			this.dm = new Array(d.dates.length);
			this.dstd = new Array(d.dates.length);
			for(i=0;i<d.dates.length;i++){
				this.dmean[i] = ([Number(d.dates[i])*1000,Number(d.normalised[i])]);
				this.dm[i] = {x:Number(d.dates[i])*1000,y:Number(d.normalised[i])};
				this.dstd[i] = (Number(d.std[i]));
				//this.ids.push(val.id);
			}
		}
	}else if(this.type=="average"){

		if(typeof d=="undefined"){
		
		}else if(typeof d[0].date=="undefined"){
			this.dataplot = new Array(d.calibration.length);
			this.ys = new Array(d.calibration.length);
			if(d.source.length == 0) bubblePopup({id:'editmsg',el:$(this.id),w:200,align:'center',html:this.msg.nodata,'padding':2})
			for(var c=0, j=0 ; c < d.calibration.length ; c++){
				this.ids.push(d.id[c]);
				this.dataplot[c] = [];
				this.used.push(true)
				for(var i=0 ; i < d.calibration[c].length ; i++){
					n = Number(d.calibration[c][i]);
					if(n > 0){
						this.dataplot[c].push([Number(d.datestamps[i])*1000, n,d.id[i]]);
						this.ys[c].push(n);
					}else this.dataplot[c].push([Number(d.datestamps[i])*1000, null,d.id[i]]);
				}
			}
		}else{
			if(d.length == 0) bubblePopup({id:'editmsg',el:$(this.id),w:200,align:'center',html:this.msg.nodata,'padding':2})
			else{
				cal = d[0].data.calibration;
				this.dataplot = new Array(cal.length);
				this.ys = new Array(cal.length);
				for(var c=0 ; c < cal.length ; c++){
					this.dataplot[c] = new Array(d.length);
					this.ys[c] = new Array(d.length);
					this.used.push(true);
					for(var i=0 ; i < d.length ; i++){
						n = Number(d[i].data.calibration[c]);
						if(n > 0){
							this.dataplot[c][i] = ([Number(d[i].datestamp)*1000, n,d[i].id]);
							this.ys[c][i] = n;
						}else this.dataplot[c][i] = ([Number(d[i].datestamp)*1000, null,d[i].id]);
					}
				}
			}
		}
	}
}

// Return the model values
// This model assumes a linear first order limb darkening and 
// uses the method defined in Addison, Durrance & Schwieterman 
// http://adsabs.harvard.edu/abs/2010JSARA...3...45A
Lightcurve.prototype.model = function(p, t) {

	t = optimize.vector.atleast_1d(t);
	p = optimize.vector.atleast_1d(p);

	var a = p[0];	// in units of rstar
	var rstar = 1;
	var rplanet = p[1];	// in units of rstar
	var tzero = p[2];
	var period = 1;
	var inc = 0.0;
	
	// The fractional drop in intensity caused by the planet
	var Fb;
	var px = 8;
	var i, j, dpix, x, theta, xpos, ypos, result = [], v, n;
	var mu = 0.684;

	ypos = a * Math.sin(inc);

	var pxstar = (4/3)*Math.PI*Math.pow(px*rstar/rplanet,2);

	for (x = 0; x < t.length; x++) {

		theta = (t[x]-tzero)/(period);

		xpos = a * Math.sin(2*Math.PI*theta);

		Fb = 0;
		n = 0;
		for(i = -px; i <= px ; i++){
			for(j = -px; j <= px ; j++){
				dpix = Math.sqrt( Math.pow((xpos + rplanet*i/px),2) + Math.pow((ypos + rplanet*j/px),2));
				
				if(dpix < rstar){

					v = (1 - mu*(1 - Math.sqrt(1 - Math.pow((dpix/rstar),2))))
					Fb += v;
					n++;
				}
			}
		}

		// Scale by star pixels
		result.push(1 - Fb/pxstar);
	}

	return result;

};

// Fit the model to the data
Lightcurve.prototype.fit = function(d) {

	var i, p1, outx, out, n = 200;
	var data = [];
	var outx = [];
	// '#d62728','#1e77b4','#edc240'
	var out = { id: 'model', data: [], points: { show: false }, lines: { show: true, width: 3 }, color: "rgb(51,153,255)",clickable: false,hoverable:false};
	var _obj = this;
	var xs = [], ys = [], es = [];

	//var range = d[d.length-1].x-d[0].x;
	var range = this.graph.x.max - this.graph.x.min;

	for(i = 0; i < d.length; i++) xs.push((d[i].x-d[0].x)/this.period);
	for(i = 0; i < d.length; i++) ys.push(d[i].y);
	for(i = 0; i < d.length; i++) es.push(d[i].err);
	for(i = 0; i < n; i++) outx.push((i/(n-1))*(d[d.length-1].x-d[0].x)/this.period);

	// orbital radius, star radius, planet radius
	p0 = [6.966,0.1,(d[Math.floor(d.length/2)].x-d[0].x)/this.period];

	p1 = optimize.newton(function(p){
		var i, chi = [];
		var model = _obj.model(p, xs);
		for (i = 0; i < xs.length; i++) {
			chi.push((ys[i] - model[i]) / es[i]);
		}
		return chi;
	}, p0);

	var model = this.model(p1,outx);

	var mn = 1;
	for(i = 0; i < n; i++){
		out.data.push({x:(outx[i]*this.period)+d[0].x, y: model[i],points:{show:true} });
		if(model[i] < mn) mn = model[i];
	}

	this.graph.addSeries(out);
	
	this.fitted = { xaxis: { from: this.graph.x.min, to: this.graph.x.min+(this.period)/(Math.PI*p1[0]) }, yaxis: { from: mn, to: 1 }};

	return this;
};

Lightcurve.prototype.update = function(){
	var line = 0;
	var x,y,t;

	if(this.type=="super"){

	    this.dlow = new Array(this.dmean.length);
	    this.dlow2 = new Array(this.dmean.length);
	    this.dhigh = new Array(this.dmean.length);
	    this.dhigh2 = new Array(this.dmean.length);
	    this.dl = this.dh = this.dm[0].y;
		for(var i = 0; i < this.dm.length ; i++){
		    this.dlow[i] = [this.dmean[i][0],(this.dmean[i][1] - this.dstd[i]) ];
			this.dlow2[i] = [this.dmean[i][0],(this.dmean[i][1] - 2*this.dstd[i])];
			this.dhigh[i] = [this.dmean[i][0],(this.dmean[i][1] + this.dstd[i])];
			this.dhigh2[i] = [this.dmean[i][0],(this.dmean[i][1] + 2*this.dstd[i])];

			y = (this.dm[i].y - 1.4*this.dstd[i]);
			if(y < this.dl) this.dl = y;
			y = (this.dm[i].y + 1.4*this.dstd[i]);
			if(y > this.dh) this.dh = y;
			
		}
		var dataset2 = [
			{ id: 'low2', data: this.dlow2, lines: { show: true, lineWidth: 0, fill: false }, color: "rgb(51,153,255)",clickable: false,hoverable:false},
			{ id: 'low', data: this.dlow, lines: { show: true, lineWidth: 0, fill: 0.1 }, color: "rgb(51,153,255)", fillBetween: 'low2',clickable: false,hoverable:false },
			{ id: 'mean', data: this.dmean, lines: { show: true, lineWidth: 2.5, fill: 0.2, shadowSize: 0 }, color: "rgb(51,153,255)", fillBetween: 'low',clickable: false,hoverable:false },
			{ id: 'high', data: this.dhigh, lines: { show: true, lineWidth: 0, fill: 0.2 }, color: "rgb(51,153,255)", fillBetween: 'mean',clickable: false,hoverable:false },
			{ id: 'high2', data: this.dhigh2, lines: { show: true, lineWidth: 0, fill: 0.1 }, color: "rgb(51,153,255)", fillBetween: 'high',clickable: false,hoverable:false },
		];
		var dataset3 = [
			{ id: 'mean', data: this.dm, points: {show: true, radius: 3, width: 1.5}, lines: { show: false, width: 1 }, color: "rgb(51,153,255)", clickable: false,hoverable:false }
		];

		t = (this.dm[this.dm.length-1].x-this.dm[0].x)/25;
		var means = [];
		var maxs = [];
		var mins = [];
		var meanstd = 0;
		for(var i = 0; i < this.dmean.length ; i++){
			means.push(this.dmean[i][1]);
			maxs.push(this.dhigh2[i][1]);
			mins.push(this.dlow2[i][1]);
			meanstd += this.dstd[i];
		}
		meanstd /= this.dmean.length
		r = getRange(means);
		if(typeof r=="object"){
			var padd = meanstd*4;
			if(r.min-padd > min(mins)) this.options.yaxis.min = r.min-meanstd*4;
			if(r.max+padd < max(maxs)) this.options.yaxis.max = r.max+meanstd*4;
		}
		/*
		$.plot(this.mainplot, dataset2, this.options);//{ xaxis:xaxis, yaxis: yaxis, legend: { position: 'se' }, grid: { hoverable: true, clickable: true, markings:	[ { color: '#f00', lineWidth: 1, xaxis: { from: line, to: line } }] } });
		*/
		this.graph = $.graph('mainplot', dataset3, {
			xaxis: { label: this.options.xaxis.axisLabel, mode: 'time', min: this.dm[0].x-t, max: this.dm[this.dm.length-1].x+t },
			yaxis: { label: this.options.yaxis.axisLabel, min: this.dl, max: this.dh },
			grid: { show: true, color:'rgb(150,150,150)', border: 2, clickable: true, hoverable: true }
		});

		this.fit(this.dm);
	
	}else if(this.type=="calibrators"){

		var dataset = [];
		var dataplot2 = [];
		for(var d=0 ; d < this.dataplot.length ; d++){
			dataplot2.push([]);
			for(var i=0 ; i < this.dataplot[d].length ; i++){
				dataplot2[d].push({x:this.dataplot[d][i][0],y:this.dataplot[d][i][1],id:this.dataplot[d][i][2]});
			}
		}
		
		//var colours = ["#edc240", "#afd8f8", "#cb4b4b", "#4da74d", "#9440ed","#c29a2d","#87adc7","#a83f3a","#437e47","#5e2796"]
		var colours = ["#d62728","#1e77b4","#edc240","#2ba02c","#9467bd","#8f2323","#1b5278","#9e790b","#076b08","#572b7e","#eb7172","#66aada","#f6dc8c","#76d077","#cebcde"];
		var url = this.url.edit;
		for(var d=0 ; d < this.dataplot.length ; d++){
			if(this.used[d]){
				// Add a data set
				dataset.push({
					data: dataplot2[d],
					points: { show: true, radius: 3, width: 1.5 },
					lines: { show: true ,width: 1.5 },
					color: colours[d],
					clickable: true,
					hoverable: true,
					hover: {
						text: function(e){
							return '<a href="'+url+'{{id}}">Edit the frame<br />at '+unixtohours(e.data.x)+'</a>';
						},
						radius: 7,
						width: 3.5
				    },
				    css: { 'background-color': 'white', 'text-align':'center' },
					class: 'poppitypin chat-bubble'
				});
			}
		}

		if(this.graph) this.graph.updateData(dataset);
		else{
			this.graph = $.graph('mainplot', dataset,{
				xaxis: { label: this.options.xaxis.axisLabel, mode: 'time' },
				yaxis: { label: this.options.yaxis.axisLabel },
				grid: { show: true, color:'rgb(150,150,150)', clickable: true, hoverable: true }
			});
		}

	}else if(this.type=="average"){

		if(this.graph) this.graph.clear();

		var dataset = [];
		var dataplot2 = [];
		var mn = this.dataplot[this.cal.order][0][1];
		var mx = this.dataplot[this.cal.order][0][1];

		for(var d=0 ; d < this.dataplot.length ; d++){
			dataplot2.push([]);
			for(var i=0 ; i < this.dataplot[d].length ; i++){
				dataplot2[d].push({x:this.dataplot[d][i][0],y:this.dataplot[d][i][1],id:this.dataplot[d][i][2]});
				if(this.cal.order==d){
					if(this.dataplot[d][i][1] < mn) mn = this.dataplot[d][i][1];
					if(this.dataplot[d][i][1] > mx) mx = this.dataplot[d][i][1];
				}
			}
		}
		
		var r = (mx-mn);
		mn -= r/10;
		mx += r/10;

		for(var d=0 ; d < this.dataplot.length ; d++) dataset.push({ data: dataplot2[d], points: {show:false}, color: "rgba(0,0,0,"+(this.cal.order==d ? 1 : 0.1)+")", lines: { show: true, width: (this.cal.order==d ? 2 : 1) }, hoverable: false });

		// Update the graph
		if(this.graph){
			this.graph.setOptions({yaxis:{min:mn, max: mx}})
			this.graph.updateData(dataset);
		}else{
			// Create a new graph
			this.graph = $.graph('mainplot', dataset,{
				xaxis: { label: this.options.xaxis.axisLabel, mode: 'time' },
				yaxis: { label: this.options.yaxis.axisLabel, min: mn, max: mx },
				grid: { show: true, color:'rgb(150,150,150)' }
			});
		}

	}
}

Lightcurve.prototype.calibrate_data = function(){
	// Send a server side request for all validated calibrators
	var querstr = "mode=super"	
	$.getJSON(this.url.xhr+"?"+querystr,function(data){
		for (i=0;i<data.dates.length;i++){
			if (typeof data.calibration[i] !='undefined'){
				value = (Number(data.source[i]) - Number(data.background[i]))/(Number(data.calibration[i] -Number(data.background[i])));
				_obj.dcal.push([data.dates[i],value]);
			}
		}
		if (_obj.dcal.length > 0){
			$("#message").css("display","block");
			$("#message").html("Including "+data.calibration.length+" calibrators into the super calibrator");
			$("#message").delay(1500).slideUp("slow");
			$.plot(mainplot,[ { data: _obj.dmine}], _obj.options);
		}else{
			$("#message").css("display","block");
			$("#message").html("There are calibrators available for the supercalibrator");
			$("#message").delay(1500).slideUp("slow");
		}
	});
}

function getRange(d){
	var hi = max(d);
	var lo = min(d);
	var range = hi-lo;
	var i = 0;

	if(range <= 0) return {min:lo,max:hi,inc:1,n:1};

	// potential increment size
	var tinc = Math.pow(10,Math.ceil(Math.log(range/10)/Math.log(10)));

	// Get maximum value on axis
	var tmax = (Math.floor(hi/tinc)*tinc);
	if(tmax < hi) tmax += tinc;

	// Get minimum value on axis
	tmin = tmax;
	do{ i++; tmin -= tinc; }while(tmin > lo);
	
	if(Math.abs(tmin) < 1E-15) tmin = 0.0;
	
	// Increase the number of increments
	while(i < 5) {
		tinc /= 2.0;
		if((tmin + tinc) <= lo) tmin += tinc;
		if((tmax - tinc) >= hi) tmax -= tinc;
		i = i*2;
	}
	return {min:tmin,max:tmax,inc:tinc,n:(tmax-tmin)/tinc};
}
function bin(array){
	var range = getRange(array)
	var mx = max(array);
	var mn = min(array);
	var binned = new Array(range.n);
	for(var i = 0; i < range.n ; i++) binned[i] = [(i*range.inc)+range.min,0]
	for(var i = 0; i < array.length ; i++){
		j = Math.floor((array[i]-range.min)/range.inc);
		if(binned[j]) binned[j] = [((j*range.inc)+range.min),binned[j][1]+1];
		else binned[j] = [((j*range.inc)+range.min),1];
	}
	return binned;
}
function max(array){ return Math.max.apply(Math, array); }
function min(array){ return Math.min.apply(Math, array); }
