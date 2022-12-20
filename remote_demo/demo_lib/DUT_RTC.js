const	SOUND_DATA	= '{% sound %}';
let		sound;

if ( '' != SOUND_DATA )
	sound	= new Audio( SOUND_DATA );
else
	sound	= null;
	
/****************************
 ****	time display
 ****************************/
 
/******** getTimeAndShow ********/

function makeGetTimeAndShow() {
	let prev_reg	= [];	//	to prevent refresh on user writing field
	let prev_alarm	= [];	//	to prevent refresh on user writing field
	let prev_alarm_flg	= false;	//	to prevent error of retrying open the dialog

	return function() {
		function done() {
			let obj = JSON.parse( this.responseText )

			let elem = document.getElementById( "datetime" );
			elem.innerText = obj.datetime.str;
			//console.log( obj.ts )
			if ( obj.ts ) {
				let elem = document.getElementById( "timestamp" );
				elem.innerText = obj.ts;
			}

			for ( let i = 0; i < 5; i++ ) {
				let value	= obj.alarm[ i ];
				if ( value != prev_alarm[ i ] ) {
					document.getElementById( "alarmField" + i ).value	= ( value == 0x80 ) ? '--' : hex( value );
				}
			}
			prev_alarm	= obj.alarm;
									
			for ( let i = 0; i < obj.reg.length; i++ ) {
				let value	= obj.reg[ i ];
				if ( value != prev_reg[ i ] ) {
					document.getElementById('regField' + i ).value	= hex( value );
				}
			}
			prev_reg	= obj.reg;
			
			if ( obj.alarm_flg ) {
				document.getElementById( 'dialog' ).showModal();
				prev_alarm_flg	= true;
				
				if ( sound )
					sound.play();
				else
					console.log( 'Sound is not played' )
			}
		}

		let url	= REQ_HEADER
		ajaxUpdate( url, done )
	}
}

let getTimeAndShow	= makeGetTimeAndShow();

/****************************
 ****	register controls
 ****************************/
 
/******** updateRegField ********/

function updateRegField( idx ) {
	let valueFieldElement = document.getElementById( "regField" + idx );
	let value	= parseInt( valueFieldElement.value, 16 )
	let no_submit	= 0
	
	if ( isNaN( value ) ) {
		no_submit	= 1
		value = document.getElementById( "Slider" + idx ).value;
	}
	value	= (value < 0  ) ?   0 : value
	value	= (255 < value) ? 255 : value
	valueFieldElement.value = hex( value )

	if ( no_submit )
		return;

	let url	= REQ_HEADER + "reg=" + idx + "&val=" + value
	ajaxUpdate( url, () => {
		obj = JSON.parse( this.responseText );		
		document.getElementById('regField' + obj.reg ).value	= hex( obj.val )
		
	} )
}

function setCurrentTime() {
	let url	= REQ_HEADER + 'set_current_time';
	ajaxUpdate( url );
}

function setPCTime( element ) {
	//	"setPCTime()" doesn't have precise timing synchronization mechanism
	//	but it may not be a big problem becase in noemal demo environment in local netwotk
	//	may have very small delay

	WKDY	= [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" ]

	let	now		= new Date( Date.now() - (new Date()).getTimezoneOffset() * 60 * 1000 );
	let url	= REQ_HEADER + 'set_pc_time=' + now.toJSON() + '&weekday=' + WKDY[ now.getDay() ];
	
	ajaxUpdate( url, () => {
		let	complete	= new Date( Date.now() - (new Date()).getTimezoneOffset() * 60 * 1000 );
		let	delay		= complete - now;

		console.log( "setPCTime(): turn around time = " + delay + "ms" );
	});
	
	// server will get string of "...?set_pc_time=2022-12-19T06:11:31.031Z&weekday=Monday?..."
}

function clarAlarm() {
	document.getElementById( 'dialog' ).close();
	prev_alarm_flg	= false
	
	let url	= REQ_HEADER + 'clear_alarm'
	ajaxUpdate( url );
}

function setAlarm() {

	let weekday = document.getElementById( "alarmField4" ).value;
	let day		= document.getElementById( "alarmField3" ).value;
	let hour	= document.getElementById( "alarmField2" ).value;
	let minute	= document.getElementById( "alarmField1" ).value;
	let second	= document.getElementById( "alarmField0" ).value;

	weekday	= ('--' == weekday) ? 80 : weekday;
	day		= ('--' == day)     ? 80 : day;
	hour	= ('--' == hour)    ? 80 : hour;
	minute	= ('--' == minute)  ? 80 : minute;
	second	= ('--' == second)  ? 80 : second;

	weekday	= '&weekday=' + weekday;
	day		= '&day='     + day;
	hour	= '&hour='    + hour;
	minute	= '&minute='  + minute;
	second	= '&second='  + second;

	let url	= REQ_HEADER + 'alarm' + weekday + day + hour + minute + second;
	ajaxUpdate( url );
}

function clearAlarmSetting() {
	document.getElementById( "alarmField4" ).value	= '--';
	document.getElementById( "alarmField3" ).value	= '--';
	document.getElementById( "alarmField2" ).value	= '--';
	document.getElementById( "alarmField1" ).value	= '--';
	document.getElementById( "alarmField0" ).value	= '--';

	weekday	= '&weekday=' + 80;
	day		= '&day='     + 80;
	hour	= '&hour='    + 80;
	minute	= '&minute='  + 80;
	second	= '&second='  + 80;

	let url	= REQ_HEADER + 'alarm' + weekday + day + hour + minute + second;
	ajaxUpdate( url );
}

window.addEventListener('load', function () {
	setInterval( getTimeAndShow, 1000 );
});
