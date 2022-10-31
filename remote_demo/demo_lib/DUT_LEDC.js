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

let timeoutId	= null;
let	count	= 0;

function updateSliderFollowup( id, i ) {
	let value = document.getElementById( id + i ).value;
	
	setSliderAndRegisterlistValues( value, "slider", i );

	let url	= REQ_HEADER + 'value=' + value + '&idx=' + i
	ajaxUpdate( url, updateDone )
	
	timeoutId = 0;
}

function updateSlider( element, moving, id, i ) {
	let value = document.getElementById( id + i ).value;
	
	setSliderAndRegisterlistValues( value, "slider", i );
	
	if ( moving ) {
		//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
		if ( timeoutId ) return ;
		timeoutId = setTimeout( function () { timeoutId = 0; }, 50 );
	}
	
	let url	= REQ_HEADER + 'value=' + value + '&idx=' + i
	
	if ( moving )
		ajaxUpdate( url );
	else
		ajaxUpdate( url, updateDone );
}

function updateValField( element, id, i ) {
	let valueFieldElement = document.getElementById( id + i );
	let value	= parseInt( valueFieldElement.value, 16 );
	let no_submit	= 0;
	let	selector;
	
	if ( ("Slider" == id) || ("valField" == id) )
		selector	= "slider";
	else
		selector	= "register";
	
	if ( isNaN( value ) ) {
		no_submit	= 1;
		
		if ( selector == "slider" )
			value = document.getElementById( id + i ).value;
	}
	value	= (value < 0  ) ?   0 : value;
	value	= (255 < value) ? 255 : value;
	valueFieldElement.value = hex( value );

	if ( no_submit )
		return;

	setSliderAndRegisterlistValues( value, selector, i );
	
	if ( selector == "slider" ) {
		let url	= REQ_HEADER + 'value=' + value + '&idx=' + i;
		ajaxUpdate( url, updateDone );
	}
	else {
		let url	= REQ_HEADER + 'reg=' + i + '&val=' + value;
		ajaxUpdate( url );
	}
}

function updateDone() {
	let obj = JSON.parse( this.responseText );
	
	if ( typeof obj.reg === 'undefined' )
		setSliderAndRegisterlistValues( obj.val, "slider", obj.idx );
	else
		setSliderAndRegisterlistValues( obj.val, "register", obj.reg );
}

function setSliderAndRegisterlistValues( value, selector, i, allreg_loading = false ) {
	let	reg_i;
	
	if ( selector == "slider" ) {
		reg_i	= index_slider2register( i )
	}
	else {
		reg_i	= i;
		i		= index_register2slider( reg_i );
	}
	
	if ( 0 <= i ) {
		document.getElementById( "Slider"   + i ).value	= value;		//	in slider table
		document.getElementById( "valField" + i ).value	= hex( value );	//	in slider table
	}
	
	if ( (reg_i == PWMALL_IDX) || (reg_i == IREFALL_IDX) )
		document.getElementById( 'regField' + reg_i ).value	= "--";	//	in register table
	else
		document.getElementById( 'regField' + reg_i ).value	= hex( value );	//	in register table

	if ( allreg_loading )
		return;
	
	let	start;
	let	end;
	if ( (IREF_OFST - 1) == i ) {
		start	= 0;
		end		= N_CHANNELS;
	}
	else if ( (IREF_OFST * 2 - 1) == i ) {
		start	= IREF_OFST + 0;
		end		= IREF_OFST + N_CHANNELS;
	}
	else {
		return;
	}

	for ( let i = start; i < end; i++ )
		setSliderAndRegisterlistValues( value, "slider", i )
}

function index_slider2register( i ) {
	if ( (0 <= i) && (i < N_CHANNELS) )
		r	= i + PWM0_IDX;
	else if ( (IREF_OFST <= i) && (i < IREF_OFST + N_CHANNELS) )
		r	= (i - IREF_OFST) + IREF0_IDX;
	else if ( (IREF_OFST - 1) == i )
		r	= PWMALL_IDX;
	else if ( (IREF_OFST * 2 - 1) == i)
		r	= IREFALL_IDX;
		
	return r;
}

function index_register2slider( i ) {
	if ( (PWM0_IDX <= i) && (i < PWM0_IDX + N_CHANNELS) )
		r	= i - PWM0_IDX;
	else if  ( (IREF0_IDX <= i) && (i < IREF0_IDX + N_CHANNELS) )
		r	= i - IREF0_IDX + IREF_OFST;
	else if ( PWMALL_IDX == i )
		r	= IREF_OFST - 1;
	else if ( IREFALL_IDX == i )
		r	= (IREF_OFST * 2) - 1;
	else
		r	= -2;
	
	return r;
}

function allRegLoad() {
	let url	= REQ_HEADER + 'allreg='
	ajaxUpdate( url, allRegLoadDone );
}

function allRegLoadDone() {
	let obj = JSON.parse( this.responseText );

	for ( let i = 0; i < obj.reg.length; i++ ) {
		setSliderAndRegisterlistValues( obj.reg[ i ], "register", i, allreg_loading = true )
	}
}
 
function loadFinished(){
	allRegLoad();
}

window.addEventListener( 'load', loadFinished );
