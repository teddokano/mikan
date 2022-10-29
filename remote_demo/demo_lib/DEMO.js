const	DEV_NAME	= '{% dev_name %}';
const	REQ_HEADER	= '/' + DEV_NAME + '?';

/****************************
 ****	service routine
 ****************************/
 
/******** ajaxUpdate ********/

function ajaxUpdate( url, func ) {
	url			= url + '?ver=' + new Date().getTime();
	let	ajax	= new XMLHttpRequest;
	ajax.open( 'GET', url, true );
	
	ajax.onload = func;
	ajax.send( null );
}

function hex( num ) {
	return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 );
}

function busReset( flag ) {
		let url;

		url	= REQ_HEADER + ((flag == 0) ? 'reset' : 'reprogram')
		ajaxUpdate( url );
}
