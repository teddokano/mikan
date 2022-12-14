function busReset( flag ) {
	let url;

	url	= REQ_HEADER + ((flag == 0) ? 'reset' : 'reprogram')
	ajaxUpdate( url );
}

function allLinkOpen( list ) {
	
	const	WINDOW_WIDTH_MIN	= 800;
	const	WINDOW_HEIGHT_MIN	= 1000;
	const	count	= list.length;
	const	n_col	= parseInt( window.screen.width / WINDOW_WIDTH_MIN );
	const	n_row	= parseInt( (count + (n_col - 1)) / n_col );

	let		left_ofst	= window.screen.width / n_col;
	let		top_ofst	= window.screen.height / n_row;

	width	= (left_ofst < WINDOW_WIDTH_MIN ) ? WINDOW_WIDTH_MIN  : left_ofst;
	//height	= (top_ofst  < WINDOW_HEIGHT_MIN) ? WINDOW_HEIGHT_MIN : top_ofst;
	height	= top_ofst;
	
	list.forEach( ( url, i ) => {
		let index	= (i % n_row) * n_col + parseInt(i / n_row);
		window.open(	url, 
						url, 
						'width=' + width 
							+ ',height=' + height 
							+ ',left=' + left_ofst * (index % parseInt((count + (n_row - 1)) / n_row)) 
							+ ',top=' + top_ofst * parseInt(index / parseInt((count + (n_row - 1)) / n_row))
					);
	});
}
