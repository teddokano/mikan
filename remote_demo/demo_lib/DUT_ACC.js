let	acc_data	= {
	time:[],
	x:[],
	y:[],
	z:[],
	chart: undefined,

	getAndShow: function () {		
		let url		= REQ_HEADER + "update=1";
		
		ajaxUpdate( url, data => {
			obj = JSON.parse( data );

			obj.forEach( data => {
				this.time.push( data.time );
				this.x.push( data.x );
				this.y.push( data.y );
				this.z.push( data.z );
			});
			
			this.time	= this.time.slice( -100 );
			this.x	= this.x.slice( -100 );
			this.y	= this.y.slice( -100 );
			this.z	= this.z.slice( -100 );
			
			this.draw();
			
			console.log( data.x );
/*			
			if ( this ) {
				let elem = document.getElementById( "temperature" );
				elem.innerText = this.temp[ this.temp.length - 1 ].toFixed( 3 ) + '˚C';
			}
			
			for ( let i = 0; i < TABLE_LEN; i++ )
			{
				document.getElementById( "timeField" + i ).value = this.time.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				
				let	value	= this.temp.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				
				if ( !isNaN( value ) )
					value	= value.toFixed( 3 );
					
				document.getElementById( "tempField" + i ).value = value;
			}
*/
			document.getElementById( "infoFieldValue0" ).value = this.time[ 0 ];
			document.getElementById( "infoFieldValue1" ).value = this.time[ this.time.length - 1 ];
			document.getElementById( "infoFieldValue2" ).value = this.time.length;
		} );
	},

	draw: function () {
		let	ctx = document.getElementById("myLineChart");

		if ( this.chart ) {
			this.chart.destroy();
		}

		this.chart = new Chart( ctx, {
		
			type: 'line',
			data: {
				labels: this.time,
				datasets: [
					{
						label: 'x',
						data: this.x,
						borderColor: "rgba( 255, 0, 0, 1 )",
						backgroundColor: "rgba( 0, 0, 0, 0 )"
					},
					{
						label: 'y',
						data: this.y,
						borderColor: "rgba( 0, 255, 0, 1 )",
						backgroundColor: "rgba( 0, 0, 0, 0 )"
					},
					{
						label: 'z',
						data: this.z,
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
							suggestedMax: GRAPH_HIGH,
							suggestedMin: GRAPH_LOW,
							stepSize: 0.1,
							callback: function(value, index, values){
							return  value +  ' ˚g'
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
		});
	},
	
	save: function () {
		console.log( 'csvFileOut' );
		let str	= [];
		let	len	= this.time.length;
		
		str	+= "time,temp,tos,thyst,os,heater\n";
		for ( let i = 0; i < len; i++ ) {
			str	+= this.time[ i ] + "," +  this.temp[ i ] + "," + this.tos[ i ] + "," + this.thyst[ i ] + "," + this.os[ i ] + "," + this.heater[ i ] + "\n";
		}

		let now		= new Date()
		let blob	= new Blob( [str], {type:"text/csv"} );
		let link	= document.createElement( 'a' );
		link.href	= URL.createObjectURL( blob );
		link.download	= DEV_NAME + "_measurement_result" + now.toString() + ".csv";
		link.click();
	}
}

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
	acc_data.getAndShow();
}

window.addEventListener( 'load', function () {
	acc_data.draw();
	setInterval( getTempAndShow, 100 );
});