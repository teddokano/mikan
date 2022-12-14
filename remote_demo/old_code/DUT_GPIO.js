/****************************
 ****	register controls
 ****************************/
 
/******** updateRegField ********/

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

	let url	= REQ_HEADER + "reg=" + idx + "&val=" + value;
	ajaxUpdate( url )
}

function allRegLoad() {
	let url	= REQ_HEADER + 'allreg='
	ajaxUpdate( url, allRegLoadDone );
}

function allRegLoadDone() {
	let obj = JSON.parse( this.responseText );

	for ( let i = 0; i < obj.reg.length; i++ ) {
		document.getElementById('regField' + i ).value	= hex( obj.reg[ i ] );
	}
}

window.addEventListener('load', function () {
	allRegLoad();
});
