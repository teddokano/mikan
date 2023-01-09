/****************************
 ****	service routine
 ****************************/
 
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
		.then( ( data ) => {
			func && func( data );
		} );
}

function hex( num ) {
	return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 );
}


