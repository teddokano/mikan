function show_setting_panel() {
	let url		= REQ_HEADER + "start_setting";
	
	ajaxUpdate( url, data => {
		let obj = JSON.parse( data );

		document.getElementById( 'TempOffset' ).value	= obj.temperature.ofst;
		document.getElementById( 'TempCoeff'  ).value	= 1 / obj.temperature.coeff;
		document.getElementById( 'TempBase'   ).value	= obj.temperature.base;
	} );

	document.getElementById('show_button').style.display = 'none';
	document.getElementById('hide_button').style.display = 'block';
	document.getElementById('AFEsetting' ).style.display = 'block';
	document.getElementById('graph_acc'  ).style.display = 'none';
	document.getElementById('graph_mag'  ).style.display = 'none';
}

function hide_setting_panel() {
	document.getElementById('show_button').style.display = 'block';
	document.getElementById('hide_button').style.display = 'none';
	document.getElementById('AFEsetting' ).style.display = 'none';
	document.getElementById('graph_acc'  ).style.display = 'block';
	document.getElementById('graph_mag'  ).style.display = 'block';
}

function zero_setting() {
	let url		= REQ_HEADER + "weight_zero";
	ajaxUpdate( url );
}

function load_default_setting() {
	let url		= REQ_HEADER + "load_default_setting";

	ajaxUpdate( url, data => {
		let obj = JSON.parse( data );

		document.getElementById( 'TempOffset' ).value	= obj.temperature.ofst;
		document.getElementById( 'TempCoeff'  ).value	= 1 / obj.temperature.coeff;
		document.getElementById( 'TempBase'   ).value	= obj.temperature.base;
	} );
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

	ajaxUpdate( REQ_HEADER + "cal_weight_scale=" + JSON.stringify( obj ) );
}

function updateTempSetting() {
	const fields	= { 'TempOffset': 'ofst', 'TempCoeff': 'coeff', 'TempBase': 'base' }
	let obj	= {};
	
	for ( let key in fields ) {
		value	= document.getElementById( key ).value - 0;
		
		if ( isNaN( value ) ) {
			return;
		}
		
		obj[ fields[ key ] ]	= value;
	}
	
	obj.coeff	= 1 / obj.coeff;
	
	ajaxUpdate( REQ_HEADER + "cal_temp=" + JSON.stringify( obj ) );
}
