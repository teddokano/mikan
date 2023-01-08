
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
	
	ajaxUpdate( url, function ( data ){
		let obj = JSON.parse( data );

		bf_reg	= obj.bf_reg

		for ( let i = 0; i < obj.reg.length; i++ ) {
			v	= obj.reg[ i ];
			
			if ( prev_reg[ i ] != v )
				document.getElementById('regField' + i ).value	= hex( v );
				setRegisterBits( i, v )
		}
		prev_reg	= obj.reg;
	} );
}

function setRegisterBits( ri, v ) {
	if ( bf_reg.includes( ri ) )
		for ( let i = 7; 0 <= i; i-- )
			document.getElementById('bitField' + ri + '-' + i ).value	= (v >> i) & 0x1;
}

function singleReload() {
	allRegLoad();
}

let	intervalTimer;
function autoReload() {
	intervalTimer	= setInterval( allRegLoad, 200 );
}

function stopReload() {
	clearInterval( intervalTimer );
}

let reg_list	= {};

function getRegList() {
	let url	= REQ_HEADER + 'reglist'
	
	ajaxUpdate( url, function (){
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
