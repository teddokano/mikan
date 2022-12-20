const	TABLE_LEN	= {% table_len %}
const	GRAPH_HIGH	= {% graph_high %}
const	GRAPH_LOW	= {% graph_low %}
const	TOS_INIT	= {% tos_init %}
const	THYST_INIT	= {% thyst_init %}
const	OS_LABEL	= 'OS pin ( high@' + GRAPH_HIGH + ' / low@' + GRAPH_LOW + ' )'
const	MAX_N_DATA	= {% max_n_data %}

let	temp_data	= {
	time:[],
	temp:[],
	tos:[],
	thyst:[],
	os:[],
	heater:[]
}

function drawChart() {
	var ctx = document.getElementById("myLineChart");
	window.myLineChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: temp_data.time,
			datasets: [
				{
					label: 'temperature',
					data: temp_data.temp,
					borderColor: "rgba( 255, 0, 0, 1 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: 'Tos',
					data: temp_data.tos,
					borderColor: "rgba( 255, 0, 0, 0.3 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: 'Thyst',
					data: temp_data.thyst,
					borderColor: "rgba( 0, 0, 255, 0.3 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: OS_LABEL,
					data: temp_data.os,
					borderColor: "rgba( 0, 255, 0, 0.5 )",
					backgroundColor: "rgba( 0, 0, 0, 0 )"
				},
				{
					label: 'Heater',
					data: temp_data.heater,
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

let	lastTime;

function pastSec() {
	let	now	= Date.now();
	let	past	= now - lastTime;
	lastTime	= now;

	return isNaN( past ) ? MAX_N_DATA : parseInt( past / 1000 );
}

/******** getTempAndShow ********/

function getTempAndShow() {
	let	past	= pastSec();
	//console.log( past );
	let url	= REQ_HEADER + "update=" + (past + 1);
	ajaxUpdate( url, getTempAndShowDone );
}

function getTempAndShowDone() {
	//console.time( 'getTempAndShowDone' );	
	let obj = JSON.parse( this.responseText );

	obj.forEach( data => {
		if ( temp_data.time.includes( data.time ) )
			return;
		
		temp_data.time.push(   data.time   );
		temp_data.temp.push(   data.temp   );
		temp_data.tos.push(    data.tos    );
		temp_data.thyst.push(  data.thyst  );
		temp_data.os.push(     data.os     );
		temp_data.heater.push( data.heater );
	});
	
	drawChart();
	
	if ( temp_data ) {
		let elem = document.getElementById( "temperature" );
		elem.innerText = temp_data.temp[ temp_data.temp.length - 1 ].toFixed( 3 ) + '˚C';
	}

	
	for ( let i = 0; i < TABLE_LEN; i++ )
	{
		document.getElementById( "timeField" + i ).value = temp_data.time.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
		
		let	value	= temp_data.temp.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
		
		if ( !isNaN( value ) )
			value	= value.toFixed( 3 );
			
		document.getElementById( "tempField" + i ).value = value;
	}
	
	document.getElementById( "infoFieldValue0" ).value = temp_data.time[ 0 ];
	document.getElementById( "infoFieldValue1" ).value = temp_data.time[ temp_data.time.length - 1 ];
	document.getElementById( "infoFieldValue2" ).value = temp_data.time.length;
	//console.timeEnd( 'getTempAndShowDone' );
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
	ajaxUpdate( url, setTosThystDone );
}

/******** setTosThystDone ********/

function setTosThystDone() {
	let obj = JSON.parse( this.responseText );
}

function csvFileOut() {
	console.log( 'csvFileOut' );
	let str	= [];
	let	len	= temp_data.time.length;
	
	str	+= "time,temp,tos,thyst,os\n";
	for ( let i = 0; i < len; i++ ) {
		str	+= temp_data.time[ i ] + "," +  temp_data.temp[ i ] + "," + temp_data.tos[ i ] + "," + temp_data.thyst[ i ] + "," + temp_data.os[ i ] + "," + temp_data.heater[ i ] + "\n";
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

window.addEventListener( 'load', function () {
	drawChart();
	setInterval( getTempAndShow, 1000 );
});
