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

	getAndShow() {		
		let url		= REQ_HEADER + "update=1";

		ajaxUpdate( url, data => {
			let obj = JSON.parse( data );

			obj.forEach( data => {
				this.time.push( data.time );
				this.x.push( data.x );
				this.y.push( data.y );
				this.z.push( data.z );
			});

			if ( 100 < time.length ) {
				this.cs.data.labels.shift();
				this.cs.data.datasets[0].data.shift();
				this.cs.data.datasets[1].data.shift();
				this.cs.data.datasets[2].data.shift();
			}
 
			this.draw();

			for ( let i = 0; i < TABLE_LEN; i++ )
			{
				document.getElementById( "timeField" + i ).value = time.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				
				let	xv	= x.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				let	yv	= y.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				let	zv	= z.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				
				xv	= isNaN( xv ) ? x : xv.toFixed( 6 );
				yv	= isNaN( yv ) ? y : yv.toFixed( 6 );
				zv	= isNaN( yv ) ? z : zv.toFixed( 6 );
					
				document.getElementById( "xField" + i ).value = xv;
				document.getElementById( "yField" + i ).value = yv;
				document.getElementById( "zField" + i ).value = zv;
			}

			document.getElementById( "infoFieldValue0" ).value = time[ 0 ];
			document.getElementById( "infoFieldValue1" ).value = time[ time.length - 1 ];
			document.getElementById( "infoFieldValue2" ).value = time.length;
		} );
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
			document.getElementById( "timeField" + i ).value = this.time.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			
			let	xv	= this.x.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			let	yv	= this.y.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			let	zv	= this.z.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			
			xv	= isNaN( xv ) ? xv : xv.toFixed( 6 );
			yv	= isNaN( yv ) ? yv : yv.toFixed( 6 );
			zv	= isNaN( yv ) ? zv : zv.toFixed( 6 );
				
			document.getElementById( "xField" + i ).value = xv;
			document.getElementById( "yField" + i ).value = yv;
			document.getElementById( "zField" + i ).value = zv;
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
	accGraph.save();
	magGraph.save();
}

function getTempAndShow() {
	let url		= REQ_HEADER + "update=1";
	
	ajaxUpdate( url, data => {
		let obj = JSON.parse( data );

		obj.forEach( data => {
			accGraph.push( data.time, { x:data.x, y:data.y, z:data.z } );
			magGraph.push( data.time, { x:data.mx, y:data.my, z:data.mz } );
		} );
		accGraph.draw();
		accGraph.update_tables();
		magGraph.draw();
	} );
}

window.addEventListener( 'load', function () {
	setInterval( getTempAndShow, 200 );
});

let	acc	= {
	type: 'line',
	data: {
		labels: [],
		datasets: [
			{
				label: 'x',
				data: [],
				borderColor: "rgba( 255, 0, 0, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
			{
				label: 'y',
				data: [],
				borderColor: "rgba( 0, 255, 0, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
			{
				label: 'z',
				data: [],
				borderColor: "rgba( 0, 0, 255, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
		],
	},
	options: {
		animation: false,
		title: {
			display: true,
			text: '"g" now'
		},
		scales: {
			yAxes: [{
				ticks: {
					suggestedMax: 2.0,
					suggestedMin: -2.0,
					stepSize: 1,
					callback: function(value, index, values){
					return  value +  ' g'
					}
				},
				scaleLabel: {
					display: true,
					labelString: ' ]gravitational acceleration [g]'
				}
			}],
			xAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'time'
				}
			}]
		},
	}
};

let	mag	= {
	type: 'line',
	data: {
		labels: [],
		datasets: [
			{
				label: 'x',
				data: [],
				borderColor: "rgba( 255, 0, 0, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
			{
				label: 'y',
				data: [],
				borderColor: "rgba( 0, 255, 0, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
			{
				label: 'z',
				data: [],
				borderColor: "rgba( 0, 0, 255, 1 )",
				backgroundColor: "rgba( 0, 0, 0, 0 )"
			},
		],
	},
	options: {
		animation: false,
		title: {
			display: true,
			text: '"mag" now'
		},
		scales: {
			yAxes: [{
				ticks: {
					//suggestedMax: 2.0,
					//suggestedMin: -2.0,
					//stepSize: 1,
					callback: function(value, index, values){
					return  value +  ' nT'
					}
				},
				scaleLabel: {
					display: true,
					labelString: 'geomagnetism [nT]'
				}
			}],
			xAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'time'
				}
			}]
		},
	}
};

accGraph	= new GraphDraw( "Chart0", acc );
magGraph	= new GraphDraw( "Chart1", mag );
