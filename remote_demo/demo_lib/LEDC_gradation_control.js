class GradationFunc	{
	constructor( setting ) {
		if ( 0 < setting.rtime ) {
			let iref	= setting.iref * 255;	
			let time	= setting.rtime * 1000;
			
			let step_duration	= time / iref;

			if ( 32 < step_duration )
				this.cycle_time	= 8;
			else
				this.cycle_time	= 0.5;
				
			this.multi_fctr	= parseInt( step_duration / this.cycle_time );
			this.multi_fctr	= (this.multi_fctr <   1) ? 1 : this.multi_fctr;
			this.multi_fctr	= (64 < this.multi_fctr) ? 64 : this.multi_fctr;
			
			if ( 1 == this.multi_fctr )
				this.iref_inc	= parseInt( iref / (time / this.cycle_time) )
			else
				this.iref_inc	= 1

			this.ramp_time	= ((this.multi_fctr * this.cycle_time ) * (iref / this.iref_inc)) / 1000
		}
		
		this.iref		= setting.iref;
		this.t_ramp_up	= setting.up ? this.ramp_time : 0;
		this.t_hold_on	= this.t_ramp_up + setting.h_on;
		this.t_ramp_dn	= this.t_hold_on + (setting.down ? this.ramp_time : 0);
		this.t_cycle	= this.t_ramp_dn + setting.h_off;
		this.values		= [];
		this.reg		= [];
																	   
		let h	= { 0: 0, 0.25: 1, 0.5: 2, 0.75: 3, 1: 4, 2: 5, 4: 6, 6: 7 };
		this.reg[ 0 ]	= (setting.up << 7) | (setting.down << 6) | (this.iref_inc - 1);
		this.reg[ 1 ]	= ((setting.cycle_time == 8) ? 0x40 : 0x00) | (this.multi_fctr - 1);
		this.reg[ 2 ]	= 0xC0 | (h[ setting.h_on ] << 3) | h[ setting.h_off ]; 
		this.reg[ 3 ]	= parseInt( setting.iref * 255.0 ); 
	}
	
	getCurve( time ) {
		let	t;
		let	v;
		time	%= this.t_cycle;
		
		if ( time < this.t_ramp_up ) {
			t	= time - 0;
			v	= this.iref * (t / this.ramp_time);
		}
		else if ( time < this.t_hold_on ) {
			v	= this.iref;
		}
		else if ( time < this.t_ramp_dn ) {
			t	= time - this.t_hold_on;
			v	= this.iref * (1 - (t / this.ramp_time));
		}
		else {
			v	= 0;
		}
		this.values.push( v );
	}
}


const	TABLE_LEN	= 10
const	GRAPH_HIGH	= 1
const	GRAPH_LOW	= 0

function drawChart( time, g ) {
	var ctx = document.getElementById("myLineChart");
	window.myLineChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: time,
			datasets: [
					   {
						   label: 'group0',
						   data: g[ 0 ].values,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 0, 0, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group1',
						   data: g[ 1 ].values,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 115, 78, 48, 0.5 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group2',
					       data: g[ 2 ].values,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 255, 0, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group3',
					       data: g[ 3 ].values,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 237, 109, 53, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group4',
					       data: g[ 4 ].values,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 255, 190, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group5',
					       data: g[ 5 ].values,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 0, 255, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   ],
		},
		options: {
			animation: false,
			title: {
				display: true,
				text: 'gradation curves'
			},
			scales: {
				yAxes: [{
					ticks: {
						suggestedMax: GRAPH_HIGH,
						suggestedMin: GRAPH_LOW,
						stepSize: 0.1,
						callback: function(value, index, values){
							return  value +  ''
						}
					},
					scaleLabel: {
						display: true,
						labelString: 'current ratio'
					}
				}],
				xAxes: [{
					scaleLabel: {
						display: true,
						labelString: 'time [second]'
					}
				}]
			},
		}
	});
}

window.addEventListener( 'load', function () {				
	updatePlot();
});

function updatePlot() {
	let time_base	= [];
	let t_max		= 0;				
	let setting		= {};
	let	gradation_groups	= [];
				
	for ( let i = 0; i < 6; i++ ) {					
		setting.iref	= parseFloat( document.getElementById( 'maxCurrent'    + i ).value );
		setting.rtime	= parseFloat( document.getElementById( 'rampTimeField' + i ).value );
		setting.h_on	= parseFloat( document.getElementById( 'holdON'        + i ).value );
		setting.h_off	= parseFloat( document.getElementById( 'holdOFF'       + i ).value );
		setting.up		= document.getElementById( 'rampSwUp'      + i ).checked;
		setting.down	= document.getElementById( 'rampSwDown'    + i ).checked;
		setting.phase	= document.getElementById( 'phase'         + i ).value;
		
		gradation_groups[ i ]	= new GradationFunc( setting );
	}
			
	/*
	gradation_groups.forEach( function( g, i ) {
		g.reg.forEach( function( v, j ) {
			console.log( i + ' ' + j + ' ' + hex( v ) );
		});		
	});		
	*/

	for ( let g of gradation_groups ){
		t_max	= (t_max < g.t_cycle) ? g.t_cycle : t_max;
	}
	
	let resoution	= 1000
	for ( let i = 0; i <= t_max * resoution; i ++ ) {
		time_base.push( i / resoution );
	}
	
	for ( let g of gradation_groups ) {
		for ( let t of time_base ) {
			g.getCurve( t );
		}
	}
	
	drawChart( time_base, gradation_groups );

	gradation_groups.forEach( function( g, i ) { 
		document.getElementById( 'rampTimeField' + i ).value	= g.ramp_time;		
	});
}

function updateGradationEnable() {
   let	channels	= [];
			   
   for ( let i = 0; i < N_CHANNELS; i++ ) {
	   if ( document.getElementById( 'gradationEnable' + i ).checked ) {
		   channels.push( i )
	   }
   }
		   
   console.log( channels );
}

function updateGroupSelect() {
	let	group	= [ [], [], [], [], [], [] ]

	for ( let i = 0; i < N_CHANNELS; i++ ) {
		group[ document.getElementById( 'groupSelect' + i ).value ].push( i );
	}

	console.log( group );
}

