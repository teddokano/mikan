let reqCount	= 0;

function ajaxUpdate( url, func, timeout = 5000 ) {
	url			= url + '?ver=' + new Date().getTime();
	
	if ( (timeout < 1000) && reqCount )
			return;	//	ignore since this is low priority request (avoid to disturb server response time)
		
	reqCount++;
	
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
			if ( reqCount )
				reqCount--;
		} )
		.catch( ( error ) => {
			if ( reqCount )
				reqCount--;
			console.log( 'ajaxUpdate - fetch timeout ' + error )
		} );
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

async function responseTime( url, n = 10 ) {
	let	resp	= {	raw: [] };
	resp.total	= 0;
	
	for ( let i = 0; i < n; i++ ) {
		let start	= performance.now();
		await new Promise( (resolve, reject) => { ajaxUpdate( url, () => resolve(), 1000 ) } )
		let e_time	= performance.now() - start;
		resp.raw.push( e_time );
		resp.total	+= e_time;
	}
	
	resp.raw.sort( (a, b) => (a - b) );
	resp.median	= resp.raw[ Math.trunc(n / 2) ];
	resp.max	= Math.max( ...(resp.raw) );
	resp.min	= Math.min( ...(resp.raw) );
	resp.avg	= resp.total / resp.raw.length;
	
	return resp;
}

function showResponseTimeResult( resp ) {
	console.log( 'measured server response ---' );
	console.log( resp );
}

function measureServerResponse( message, func ) {
	let url	= REQ_HEADER + message;
	let	resp;
	
	responseTime( url )
		.then( ( resp ) => { 
			showResponseTimeResult( resp );		

			func && func( resp );
	} );
}


const zip = ( a1, a2 ) => a1.map( ( _, i ) => [ a1[ i ], a2[ i ] ] );
