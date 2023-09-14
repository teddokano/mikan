class GraphDraw {
	constructor( obj ) {
		this.id		= obj.id;
		this.ctx	= document.getElementById( this.id );		
		this.cs		= obj.setting;
		this.data_s	= [];
		
		this.time	= this.cs.data.labels;

		for ( const ds of this.cs.data.datasets ) {
			this.data_s.push( ds.data );
		}
	}

	push( data ) {	
		this.time.push( data.time );
		
		for ( const [ series, ds ] of zip( this.data_s, this.cs.data.datasets ) ) {
			series.push( data[ this.id + ds.label ] );
		}
		
		if ( 100 < this.time.length ) {
			this.cs.data.labels.shift();
			
			for ( const ds of this.cs.data.datasets ) {
				ds.data.shift();
			}			
		}
	}
	
	update_tables() {
		for ( let i = 0; i < TABLE_LEN; i++ )
		{
			document.getElementById( this.id + "timeField" + i ).value = this.time.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
			
			for ( const [ series, ds ] of zip( this.data_s, this.cs.data.datasets ) ) {
				let v	= series.slice( -TABLE_LEN )[ TABLE_LEN - i - 1 ];
				v		= isNaN( v ) ? v : v.toFixed( 6 );
				document.getElementById( this.id + ds.label + "Field" + i ).value = v;				
			}
		}

		document.getElementById( "infoFieldValue0" ).value = this.time[ 0 ];
		document.getElementById( "infoFieldValue1" ).value = this.time[ this.time.length - 1 ];
		document.getElementById( "infoFieldValue2" ).value = this.time.length;
	}

	draw() {
		if ( this.chart )
			this.chart.destroy();

		this.chart = new Chart( this.ctx, this.cs );
	}

	save() {
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
		link.download	= DEV_NAME + this.id + "_measurement_result " + now.toString() + ".csv";
		link.click();
		URL.revokeObjectURL( link.href );
	}
	
	get_last_data() {
		let data	= [];
		
		for ( const ds of this.cs.data.datasets ) {
			data.push( ds.data.slice( -1 )[ 0 ] );
		}			
		return data[ 0 ];
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
			for ( const g of graph ) {
				g.push( data );
			}
		} );
		
		for ( const g of graph ) {
			g.draw();
			g.update_tables();
		}
		
		gauge[ 0 ].refresh( graph[ 0 ].get_last_data() );
		gauge[ 1 ].refresh( graph[ 1 ].get_last_data() );
	} );
}

window.addEventListener( 'load', function () {
	set_gauge();
	initial_data_loading();
	document.getElementById( 'dialog' ).showModal();
	
	setTimeout( () => { 
		document.getElementById( 'dialog' ).close();
		setInterval( getDataAndShow, 200 ); 
	}, 3000 );
});

let graph	= [];
let gauge	= [];

function set_gauge() {
	ajaxUpdate( REQ_HEADER + "start_setting", data => {
		let obj = JSON.parse( data );

		set_gauge_params( obj.scales );
	} );
}

function set_gauge_params( os ) {
	let setting	= [
		{
		id: 'gaugeX', 
		label: 'Temperature',
		color: '#ff0000',
		value: 0,
		min: os[ 0 ].min,
		max: os[ 0 ].max,
		decimals: 1,
		symbol: '℃',
		pointer: true,
		gaugeWidthScale: 0.5,
		customSectors: {
			percents: true,
			ranges: [
				{
					color : "#0000FF",
					lo : 0,
					hi : 50
				},
				{
					color : "#FF0000",
					lo : 51,
					hi : 100
				},
			]
		},
		counter: false
	},
	{
		id: 'gaugeY', 
		label: 'Weight',
		color: '#00ff00',
		value: 0,
		min: os[ 1 ].min,
		max: os[ 1 ].max,
		decimals: 1,
		symbol: 'g',
		pointer: true,
		gaugeWidthScale: 0.5,
		customSectors: {
			percents: true,
			ranges: [
				{
					color : "#0000FF",
					lo : 0,
					hi : 50
				},
				{
					color : "#FF0000",
					lo : 51,
					hi : 100
				},
			]
		},
		counter: false
	}];
	
	for ( const s of setting ) {
		gauge.push( new JustGage( JSON.parse( JSON.stringify( s ) ) ) );		
	}
}

function initial_data_loading() {
	ajaxUpdate( REQ_HEADER + "settings", data => {
		let obj = JSON.parse( data );

		for ( const o of obj ) {
			graph.push( new GraphDraw( o ) );
		}
	} );
}
