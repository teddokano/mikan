/*
 *	Javascript code for DUT_RTC.py
 *
 *	This script will be processed in DUT_RTC.py to replace "{%  %}" valriables
 */

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

function getTimeAndShow() {
	let url	= REQ_HEADER
	ajaxUpdate( url, getTimeAndShowDone )
}

/******** getTimeAndShowDone ********/

let prev_reg	= [];	//	to prevent refresh on user writing field
let prev_alarm	= [];	//	to prevent refresh on user writing field
let prev_alarm_flg	= false;	//	to prevent error of retrying open the dialog

function getTimeAndShowDone() {
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


/****************************
 ****	register controls
 ****************************/
 
/******** updateRegField ********/

function updateRegField( element, idx ) {
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
	ajaxUpdate( url, updateRegFieldDone )
}

function updateRegFieldDone() {
	obj = JSON.parse( this.responseText );
	
	document.getElementById('regField' + obj.reg ).value	= hex( obj.val )
}

function setCurrentTime( element ) {
	let url	= REQ_HEADER + 'set_current_time';
	ajaxUpdate( url );
}

function clarAlarm( element ) {
	document.getElementById( 'dialog' ).close();
	prev_alarm_flg	= false
	
	let url	= REQ_HEADER + 'clear_alarm'
	ajaxUpdate( url );
}

function setAlarm( element ) {

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

function clearAlarmSetting( element ) {
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
