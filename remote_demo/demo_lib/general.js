/****************************
 ****	service routine
 ****************************/
 

/******** ajaxUpdate ********/

function ajaxUpdateTrials( url, func, retry = 3 ) {
	while ( retry-- ) {
		let	errorFlag	= false;
		try {
			console.log( 'trying;' + retry );
			ajaxHandling( url, func );		
		} catch ( e ) {
			console.log( e );
			errorFlag	= true;
		} finally {
			if ( !errorFlag )
				retry	= 0;
		}
	}
}

function ajaxUpdate( url, func ) {
	url			= url + '?ver=' + new Date().getTime();
	let	ajax	= new XMLHttpRequest;
	ajax.open( 'GET', url, false );
	ajax.onload = func;
	ajax.send( null );
}

function hex( num ) {
	return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 );
}


