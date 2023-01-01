const	getTimeAndShow	= (function () {
	let prev_reg	= [];	//	to prevent refresh on user writing field
	let prev_alarm	= [];	//	to prevent refresh on user writing field
	let prev_alarm_flg	= false;	//	to prevent error of retrying open the dialog

	return function() {
		function done() {
			let obj = JSON.parse( this.responseText );

			let elem = document.getElementById( "datetime" );
			elem.innerText = obj.datetime.str;
			//console.log( obj.ts );
			if ( obj.ts ) {
				let elem = document.getElementById( "timestamp" );
				elem.innerText = obj.ts;
			}

			for ( let i = 0; i < 5; i++ ) {
				let value	= obj.alarm[ i ];
				if ( value != prev_alarm[ i ] ) {
					document.getElementById( "alarmField" + i ).value	= ( value == 0x80 ) ? '--' : hex( value );
				}
			}
			prev_alarm	= obj.alarm;
									
			for ( let i = 0; i < obj.reg.length; i++ ) {
				let value	= obj.reg[ i ];
				if ( value != prev_reg[ i ] ) {
					document.getElementById('regField' + i ).value	= hex( value );
				}
			}
			prev_reg	= obj.reg;
			
			if ( obj.alarm_flg ) {
				document.getElementById( 'dialog' ).showModal();
				prev_alarm_flg	= true;
				
				if ( sound )
					sound.play();
				else
					console.log( 'Sound is not played' );
			}
		}

		let url	= REQ_HEADER;
		ajaxUpdate( url, done );
	}
})();


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
	ajaxUpdate( url, () => {
		obj = JSON.parse( this.responseText );		
		document.getElementById('regField' + obj.reg ).value	= hex( obj.val );
	} )
}

window.addEventListener('load', function () {
	setInterval( getTimeAndShow, 1000 );
});
