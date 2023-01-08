/****************************
 ****	service routine
 ****************************/
 

/******** ajaxUpdate ********/

function ajaxUpdate( url, func ) {
	url			= url + '?ver=' + new Date().getTime();
	
	fetch( url )
		.then( response => {
		/*
			console.log( "response.ok = " + response.ok )
			console.log( "response.headers = " + response.ok )
			console.log( "Content-Type = " + response.headers.get( "Content-Type" ) )
		 */
			return response.text();
		} )
		.then( function ( data ) {
			if ( typeof func === "undefined" )
				;	//	do nothing
			else
				func( data );
		} );
}

function ajaxUpdate__OLD( url, func ) {
	url			= url + '?ver=' + new Date().getTime();
	let	ajax	= new XMLHttpRequest;
	ajax.open( 'GET', url, false );
	ajax.onload = func;
	ajax.send( null );
}

function hex( num ) {
	return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 );
}


