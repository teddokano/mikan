class GradationFunc	{
	constructor( max_iref, ramp_time, up, down, hold_on_time, hold_off_time, phase ) {
		if ( 0 < ramp_time ) {
			let iref	= max_iref * 255;	
			let time	= ramp_time * 1000;
			
			let step_duration	= time / iref;
			let cycle_time;
			let	multi_fctr;
			let	iref_inc;
			
			if ( 32 < step_duration )
				cycle_time	= 8;
			else
				cycle_time	= 0.5;
				
			multi_fctr	= parseInt( step_duration / cycle_time );
			multi_fctr	= (multi_fctr <   1) ? 1 : multi_fctr;
			multi_fctr	= (64 < multi_fctr) ? 64 : multi_fctr;
			
			if ( 1 == multi_fctr )
				iref_inc	= parseInt( iref / (time / cycle_time) )
			else
				iref_inc	= 1

			ramp_time	= ((multi_fctr * cycle_time ) * (iref / iref_inc)) / 1000
		}
		
		this.phase		= phase;
		this.iref		= max_iref;
		this.ramp_time	= ramp_time;
		this.t_ramp_up	= up ? ramp_time : 0;
		this.t_hold_on	= this.t_ramp_up + hold_on_time;
		this.t_ramp_dn	= this.t_hold_on + (down ? ramp_time : 0);
		this.t_cycle	= this.t_ramp_dn + hold_off_time;
		this.values		= [];
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


/*
 *	Javascript code for DUT_TEMP.py
 *
 *	This script will be processed in DUT_LEDC.py to replace "{%  %}" valriables
 */

const	TABLE_LEN	= 10
const	GRAPH_HIGH	= 1
const	GRAPH_LOW	= 0

function drawChart( time, g0, g1, g2, g3, g4, g5, g6 ) {
	var ctx = document.getElementById("myLineChart");
	window.myLineChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: time,
			datasets: [
					   {
						   label: 'group0',
						   data: g0,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 0, 0, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group1',
						   data: g1,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 115, 78, 48, 0.5 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group2',
						   data: g2,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 255, 0, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group3',
						   data: g3,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 237, 109, 53, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group4',
						   data: g4,
						   lineTension: 0.0,
						   pointRadius: 0,
						   borderColor: "rgba( 255, 190, 0, 1 )",
						   backgroundColor: "rgba( 0, 0, 0, 0 )"
					   },
					   {
						   label: 'group5',
						   data: g5,
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
						labelString: 'time'
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
	let time_base	= []
	let	gradation_groups	= [];

	for ( let i = 0; i < 6; i++ ) {					
		let iref	= parseFloat( document.getElementById( 'maxCurrent'    + i ).value );
		let rtime	= parseFloat( document.getElementById( 'rampTimeField' + i ).value );
		let h_on	= parseFloat( document.getElementById( 'holdON'        + i ).value );
		let h_off	= parseFloat( document.getElementById( 'holdOFF'       + i ).value );
		let up		= document.getElementById( 'rampSwUp'      + i ).checked;
		let down	= document.getElementById( 'rampSwDown'    + i ).checked;
		let phase	= document.getElementById( 'phase'         + i ).value;
		
		gradation_groups[ i ]	= new GradationFunc( iref, rtime,  up, down, h_on, h_off, phase );
	}

	t_max	= 0;
	
	for ( let g of gradation_groups ){
		t_max	= (t_max < g.t_cycle) ? g.t_cycle : t_max;
	}
	
	let resoution	= 1000
	for ( let i = 0; i <= t_max * resoution; i ++ ) {
		time_base.push( i / resoution );
	}
	
	for ( let g of gradation_groups ) {
		for ( let element of time_base ) {
			g.getCurve( element );
		}
	}
	
	drawChart( time_base, gradation_groups[ 0 ].values, gradation_groups[ 1 ].values, gradation_groups[ 2 ].values, gradation_groups[ 3 ].values, gradation_groups[ 4 ].values, gradation_groups[ 5 ].values  );
	
	for ( let i = 0; i < 6; i++ )
		document.getElementById( 'rampTimeField' + i ).value	= gradation_groups[ i ].ramp_time;
}

function updateGroupSelect( id, i ) {
	let value = document.getElementById( id + i ).value;
	
	console.log( id + i + ' : ' + value );
}

function updateGradationEnable( id, i ) {
	let value = document.getElementById( id + i ).checked;
	
	console.log( id + i + ' : ' + value );
}


