function busReset( flag ) {
		let url;

		url	= REQ_HEADER + ((flag == 0) ? 'reset' : 'reprogram')
		ajaxUpdate( url );
}
