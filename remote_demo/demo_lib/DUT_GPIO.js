let initAllRegReloadInterval	= 5;
let	allRegReloadInterval		= initAllRegReloadInterval;

function updateRegField( idx ) {
	let valueFieldElement = document.getElementById( "regField" + idx );
	let value	= parseInt( valueFieldElement.value, 16 );
	let no_submit	= 0;
	
	if ( isNaN( value ) ) {
		no_submit	= 1;
		value = document.getElementById( "Slider" + idx ).value;
	}
	value	= (value < 0  ) ?   0 : value;
	value	= (255 < value) ? 255 : value;
	valueFieldElement.value = hex( value );

	if ( no_submit )
		return;

	setRegisterBits( idx, value )

	let url	= REQ_HEADER + "reg=" + idx + "&val=" + value;
	ajaxUpdate( url )
	allRegLoad();
}

function updateBitField( ri, bi ) {
	let bv	= document.getElementById( "bitField" + ri + '-' + bi ).value;
	let elm	= document.getElementById( "regField" + ri );
	let rv	= parseInt( elm.value, 16 );
	
	rv	&= ~(0x1 << bi);
	rv	|=    bv << bi;
	
	elm.value	= hex( rv );
	
	updateRegField( ri );
}

let prev_reg	= [];	//	to prevent refresh on user writing field
let bf_reg		= [];

function allRegLoad( timeout = 5000 ) {
	let url	= REQ_HEADER + 'allreg='
	
	ajaxUpdate( url, data => {
		let obj = JSON.parse( data );

		bf_reg	= obj.bf_reg

		for ( let i = 0; i < obj.reg.length; i++ ) {
			let v		= obj.reg[ i ];
			let elem	= document.getElementById('regField' + i );
			let pv		= prev_reg[ i ];
			
			if ( pv != v ) {
				elem.value	= hex( v );
				setRegisterBits( i, v )
				
				highlight( elem );
			}
		}
		prev_reg	= obj.reg;
	}, 
	timeout );
}

function setRegisterBits( ri, v ) {
	if ( bf_reg.includes( ri ) ) {
		for ( let i = 7; 0 <= i; i-- )
		{
			let b_v		= ( v >> i) & 0x1;
			let elem	= document.getElementById('bitField' + ri + '-' + i );
			
			if ( elem.value	!= b_v ) {
				elem.value	= b_v;
				highlight( elem );
			}
		}
	}
}

let	intervalTimer;
function AutoReloadSwitch() {
	let autoReloadSwitchElement	= document.getElementById( "AutoReloadSwitch" );
	let elem = Array.from( document.getElementsByClassName( "reg_table_val" ) );
	
	if ( autoReloadSwitchElement.checked ) {
		elem.forEach( e => e.style.border = "solid 1px #8080FF" );
		let interval	= 1000 / allRegReloadInterval;
		intervalTimer	= setInterval( allRegLoad, interval, interval - 20 );
		console.log( 'autoReloadSwitchElement=ON: ' );		
		//measureResponseGPIO();
	} else {
		elem.forEach( e => e.style.border = "solid 1px #FFFFFF" );
		clearInterval( intervalTimer );
		console.log( 'autoReloadSwitchElement=OFF: ' );		
		//measureResponseGPIO();
	}
}

function measureResponseGPIO() {
	let url	= REQ_HEADER + 'allreg=';
	let	resp;
	
	responseTime( url )
		.then( ( resp ) => { 
			showResponseTimeResult( resp );		
//			setMaxReqRate( reqRate = 1000 / (resp.median + 5) );
	} );
	responseTime( url )
		.then( ( resp ) => { 
			showResponseTimeResult( resp );		
//			setMaxReqRate( reqRate = 1000 / (resp.median + 5) );
	} );
}

let reg_list	= {};

function getRegList() {
	let url	= REQ_HEADER + 'reglist'
	
	ajaxUpdate( url, () => {
		let obj = JSON.parse( this.responseText );

		obj.reglist.forEach( ( element, i ) => {
			reg_list[ element.name ]	= { "idx" : element.idx, "i" : i }
		} )
		console.log( reg_list );
	} );
}

window.addEventListener( 'load', function () {
	allRegLoad();
	getRegList();
	//measureResponseGPIO();
});
