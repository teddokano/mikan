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
	
	get_last_data() {
		let data	= [];
		
		for ( const ds of this.cs.data.datasets ) {
			data.push( ds.data.slice( -1 )[ 0 ] );
		}			

		return data;
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
	camera.position.set( 0, 0, 500);

	let box0 = new THREE.Mesh(
								  new THREE.BoxGeometry( 300, 200, 20 ), 
								  new THREE.MeshLambertMaterial({color: 0x33FF33})
								);
	let box1 = new THREE.Mesh(
								  new THREE.BoxGeometry(  30,  50, 25 ),
								  new THREE.MeshPhongMaterial({color: 0xC0C0C0})
								);
	let box2 = new THREE.Mesh(
								  new THREE.BoxGeometry( 100, 100, 20 ),
								  new THREE.MeshLambertMaterial({color: 0x33EE33})
								);

	box0.position.set(    0,  0,  0 );
	box1.position.set(  70, -80, 25 );
	box2.position.set( -100,  0, 25 );

	let boxes = new THREE.Group();
	boxes.add(box0);
	boxes.add(box1);
	boxes.add(box2);
	scene.add( boxes );
	const ambient	= new THREE.AmbientLight( 0xFFFFFF, 0.2 );
	scene.add( ambient );
//	  const hemi	= new THREE.HemisphereLight( 0x0000FF, 0xFF0000, 0.2 );
//	  scene.add( hemi );
	const light	= new THREE.DirectionalLight( 0xFFFFFF, 1.0 );
	light.position.set( -1, 1, 1 );
	scene.add( light );
	tick();

	function tick() {
		//box.rotation.x += 0.01;
		//box.rotation.y += 0.01;
		//box.rotation.z += 0.01;
		
		let x, y, z;
		
		if ( graph[ 0 ] ) {
			[ x, y, z ]	= graph[ 0 ].get_last_data();
		}
		
		if ( 0 < z ) {
			console.log( '+ ' + x + ', ' + y );
			boxes.rotation.x	= Math.atan2( -y, z );
			boxes.rotation.y	= Math.atan2(  x, z );
		} else {
			console.log( '- ' + x + ', ' + y );
			boxes.rotation.x	= Math.atan2( -y, -z ) + Math.PI;
			boxes.rotation.y	= Math.atan2(  x, -z ) + Math.PI;
		}			
//		console.log( boxes.rotation.x, boxes.rotation.y );
//		box.rotation.z	= Math.asin( z / 1 );
		boxes.rotation.z	= 0;

		renderer.render( scene, camera );

		requestAnimationFrame( tick );
	}
}

//window.addEventListener( 'DOMContentLoaded', init3D );
