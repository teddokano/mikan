let timeoutId	= null;
let	count		= 0;
let	InitReqRate	= 20;
let	maxReqRate	= InitReqRate;

function updateSlider( moving, id, i ) {
	let value = document.getElementById( id + i ).value;
	
	setSliderAndRegisterlistValues( value, "slider", i );
	
	if ( moving ) {
		//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
		if ( timeoutId ) return ;
		timeoutId = setTimeout( function () { timeoutId = 0; }, 1000 / maxReqRate );
	}

	let url	= REQ_HEADER + 'value=' + value + '&idx=' + i
	//console.log( 'moving = ' + moving + ', value = ' + value );
	
	if ( moving )
		ajaxUpdate( url, null, timeout = 1000 / maxReqRate - 5 );
	else
		ajaxUpdate( url, updateDone );
}

function updateValField( id, i ) {
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

function updateDone( data ) {
	let obj = JSON.parse( data );
	
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
	
	if ( PWMALL_IDX & ((reg_i == PWMALL_IDX) || (reg_i == IREFALL_IDX)) )
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

function allRegLoadDone( data ) {
	//	Needed to be a indivisual function, to be called from "LEDC_gradation_control.js"
	let obj = JSON.parse( data );

	 for ( let i = 0; i < obj.reg.length; i++ ) {
		 setSliderAndRegisterlistValues( obj.reg[ i ], "register", i, allreg_loading = true )
	 }
}

function setMaxReqRate( reqRate = 0 ) {
	elem		= document.getElementById( 'maxReqRate' );
	
	if ( !reqRate )
		maxReqRate	= elem.value;
	else
		maxReqRate	= reqRate;
	
	maxReqRate	= (maxReqRate <  1) ?  1 : maxReqRate;
	maxReqRate	= (30 < maxReqRate) ? 30 : maxReqRate;
	
	elem.value	= maxReqRate;
}
 
function resetMaxReqRate() {
	maxReqRate	= InitReqRate;
	document.getElementById( 'maxReqRate' ).value	= maxReqRate;
}

async function measureResponse( n = 10 ) {
	let url		= REQ_HEADER + 'value=' + 16 + '&idx=' + 199;
	let	resp	= [];
	
	for ( let i = 0; i < n; i++ ) {
		let start	= performance.now();
		await new Promise( (resolve, reject) => { ajaxUpdate( url, () => resolve(), 1000 ) } )
		resp.push( performance.now() - start );
	}
	
	resp.sort( (a, b) => (a - b) );
	median	= resp[ Math.trunc(n / 2) ]
	
	//resp.forEach( t => console.log( t ) );
	
	console.log( 'measured server response ---' );
	console.log( '- max:' + Math.max( ...resp ) + 'ms' );
	console.log( '- min:' + Math.min( ...resp ) + 'ms' );
	console.log( '- median:' + median + 'ms' );
	
	setMaxReqRate( reqRate = 1000 / (median + 5) );
}

window.addEventListener( 'load', function () {
	allRegLoad();
	setDefaultSelection();
	measureResponse();
} );
