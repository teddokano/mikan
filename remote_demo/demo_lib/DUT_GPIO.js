
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

function allRegLoad() {
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
				setRegisterBits( i, v, pv )
				
				elem.style.border = "solid 1px #FF0000";
				setTimeout( e => {
					e.style.border = "solid 1px #FFFFFF";
				}, 1000, elem )
			}
		}
		prev_reg	= obj.reg;
	} );
}

function setRegisterBits( ri, v, pv ) {
	if ( bf_reg.includes( ri ) )
		for ( let i = 7; 0 <= i; i-- )
		{
			b_v		= ( v >> i) & 0x1;
			b_pv	= (pv >> i) & 0x1;
			
			if ( b_v != b_pv ) {
				elem		= document.getElementById('bitField' + ri + '-' + i );
				elem.value	= b_v ? 1 : 0;

				elem.style.border = "solid 1px #FF0000";
				setTimeout( e => {
					e.style.border = "solid 1px #FFFFFF";
				}, 1000, elem )
			}
		}
}

let	intervalTimer;
function AutoReloadSwitch() {
	let autoReloadSwitchElement	= document.getElementById( "AutoReloadSwitch" );
	var elem = Array.from( document.getElementsByClassName( "reg_table_val" ) );
	
	console.log( elem );
	elem.forEach( e => console.log( e ) );
	
	if ( autoReloadSwitchElement.checked ) {
		elem.forEach( e => console.log( e.style.border = "solid 1px #8080FF" ) );
		intervalTimer	= setInterval( allRegLoad, 200 );
	} else {
		elem.forEach( e => console.log( e.style.border = "solid 1px #FFFFFF" ) );
		clearInterval( intervalTimer );
	}
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
});
