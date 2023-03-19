class GraphDraw {
	constructor( obj ) {
		this.id		= obj.id;
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
		let	ctx = document.getElementById( this.id );
		
		if ( this.chart )
			this.chart.destroy();

		this.chart = new Chart( ctx, this.cs );
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
	} );
}

window.addEventListener( 'load', function () {
	init3D();
	setInterval( getDataAndShow, 200 );
});

let graph	= [];

ajaxUpdate( REQ_HEADER + "settings", data => {
	let obj = JSON.parse( data );

	for ( const o of obj ) {
		graph.push( new GraphDraw( o ) );
	}
} );


function init3D() {
	const	width	= 960;
	const	height	= 540;

	const renderer	= new THREE.WebGLRenderer({
		canvas: document.querySelector( "#myCanvas" )
	});
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( width, height );

	const scene	= new THREE.Scene();

	const camera	= new THREE.PerspectiveCamera( 45, width / height );
	camera.position.set( 0, 0, +1000 );

	const geometry	= new THREE.BoxGeometry( 400, 400, 40 );
	const material	= new THREE.MeshNormalMaterial();
	const box		= new THREE.Mesh( geometry, material );
	scene.add( box );

	tick();

	function tick() {
		//box.rotation.x += 0.01;
		box.rotation.y += 0.01;
		//box.rotation.z += 0.01;

		renderer.render( scene, camera ); // レンダリング

		requestAnimationFrame( tick );
	}
}

//window.addEventListener( 'DOMContentLoaded', init3D );
