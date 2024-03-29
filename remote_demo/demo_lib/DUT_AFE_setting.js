let	reference_junction_temp_select	= 0;
let	temp_message_interval;

function show_setting_panel() {
	let url		= REQ_HEADER + "start_setting";
	
	ajaxUpdate( url, data => { set_fields( data ); } );

	document.getElementById('show_button').style.display = 'none';
	document.getElementById('hide_button').style.display = 'block';
	document.getElementById('AFEsetting' ).style.display = 'block';
	document.getElementById('graph_acc'  ).style.display = 'none';
	document.getElementById('graph_mag'  ).style.display = 'none';
	
	temp_message_interval	= setInterval( get_temp_message, 200 )
}

function hide_setting_panel() {
	clearInterval( temp_message_interval );

	document.getElementById('show_button').style.display = 'block';
	document.getElementById('hide_button').style.display = 'none';
	document.getElementById('AFEsetting' ).style.display = 'none';
	document.getElementById('graph_acc'  ).style.display = 'block';
	document.getElementById('graph_mag'  ).style.display = 'block';	
}

function zero_setting() {
	let url		= REQ_HEADER + "weight_zero";
	ajaxUpdate( url, timeout = 5000 );
}

function load_default_setting() {
	let url		= REQ_HEADER + "load_default_setting";

	ajaxUpdate( url, data => {
		set_fields( data );
	} );
}

function set_fields( data ) {
	let obj = JSON.parse( data );

	document.getElementById( 'TempOffset'  ).value	= obj.temperature.ofst;
	document.getElementById( 'TempCoeff'   ).value	= 1 / obj.temperature.coeff;
	document.getElementById( 'TempBase'    ).value	= obj.temperature.base;
	document.getElementById( 'TempAddress' ).value	= hex( obj.temperature.target );
	
	reference_junction_temp_select	= obj.temperature.select;
	
	let elements = document.getElementsByName( 'rjt' );
	elements[ obj.temperature.select ].checked = true;

	document.getElementById( 'Ch0max'  ).value	= obj.scales[ 0 ].max;
	document.getElementById( 'Ch0min'  ).value	= obj.scales[ 0 ].min;
	document.getElementById( 'Ch1max'  ).value	= obj.scales[ 1 ].max;
	document.getElementById( 'Ch1min'  ).value	= obj.scales[ 1 ].min;
}

function updateTempRadio( select ) {
	console.log( "updateTempRadio = " + select  );
	reference_junction_temp_select	= select;
	
	updateTempSetting();
}

function scale_calibration() {
	const fields	= { 'cal_scale_input': 'cal' }
	let obj	= {};
	
	for ( let key in fields ) {
		value	= document.getElementById( key ).value - 0;
		
		if ( isNaN( value ) ) {
			return;
		}
		
		obj[ fields[ key ] ]	= value;
	}

	ajaxUpdate( REQ_HEADER + "cal_weight_scale=" + JSON.stringify( obj ), timeout = 5000 );
}

function updateTempSetting() {
	const fields	= { 'TempOffset': 'ofst', 'TempCoeff': 'coeff', 'TempBase': 'base' }
	let obj		= {};
	
	for ( let key in fields ) {
		let value	= document.getElementById( key ).value - 0;
		
		if ( isNaN( value ) ) {
			return;
		}
		
		obj[ fields[ key ] ]	= value;
	}

	obj.scales	= [ {}, {} ];
	obj.scales[ 0 ].max		= document.getElementById( 'Ch0max' ).value - 0;
	obj.scales[ 0 ].min		= document.getElementById( 'Ch0min' ).value - 0;
	obj.scales[ 1 ].max		= document.getElementById( 'Ch1max' ).value - 0;
	obj.scales[ 1 ].min		= document.getElementById( 'Ch1min' ).value - 0;

	let num_check	= [ obj.scales[ 0 ].max, obj.scales[ 0 ].min, obj.scales[ 1 ].max, obj.scales[ 1 ].min ];
	let	err	= false;
	num_check.forEach( ( n ) => { console.log(n);if ( isNaN( n ) ) err = true; } )
	if ( err )
		return;
	
	let value	= parseInt( document.getElementById( 'TempAddress' ).value, 16 );

	if ( isNaN( value ) ) {
		return;
	}
	
	obj.target	= value;
	
	if ( 0 == obj.coeff )
	{
		obj.coeff	= 0.01;
		document.getElementById( 'TempCoeff' ).value	= obj.coeff;
	}
	obj.coeff	= 1 / obj.coeff;
	obj.select	= reference_junction_temp_select;
	
	ajaxUpdate( REQ_HEADER + "cal_temp=" + JSON.stringify( obj ) );
}

function get_temp_message() {
	ajaxUpdate( REQ_HEADER + "get_temp_message", data => {
		document.getElementById( "temp_message" ).innerText = data;
		}, 
		100
	);	
}
