class GraphDraw {
	constructor( id, cs ) {
		this.id		= id;
		this.cs		= cs;
		this.chart	= undefined;
		
		this.time	= this.cs.data.labels;
		this.x		= this.cs.data.datasets[0].data;
		this.y		= this.cs.data.datasets[1].data;
		this.z		= this.cs.data.datasets[2].data;
	}

	push( t, xyz ) {		
		this.time.push( t );
		this.x.push( xyz.x );
		this.y.push( xyz.y );
		this.z.push( xyz.z );

		if ( 100 < this.time.length ) {
			this.cs.data.labels.shift();
			this.cs.data.datasets[0].data.shift();
			this.cs.data.datasets[1].data.shift();
			this.cs.data.datasets[2].data.shift();
		}
	}
	
	update_tables() {
		for ( let i = 0; i < TABLE_LEN; i++ )
		{
			document.getElementById( this.id + "timeField" + i ).value = this.time.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			
			let	xv	= this.x.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			let	yv	= this.y.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			let	zv	= this.z.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			
			xv	= isNaN( xv ) ? xv : xv.toFixed( 6 );
			yv	= isNaN( yv ) ? yv : yv.toFixed( 6 );
			zv	= isNaN( yv ) ? zv : zv.toFixed( 6 );
				
			document.getElementById( this.id + "xField" + i ).value = xv;
			document.getElementById( this.id + "yField" + i ).value = yv;
			document.getElementById( this.id + "zField" + i ).value = zv;
		}

		document.getElementById( "infoFieldValue0" ).value = this.time[ 0 ];
		document.getElementById( "infoFieldValue1" ).value = this.time[ this.time.length - 1 ];
		document.getElementById( "infoFieldValue2" ).value = this.time.length;
	}

	draw() {
		let	ctx = document.getElementById( this.id );
		
		if ( this.chart )
			this.chart.destroy();

		this.chart = new Chart( ctx, this.cs );
	}

	save() {
		console.log( 'csvFileOut' );
		let str	= [];
		let	len	= this.time.length;
		  
		str	+= "time,x,y,z\n";
		for ( let i = 0; i < len; i++ ) {
			str	+= this.time[ i ] + "," +  this.x[ i ] + "," + this.y[ i ] + "," + this.z[ i ] + "\n";
		}

		let now		= new Date()
		let blob	= new Blob( [str], {type:"text/csv"} );
		let link	= document.createElement( 'a' );
		link.href	= URL.createObjectURL( blob );
		link.download	= DEV_NAME + this.id + "_measurement_result" + now.toString() + ".csv";
		link.click();
	}
}

function csvFileOut() {
	for ( const g of graph ) {
		g.save();

	}
}

function getDataAndShow() {
	let url		= REQ_HEADER + "update=1";
	
	ajaxUpdate( url, data => {
		let obj = JSON.parse( data );

		obj.forEach( data => {
			graph[ 0 ].push( data.time, { x:data.x, y:data.y, z:data.z } );
			graph[ 1 ].push( data.time, { x:data.mx, y:data.my, z:data.mz } );
		} );
		
		for ( const g of graph ) {
			g.draw();
			g.update_tables();
		}
	} );
}

window.addEventListener( 'load', function () {
	setInterval( getDataAndShow, 200 );
});

let graph	= [];

ajaxUpdate( REQ_HEADER + "settings", data => {
	let obj = JSON.parse( data );

	graph.push( new GraphDraw( SPLIT[ 0 ], obj[ 0 ] ) );
	graph.push( new GraphDraw( SPLIT[ 1 ], obj[ 1 ] ) );
} );


