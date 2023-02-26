/****************************
 ****	service routine
 ****************************/
 
function ajaxUpdate( url, func, timeout = 5000 ) {
	url			= url + '?ver=' + new Date().getTime();
	
	fetch( url, { signal: AbortSignal.timeout( timeout ) } )
		.then( response => {
		/*
			console.log( "response.ok = " + response.ok )
			console.log( "response.headers = " + response.ok )
			console.log( "Content-Type = " + response.headers.get( "Content-Type" ) )
		 */
			return response.text();
		} )
		.then( ( data ) => {
			func && func( data );
		} )
		.catch( ( error ) => console.log( 'ajaxUpdate - fetch timeout ' + error ) );
}

function hex( num ) {
	return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 );
}

function highlight( elem, duration = 1000 ) {
	elem.style.border = "solid 1px #FF0000";
	setTimeout( e => {
		e.style.border = "solid 1px #FFFFFF";
	}, duration, elem )	
}
