function busReset( flag ) {
	let url;

	url	= REQ_HEADER + ((flag == 0) ? 'reset' : 'reprogram')
	ajaxUpdate( url );
}

function allLinkOpen( list ) {
	s_w	= window.screen.width;
	s_h	= window.screen.height;
	count	= list.length;
	width	= window.screen.width / (count / 2);
	height	= s_h / 2;
	
	console.log( 'window.screen.width  ' + window.screen.width );
	console.log( 'window.screen.height ' + window.screen.height );

//	for ( let url of list ) {
	list.forEach( ( url, i ) => {
		window.open( url, url, 'width=' + width + ',height=' + height + ',left=' + width * (i % parseInt(count / 2)) + ',top=' + height * parseInt(i / (count / 2)) );
	});
}
