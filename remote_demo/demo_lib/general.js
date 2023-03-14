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
	
	for ( let i = 0; i < n; i++ ) {
		let start	= performance.now();
		await new Promise( (resolve, reject) => { ajaxUpdate( url, () => resolve(), 1000 ) } )
		resp.raw.push( performance.now() - start );
	}
	
	resp.raw.sort( (a, b) => (a - b) );
	resp.median	= resp.raw[ Math.trunc(n / 2) ];
	resp.max	= Math.max( ...(resp.raw) );
	resp.min	= Math.min( ...(resp.raw) );
	
	return resp;
}

function showResponseTimeResult( resp ) {
	console.log( 'measured server response ---' );
	console.log( resp );
}

const zip = ( a1, a2 ) => a1.map( ( _, i ) => [ a1[ i ], a2[ i ] ] );
