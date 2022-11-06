/*
 *	Javascript code for DUT_TEMP.py
 *
 *	This script will be processed in DUT_LEDC.py to replace "{%  %}" valriables
 */

const	TABLE_LEN	= {% table_len %}
const	GRAPH_HIGH	= {% graph_high %}
const	GRAPH_LOW	= {% graph_low %}
const	TOS_INIT	= {% tos_init %}
const	THYST_INIT	= {% thyst_init %}
const	OS_LABEL	= 'OS pin ( high@' + GRAPH_HIGH + ' / low@' + GRAPH_LOW + ' )'

let	time	= []
let	temp	= []
let	tos		= []
let	thyst	= []
let	os		= []
let	heater	= []

function drawChart() {
	console.log( 'drawing' );

	var ctx = document.getElementById("myLineChart");
	window.myLineChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: time,
			datasets: [
				{
					label: 'temperature',
					data: temp,
					borderColor: "rgba( 255, 0, 0, 1 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: 'Tos',
					data: tos,
					borderColor: "rgba( 255, 0, 0, 0.3 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: 'Thyst',
					data: thyst,
					borderColor: "rgba( 0, 0, 255, 0.3 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: OS_LABEL,
					data: os,
					borderColor: "rgba( 0, 255, 0, 0.5 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: 'Heater',
					data: heater,
					borderColor: "rgba( 255, 0, 0, 0.0 )",
					backgroundColor: "rgba( 255, 0, 0, 0.1 )"
				},
			],
		},
		options: {
			animation: false,
			title: {
				display: true,
				text: 'temperature now'
			},
			scales: {
				yAxes: [{
					ticks: {
						suggestedMax: GRAPH_HIGH,
						suggestedMin: GRAPH_LOW,
						stepSize: 1,
						callback: function(value, index, values){
						return  value +  ' ˚C'
						}
					},
					scaleLabel: {
						display: true,
						labelString: 'temperature [˚C]'
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
}

/****************************
 ****	temp display
 ****************************/

/******** getTempAndShow ********/

function getTempAndShow() {
	let url	= REQ_HEADER + "update";
	ajaxUpdate( url, getTempAndShowDone );
}

let prev_reg	= [];

function getTempAndShowDone() {
	let obj = JSON.parse( this.responseText );

	//	server sends multiple data.
	//	pick one sample from last and store local memory
	idx	= obj.data.time.length - 1;
	temperature	= obj.data.temp[ idx ];
	
	time.push( obj.data.time[ idx ] );
	temp.push( temperature );
	tos.push( obj.data.tos[ idx ] );
	thyst.push( obj.data.thyst[ idx ] );
	os.push( obj.data.os[ idx ] );
	heater.push( obj.data.heater[ idx ] );

	drawChart();
	
	var elem = document.getElementById( "temperature" );
	elem.innerText = temperature.toFixed( 3 ) + '˚C';

	
	for ( let i = 0; i < TABLE_LEN; i++ )
	{
		document.getElementById( "timeField" + i ).value = time.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
		
		let	value	= temp.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
		
		if ( !isNaN( value ) )
			value	= value.toFixed( 3 );
			
		document.getElementById( "tempField" + i ).value = value;
	}
	
	document.getElementById( "infoFieldValue0" ).value = time[ 0 ];
	document.getElementById( "infoFieldValue1" ).value = time[ time.length - 1 ];
	document.getElementById( "infoFieldValue2" ).value = time.length;
}

/****************************
 ****	widget handling
 ****************************/

/******** updateSlider ********/

function updateSlider( element, moving, idx ) {
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

function updateValField( element, idx ) {
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
	ajaxUpdate( url, setTosThystDone );
}

/******** setTosThystDone ********/

function setTosThystDone() {
	let obj = JSON.parse( this.responseText );
}

function csvFileOut(  time, temp  ) {
	console.log( 'csvFileOut' );
	let str	= [];
	let	len	= time.length;
	
	str	+= "time,temp,tos,thyst,os\n";
	for ( let i = 0; i < len; i++ ) {
		str	+= time[ i ] + "," +  temp[ i ] + "," + tos[ i ] + "," + thyst[ i ] + "," + os[ i ] + "\n";
	}
	
	let blob	= new Blob( [str], {type:"text/csv"} );
	let link	= document.createElement( 'a' );
	link.href	= URL.createObjectURL( blob );
	link.download	= DEV_NAME + "_measurement_result.csv";
	link.click();
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

function updateHeaterSwitch( element ) {
	let heaterSwitchElement	= document.getElementById( "heaterSwitch" );
	let	val;
	
	if ( heaterSwitchElement.checked )
		val	= 1;
	else
		val	= 0;
		
	let url	= REQ_HEADER + 'heater=' + val;
	ajaxUpdate( url );
}

window.addEventListener( 'load', function () {
	drawChart();
	setInterval( getTempAndShow, 1000 );
});
