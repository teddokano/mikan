class GraphDraw {
	constructor( id, req, cs ) {
		this.id		= id;
		this.req	= req;
		this.cs		= cs;
		this.chart	= undefined;
	}

	getAndShow() {		
		let url		= REQ_HEADER + this.req;
		let time	= this.cs.data.labels;
		let x		= this.cs.data.datasets[0].data;
		let y		= this.cs.data.datasets[1].data;
		let z		= this.cs.data.datasets[2].data;

		ajaxUpdate( url, data => {
			let obj = JSON.parse( data );

			obj.forEach( data => {
				time.push( data.time );
				x.push( data.x );
				y.push( data.y );
				z.push( data.z );
			});

			if ( 100 < time.length ) {
				this.cs.data.labels.shift();
				this.cs.data.datasets[0].data.shift();
				this.cs.data.datasets[1].data.shift();
				this.cs.data.datasets[2].data.shift();
			}
 
			this.draw();

			for ( let i = 0; i < TABLE_LEN; i++ )
			{
				document.getElementById( "timeField" + i ).value = time.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				
				let	xv	= x.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				let	yv	= y.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				let	zv	= z.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				
				xv	= isNaN( xv ) ? x : xv.toFixed( 6 );
				yv	= isNaN( yv ) ? y : yv.toFixed( 6 );
				zv	= isNaN( yv ) ? z : zv.toFixed( 6 );
					
				document.getElementById( "xField" + i ).value = xv;
				document.getElementById( "yField" + i ).value = yv;
				document.getElementById( "zField" + i ).value = zv;
			}

			document.getElementById( "infoFieldValue0" ).value = time[ 0 ];
			document.getElementById( "infoFieldValue1" ).value = time[ time.length - 1 ];
			document.getElementById( "infoFieldValue2" ).value = time.length;
		} );
	}

	show_obj() {
		console.log( '========================================================' );
		console.log( this.cs );
	}

	draw() {
		let	ctx = document.getElementById( this.id );
		
		if ( this.chart )
			this.chart.destroy();

		this.chart = new Chart( ctx, this.cs );
	}

	save() {
		console.log( 'csvFileOut' );
		let str		= [];
		let time	= this.cs.data.labels;
		let x		= this.cs.data.datasets[0].data;
		let y		= this.cs.data.datasets[1].data;
		let z		= this.cs.data.datasets[2].data;

		let	len	= time.length;
		  
		str	+= "time,x,y,z\n";
		for ( let i = 0; i < len; i++ ) {
			str	+= time[ i ] + "," +  x[ i ] + "," + y[ i ] + "," + z[ i ] + "\n";
		}

		let now		= new Date()
		let blob	= new Blob( [str], {type:"text/csv"} );
		let link	= document.createElement( 'a' );
		link.href	= URL.createObjectURL( blob );
		link.download	= DEV_NAME + "_measurement_result" + now.toString() + ".csv";
		link.click();
	}
}

let	acc	= {
type: 'line',
	data: {
		labels: [],
		datasets: [
			{
				label: 'x',
				data: [],
				borderColor: "rgba( 255, 0, 0, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
			{
				label: 'y',
				data: [],
				borderColor: "rgba( 0, 255, 0, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
			{
				label: 'z',
				data: [],
				borderColor: "rgba( 0, 0, 255, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
		],
	},
	options: {
		animation: false,
		title: {
			display: true,
			text: '"g" now'
		},
		scales: {
			yAxes: [{
				ticks: {
					suggestedMax: 2.0,
					suggestedMin: -2.0,
					stepSize: 1,
					callback: function(value, index, values){
					return  value +  ' g'
					}
				},
				scaleLabel: {
					display: true,
					labelString: ' gravitational acceleration [g]'
				}
			}],
			xAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'time'
				}
			}]
		},
	}
};

accGraph	= new GraphDraw( "Chart0", "update=1", acc );


/****************************
 ****	widget handling
 ****************************/

/******** updateSlider ********/

function updateSlider( moving, idx ) {
	let tos		= document.getElementById( "Slider0" ).value;
	let thyst	= document.getElementById( "Slider1" ).value;

	tos		= parseFloat( tos );	//	<-- this is required to let correct compare
	thyst	= parseFloat( thyst );	//	<-- this is required to let correct compare

	if ( idx == 0 ) {
		thyst	= ( tos < thyst ) ? tos : thyst;
		//thyst=tos;
	}
	else {
		tos		= ( tos < thyst ) ? thyst : tos;
		//tos=thyst;
	}

	setSliderValues( 0, tos   );
	setSliderValues( 1, thyst );
}

/******** updateValField ********/

function updateValField( idx ) {
	let valueFieldElement = document.getElementById( "valField" + idx );
	let value	= parseFloat( valueFieldElement.value );
	let no_submit	= 0;
	
	if ( isNaN( value ) ) {
		no_submit	= 1;
		value = document.getElementById( "Slider" + idx ).value;
	}
	value	= (value < -55  ) ? -55 : value;
	value	= (125   < value) ? 125 : value;

	setSliderValues( idx, value );
}

/******** setSliderValues ********/

function setSliderValues( idx, value ) {

	document.getElementById( "Slider" + idx ).value = value;
	document.getElementById( "valField" + idx ).value = value.toFixed( 1 );
}

/******** setTosThyst ********/

function setTosThyst() {
	let valueFieldElementTos	= document.getElementById( "valField0" );
	let valueFieldElementThyst	= document.getElementById( "valField1" );
	let tos		= parseFloat( valueFieldElementTos.value );
	let thyst	= parseFloat( valueFieldElementThyst.value );

	let url	= REQ_HEADER + 'tos=' + tos.toFixed( 1 ) + '&thyst=' + thyst.toFixed( 1 );
	ajaxUpdate( url );
}

function setConfig() {
	let config_panel = document.getElementById( 'config_panel' );
	radioNodeList = config_panel.elements[ 'os_polarity' ];
	let	pol	= radioNodeList.value;
	radioNodeList = config_panel.elements[ 'os_mode' ];
	let	mod	= radioNodeList.value;
	
	let url	= REQ_HEADER + 'os_polarity=' + pol + '&os_mode=' + mod;
	ajaxUpdate( url );
}

function updateHeaterSwitch() {
	let heaterSwitchElement	= document.getElementById( "heaterSwitch" );
	let	val;
	
	if ( heaterSwitchElement.checked )
		val	= 1;
	else
		val	= 0;
		
	let url	= REQ_HEADER + 'heater=' + val;
	ajaxUpdate( url );
}

function csvFileOut() {
	acc_data.save();
}

function getTempAndShow() {
	accGraph.getAndShow();
}

window.addEventListener( 'load', function () {
	accGraph.draw();
	setInterval( getTempAndShow, 100 );
});
