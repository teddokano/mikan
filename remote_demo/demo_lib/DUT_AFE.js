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
	setInterval( getDataAndShow, 200 );
});

let graph	= [];
let gauge	= [];

function set_gauge() {
	let setting	= [
		{
		id: 'gaugeX', 
		label: 'Temperature',
		color: '#ff0000',
		value: 0,
		min: 20,
		max: 35,
		decimals: 1,
		symbol: '℃',
		pointer: true,
		gaugeWidthScale: 0.5,
		customSectors: [
			{
				lo: 25,
				hi: 30
			}
		],
		counter: false
	},
	{
		id: 'gaugeY', 
		label: 'Weight',
		color: '#00ff00',
		value: 0,
		min: -10,
		max: 1200,
		decimals: 1,
		symbol: 'g',
		pointer: true,
		gaugeWidthScale: 0.5,
		customSectors: [
			{
				lo: 250,
				hi: 750
			}
		],
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
		
		init3D();
	} );
}

function init3D() {
	const	width	= 480;
	const	height	= 320;

	const renderer	= new THREE.WebGLRenderer({
		canvas: document.querySelector( "#myCanvas" )
	});
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( width, height );

	const scene	= new THREE.Scene();

	const camera	= new THREE.PerspectiveCamera( 45, width / height );
	camera.position.set( 0, 0, 500);
//	const controls = new THREE.OrbitControls( camera, document.body );
	
	let boxes;
	
	if ( graph.length == 1 )
		boxes	= board_ARD();
	else
		boxes	= board_RT();
	
	scene.add( boxes );
	const ambient	= new THREE.AmbientLight( 0xFFFFFF, 0.2 );
	scene.add( ambient );
	//const hemi	= new THREE.HemisphereLight( 0x0000FF, 0xFF0000, 0.5 );
	//scene.add( hemi );
	const light	= new THREE.DirectionalLight( 0xFFFFFF, 1.0 );
	light.position.set( -1, 1, 1 );
	scene.add( light );
	tick();

	function tick() {
		//box.rotation.x += 0.01;
		//box.rotation.y += 0.01;
		//box.rotation.z += 0.01;
		
		let  x,  y,  z;
		let mx, my, mz;
		
		if ( graph[ 0 ] ) {
			[ x, y, z ]	= graph[ 0 ].get_last_data();
		}
			
		if ( graph[ 1 ] ) {
			[ mx, my, mz ]	= graph[ 1 ].get_last_data();
		}
		
		boxes.rotation.x	= Math.atan2( -y, z );
		boxes.rotation.y	= Math.atan2(  x, (y * y + z * z ) ** 0.5 );
		
		let xx	= (boxes.rotation.x / Math.PI) * 180 % 360;
		let yy	= (boxes.rotation.y / Math.PI) * 180 % 360;
//		console.log( xx.toFixed( 0 ), yy.toFixed( 0 ) );

		renderer.render( scene, camera );

		requestAnimationFrame( tick );
	}
}


function board_RT() {
	let box0 = new THREE.Mesh(
		new THREE.BoxGeometry( 300, 200, 10 ), 
		new THREE.MeshLambertMaterial({color: 0x33FF33})
	);
	let box1 = new THREE.Mesh(
		new THREE.BoxGeometry(  30,  50, 25 ),
		new THREE.MeshPhongMaterial({color: 0xC0C0C0})
	);
	let box2 = new THREE.Mesh(
		new THREE.BoxGeometry( 100, 100, 10 ),
		new THREE.MeshLambertMaterial({color: 0x33EE33})
	);
	let box3 = new THREE.Mesh(
		new THREE.BoxGeometry( 6, 6, 3 ),
		new THREE.MeshLambertMaterial({color: 0x404040})
	);
	let box4 = new THREE.Mesh(
		new THREE.BoxGeometry( 50, 6, 16 ),
		new THREE.MeshLambertMaterial({color: 0x808080})
	);

	let box5 = new THREE.Mesh(
		new THREE.BoxGeometry( 50, 6, 16 ),
		new THREE.MeshLambertMaterial({color: 0x808080})
	);

	let box6 = new THREE.Mesh(
		new THREE.BoxGeometry( 40, 6, 16 ),
		new THREE.MeshLambertMaterial({color: 0x808080})
	);

	let box7 = new THREE.Mesh(
		new THREE.BoxGeometry( 30, 6, 16 ),
		new THREE.MeshLambertMaterial({color: 0x808080})
	);
	box0.position.set(    0,  0, -10 );
	box1.position.set(  70, -80,   8 );
	box2.position.set( -100,  0,  15 );

	box0.position.set(  30,  -45, -10 );
	box1.position.set( 100, -125,   8 );
	box2.position.set( -60,  -45,  15 );
	box3.position.set(   0,    0,   2 );
	box4.position.set( -88,    6,   5 );
	box5.position.set( -35,    6,   5 );
	box6.position.set( -80,  -95,   5 );
	box7.position.set( -35,  -95,   5 );
	
	let boxes = new THREE.Group();
	boxes.add( box0 );
	boxes.add( box1 );
//  boxes.add( box2 );
	boxes.add( box3 );
	boxes.add( box4 );
	boxes.add( box5 );
	boxes.add( box6 );
	boxes.add( box7 );

	return boxes;
}

function board_ARD() {
	let box0 = new THREE.Mesh(
								new THREE.BoxGeometry( 250, 280, 10 ), 
								new THREE.MeshLambertMaterial({color: 0xFF8000})
							);
	let box1 = new THREE.Mesh(
								new THREE.BoxGeometry(  10, 100, 40 ),
								new THREE.MeshLambertMaterial({color: 0x808080})
							);
	let box2 = new THREE.Mesh(
								new THREE.BoxGeometry(  10,  75, 40 ),
								new THREE.MeshLambertMaterial({color: 0x808080})
							);
	let box3 = new THREE.Mesh(
								new THREE.BoxGeometry(  10, 125, 40 ),
								new THREE.MeshLambertMaterial({color: 0x808080})
							);
	let box4 = new THREE.Mesh(
								new THREE.BoxGeometry(  10, 125, 40 ),
								new THREE.MeshLambertMaterial({color: 0x808080})
							);
	let box5 = new THREE.Mesh(
								new THREE.BoxGeometry( 10, 10, 5 ), 
								new THREE.MeshLambertMaterial({color: 0x404040})
							  );
	let box6 = new THREE.Mesh(
								  new THREE.BoxGeometry( 25, 10, 30 ), 
								  new THREE.MeshLambertMaterial({color: 0x808080})
								);
	let box7 = new THREE.Mesh(
								  new THREE.BoxGeometry( 25, 10, 30 ), 
								  new THREE.MeshLambertMaterial({color: 0x808080})
								);
	let box8 = new THREE.Mesh(
								  new THREE.BoxGeometry( 25, 10, 30 ), 
								  new THREE.MeshLambertMaterial({color: 0x808080})
							  );
	box0.position.set(    0,   0,  0 );
	box1.position.set(  110, -25, 20 );
	box2.position.set(  110,  75, 20 );
	box3.position.set( -110, -60, 20 );
	box4.position.set( -110,  70, 20 );
	box5.position.set(    0,   0,  5 );
	box6.position.set(   65,  65, 20 );
	box7.position.set(   65,  90, 20 );
	box8.position.set(   65, 115, 20 );

	let boxes = new THREE.Group();
	boxes.add( box0 );
	boxes.add( box1 );
	boxes.add( box2 );
	boxes.add( box3 );
	boxes.add( box4 );
	boxes.add( box5 );
	boxes.add( box6 );
	boxes.add( box7 );
	boxes.add( box8 );

	return boxes;
}
