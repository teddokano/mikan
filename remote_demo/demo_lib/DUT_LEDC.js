/*
 *	Javascript code for DUT_LEDC.py
 *
 *	This script will be processed in DUT_LEDC.py to replace "{%  %}" valriables
 */

const	PWM0_IDX	=  {% pwm0_idx %};
const	IREF0_IDX	=  {% iref0_idx %};
const	PWMALL_IDX	=  {% pwmall_idx %};
const	IREFALL_IDX	=  {% irefall_idx %};
const	N_CHANNELS	=  {% n_ch %};
const	IREF_OFST	=  {% iref_ofst %};
const	IREF_INIT	=  {% iref_init %};

/****************************
 ****	slider controls
 ****************************/
 
let timeoutId	= null;

/******** updateSlider ********/

function updateSlider( element, moving, idx ) {
	let value = document.getElementById( "Slider" + idx ).value;
	
	setSliderValues( idx, value );

	if ( moving ) {
		//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
		if ( timeoutId ) return ;
		timeoutId = setTimeout( function () { timeoutId = 0; }, 50 );
	}
	
	//console.log( 'pwm' + idx + ': ' + value + ', moving?: ' + moving );

	let url	= REQ_HEADER + 'value=' + value + '&idx=' + idx
	ajaxUpdate( url )
}

function updateSliderDone() {
	let obj = JSON.parse( this.responseText );
	setSliderValues( obj.idx, obj.value );
}

/******** updateValField ********/

function updateValField( element, idx ) {
	let valueFieldElement = document.getElementById( "valField" + idx );
	let value	= parseInt( valueFieldElement.value, 16 )
	let no_submit	= 0
	
	if ( isNaN( value ) ) {
		no_submit	= 1
		value = document.getElementById( "Slider" + idx ).value;
	}
	value	= (value < 0  ) ?   0 : value
	value	= (255 < value) ? 255 : value
	valueFieldElement.value = hex( value )

	if ( no_submit )
		return;

	setSliderValues( idx, value );
	console.log( 'pwm' + idx + ': ' + value );
	
	let url	= REQ_HEADER + 'value=' + value + '&idx=' + idx
	ajaxUpdate( url )
}

/******** setSliderValues ********/

function setSliderValues( i, value ) {
	setSlider( i, value );

	if ( 0 == IREF_OFST )
		return;
		
	if ( i == (IREF_OFST - 1) )
		setAllSliderValues( 0, N_CHANNELS, value );
	else if ( i == (IREF_OFST* 2 - 1) )
		setAllSliderValues( IREF_OFST, N_CHANNELS, value );
}

/******** setAllSliderValues ********/

function setAllSliderValues( start, length, value ) {
	for ( let i = start; i < start + length; i++ ) {
		setSlider( i, value );
	}
}

function setSlider( idx, value ) {
	document.getElementById( "Slider" + idx ).value = value;
	document.getElementById( "valField" + idx ).value = hex( value );
	
	let reg_idx;
	
	if ( idx <= N_CHANNELS )
		reg_idx	= PWM0_IDX + idx;
	else if ( idx == (IREF_OFST - 1) )
		reg_idx = PWMALL_IDX;
	else if ( idx == (IREF_OFST * 2 - 1) )
		reg_idx	= IREFALL_IDX;
	else
		reg_idx	= IREF0_IDX + (idx - IREF_OFST);
	
	writeRegisterField( reg_idx, value );
}

/****************************
 ****	register controls
 ****************************/
 
/******** updateRegField ********/

function updateRegField( element, idx ) {
	let valueFieldElement = document.getElementById( "regField" + idx );
	let value	= parseInt( valueFieldElement.value, 16 )
	let no_submit	= 0
	
	if ( isNaN( value ) ) {
		no_submit	= 1
		value = document.getElementById( "Slider" + idx ).value;
	}
	value	= (value < 0  ) ?   0 : value
	value	= (255 < value) ? 255 : value
	valueFieldElement.value = hex( value )

	if ( no_submit )
		return;

	let url	= REQ_HEADER + 'reg=' + idx + '&val=' + value
	ajaxUpdate( url, updateRegFieldDone )
}

function updateRegFieldDone() {
	let obj = JSON.parse( this.responseText );
	
	setRegField( obj.reg, obj.val )
}

/******** allRegLoad ********/

function allRegLoad() {
	let url	= REQ_HEADER + 'allreg='
	ajaxUpdate( url, allRegLoadDone );
}

/******** allRegLoadDone ********/

function allRegLoadDone() {
	let obj = JSON.parse( this.responseText );

	for ( let i = 0; i < obj.reg.length; i++ ) {
		setRegField( i, obj.reg[ i ], manual_input = false )
	}
}

function setRegField( idx, value, manual_input = true ) {

	if ( (PWM0_IDX <= idx) && (idx < (PWM0_IDX + N_CHANNELS)) )
		setSliderValues( idx - PWM0_IDX, value );
	else if ( IREF0_IDX && (IREF0_IDX <= idx) && (idx < (IREF0_IDX + N_CHANNELS)) )
		setSliderValues( (idx - IREF0_IDX) + IREF_OFST, value );
	else if ( manual_input && PWMALL_IDX && (idx == PWMALL_IDX) )
		setSliderValues( IREF_OFST - 1, value );
	else if ( manual_input && IREFALL_IDX && (idx == IREFALL_IDX) )
		setSliderValues( IREF_OFST * 2 - 1, value );
	else
		writeRegisterField( idx, value );
}

function writeRegisterField( idx, value ) {
	document.getElementById( 'regField' + idx ).value	= hex( value );
}

					
/****************************
 ****	page load controls
 ****************************/
 
function loadFinished(){
	allRegLoad();

	if ( 0 == IREF_OFST )
		return;

	//setAllSliderValues( IREF_OFST, N_CHANNELS, IREF_INIT );
	//setAllSliderValues( IREF_OFST * 2 - 1, 1, IREF_INIT );
	
}

window.addEventListener( 'load', loadFinished );
