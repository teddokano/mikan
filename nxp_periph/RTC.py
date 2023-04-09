from	machine				import	I2C, SPI
from nxp_periph.interface	import	Interface, I2C_target, SPI_target

class RTC_base():
	"""
	An abstraction class to make RTC user interface.
	
	"machine.RTC" like interface available but this class
	doesn't inherit machine.RTC to separate its behavior
	"""
	DATETIME_TUPPLE_FORM	= ( "year", "month", "day", "weekday",
								"hours", "minutes", "seconds", "subseconds" )
	NOW_TUPPLE_FORM			= ( "year", "month", "day", "hours",
								"minutes", "seconds", "subseconds", "tzinfo" )
	DEINIT_VAL				= ( 2015, 1, 1, 0, 0, 0, 0, None )
	DEINIT_TUPLE			= dict( zip( NOW_TUPPLE_FORM, DEINIT_VAL ) )
	DEINIT_TUPLE[ "weekday" ]	= 0		# dummy
	ALARM_KEYS				= ( "day", "hours", "minutes", "seconds", "weekday" )
	
	WKDY	= ( "Monday", "Tuesday", "Wednesday",
				"Thursday", "Friday", "Saturday", "Sunday" )
	MNTH	= ( "None", "January", "February", "March",
				"April", "May", "June", "July", "August",
				"September", "October", "Nobemver", "Decemver" )

	def datetime( self, *args ):
		"""
		get/set date&time
		
		IF NO ARGUMENT GIVEN, it returns tuple of
		  ( "year", "month", "day", "weekday",
		    "hours", "minutes", "seconds", "subseconds" )
		IF 1 OR 2 ARGUMENT ARE GIVEN, it sets date&time
		the 1st argument should be 8-tuple in format with
		  ( "year", "month", "day", "hours", "minutes",
		    "seconds", "subseconds", "tzinfo" )
		  the tzinfo is a dummy and it will be ignored.

		Parameters
		----------
		args[0] : 8-tuple, optional
			tuple of date&time
			
		Returns
		-------
		tuple : date&time info
			( "year", "month", "day", "hours",
			  "minutes", "seconds", "subseconds", "tzinfo" )
			                              tzinfo is a dummy

		"""
		length	= len( args )
		if 1 <= length:
			if 1 <= length:
				self.init( args[ 0 ], form = self.DATETIME_TUPPLE_FORM )	# args[1:] will be ignored
			return

		dt	= self.__get_datetime_reg()

		return tuple( dt[ key ] for key in self.DATETIME_TUPPLE_FORM )

	def now( self ):
		"""
		get current date&time
	
		Returns
		-------
		tuple : date&time info
			( "year", "month", "day", "hours",
			  "minutes", "seconds", "subseconds", "tzinfo" )
			                              tzinfo is a dummy
			
		"""
		dt	= self.__get_datetime_reg()
		
		return tuple( dt[ key ] for key in self.NOW_TUPPLE_FORM )

	def init( self, datetime, form = NOW_TUPPLE_FORM, weekday = 0 ):
		"""
		set date&time
	
		Parameters
		----------
		datetime : tuple, optional
			date&time tuple.
			( "year", "month", "day", "hours",
			  "minutes", "seconds", "subseconds", "tzinfo" )
			Need to have first 3 elements at least: "year", "month" and "day".
			Other elements are optional
			tzinfo is not required (ignored)
		weekday : int, optional
			weekday number : 0~6 (default=0)
			
		"""
		dt	= RTC_base.tuple2dt( datetime, form, weekday = weekday )
		self.__set_datetime_reg( dt )

	def deinit( self ):
		"""
		de-initialize
		
		software reset performed
		and date&time is set to ( 2015, 1, 1, 0, 0, 0, 0, None )
		"""
		self.__software_reset()
		self.init( self.DEINIT_VAL )

	def alarm_int( self, pin_select, **kwargs ):
		"""
		set alarm interrupt
	
		Parameters
		----------
		pin_select : string which contains "A" or "B"
			This parameter will be ignored if the RTC has only one
			interrupt output.
			A character "A" or "B" should be in the string.
			If both characters are there, it will set "A" interrupt.
		kwargs : dict
			A dictionaly which contains keys of
			"day", "hours", "minutes", "seconds" and "weekday".
			Parameter which was not specified in the dictionary will
			not be set. For instance, {"minutes":37} is given,
			The alarm will notify every hour at xx:37.

		"""
		dt	= { k:80 for k in self.ALARM_KEYS }
		for k, i, in kwargs.items():
			dt[ k ]	= i

		s	= [ dt[ k ] for k in self.ALARM_KEYS ]
		s	= [ "off" if k == 80 else str( k ) for k in s ]
		s	= [ i + ":" + j for i, j, in zip( self.ALARM_KEYS, s ) ]
		#print( "setting alarm: {}".format( ", ".join( s ) ) )

		self.__set_alarm( pin_select, dt )
		return s
		
	def timer_alarm( self, hours = 0, minutes = 0, seconds = 0, pin_select = "B" ):
		"""
		set timer
	
		Parameters
		----------
		hours   : int
		minutes : int
		seconds : int
		pin_select : string which contains "A" or "B", default "B"
			This parameter will be ignored if the RTC has only one
			interrupt output.
			A character "A" or "B" should be in the string.
			If both characters are there, it will set "A" interrupt.

		"""
		t	= self.datetime()
		
		seconds, m_carry	= (t[6] + seconds          ) % 60, (t[6] + seconds           ) // 60,
		minutes, h_carry	= (t[5] + minutes + m_carry) % 60, (t[5] + minutes + m_carry)  // 60,
		hours				= (t[4] + hours   + h_carry) % 24
		
		alarm_time	= {
							"hours"		: hours,
							"minutes"	: minutes,
							"seconds"	: seconds
					  }
		alm	= self.alarm_int( pin_select, **alarm_time )
		return	alm
	
	def clear_alarm( self ):
		"""
		disabling alarm interrupt
		"""
		self.__clear_alarm()
	
	def cancel( self ):
		"""
		cancel alarm
		"""
		self.__cancel_alarm()

	def periodic_interrupt( self, pin_select = "A", period = 1 ):
		"""
		set periodic (every minutes or seconds) interrupt
	
		Parameters
		----------
		pin_select : string which contains "A" or "B"
			This parameter will be ignored if the RTC has only one
			interrupt output.
			A character "A" or "B" should be in the string.
			If both characters are there, it will set "A" interrupt.
		period : int, option
			Periodic interrupt interval

		"""
		self.__set_periodic_interrupt( pin_select, period )

	def set_timestamp_interrupt( self, num, pin_select = "B", last_event = True ):
		"""
		set timestamp interrupt
	
		Parameters
		----------
		pin_select : string which contains "A" or "B", default "B"
			This parameter will be ignored if the RTC has only one
			interrupt output.
			A character "A" or "B" should be in the string.
			If both characters are there, it will set "A" interrupt.
		num : int
			timestamp number
		last_event : bool, option
			In default (True), the timestamp stores last event date&time
			If False, it will store first event date&time
			
		"""
		self.__set_timestamp_interrupt( pin_select, num, last_event )

	def timestamp( self ):
		"""
		get timestamp
	
		Parameters
		----------
		num : int
			timestamp number
		
		Returns
		-------
		tuple : date&time info
			( "year", "month", "day", "hours",
			  "minutes", "seconds", "subseconds", "tzinfo" )
			                              tzinfo is a dummy
		bool : timestamp event storing mode
			True  = last event storing
			False = forst event storing
		bool : active state
			True  = active
			False = disabled

		"""
		
		ts_list	= []
		for i in range( 1, self.NUMBER_OF_TIMESTAMP + 1 ):
			dt	= self.__get_timestamp_reg( i )
			dt[ "tuple" ]	= tuple( dt[ key ] for key in self.NOW_TUPPLE_FORM )
			ts_list	+= [ dt ]
		
		return ts_list

	def timestamp2str( self, ts_list ):
		"""
		timestamp converted to a str
		"""
		s	= []
		for ts, i in zip( ts_list, range( 1, self.NUMBER_OF_TIMESTAMP + 1 ) ):
			s	+= [ "timestamp{} ({}, {}): {}".format( i, ts[ "active" ], ts[ "last" ], RTC_base.tuple2str( ts[ "tuple" ], RTC_base.NOW_TUPPLE_FORM ) ) ]

		return "\n".join( s )

	def oscillator_stopped( self ):
		"""
		detects the RTC was beeing reset
	
		Returns
		-------
		bool : active state
			True  = stopped
			False = never

		"""
		return self.__oscillator_stopped()

	def battery_switchover( self, switch ):
		"""
		enabling battery switch over
	
		Parameters
		----------
		switch : bool
			Enable battery switch-over by True

		"""
		self.__battery_switchover( switch )

	def interrupt_clear( self ):
		"""
		interrupt clear
	
		Returns
		-------
		list : list of flags

		"""
		return self.__interrupt_clear()

	def check_events( self, events ):
		"""
		translate events from flags to names
	
		Parameters
		----------
		events : list of event flags

		Returns
		-------
		list : list of event names

		"""
		return self.__check_events( events )

	@classmethod
	def tuple2dt( cls, datetime, form, weekday = 0 ):
		"""
		converts a tuple format data into a dict

		Parameters
		----------
		datetime	: tuple
		form		: string
			tuple or list of key labels
		weekday		: int, default = 0
			
		Returns
		-------
		dict
			dict with keys of NOW_TUPPLE_FORM
		
		"""
		dt	= cls.DEINIT_TUPLE.copy()	# to prepare initialized dict to overwrite neccessary items
		for key, item in zip( form, datetime ):
			dt[ key ]	= item

		if "weekday" not in dt:
			dt[ "weekday" ]	= weekday

		return dt

	@classmethod
	def tuple2str( cls, tpl, form ):
		"""
		converts a tuple format data into a string

		Parameters
		----------
		datetime	: tuple
		form		: sstringtr
			tuple or list of key labels
			
		Returns
		-------
		string

		"""
		dt	= dict( zip( form, tpl ) )

		if "weekday" in dt:
			dt[ "weekday" ]	= cls.WKDY[ dt[ "weekday" ] ]
		else:
			dt[ "weekday" ]	= ""

		dt[ "month" ]	= cls.MNTH[ dt[ "month" ] ]
		str	 = "%04d %s %02d %s %02d:%02d:%02d" % \
					(dt[ "year" ], dt[ "month" ], dt[ "day" ], dt[ "weekday" ], \
					dt[ "hours" ], dt[ "minutes" ], dt[ "seconds" ] )
		
		return str

	@classmethod
	def bin2bcd( cls, value ):
		"""
		converts normal int to binary-coded-decimal (BCD)

		Parameters
		----------
		value : int
			normal integer number
		
		Returns
		-------
		int : BCD

		"""

		return ((value // 10) << 4) + (value % 10)

	@classmethod
	def bcd2bin( cls, value ):
		"""
		converts binary-coded-decimal (BCD) to normal int

		Parameters
		----------
		value : int
			BCD
		
		Returns
		-------
		int : normal integer

		"""

		return (value >> 4) * 10 + (value & 0x0F)


##	@class		PCF2131_base
#	@brief		A class to manage PCF2131 (RTC)
#
class PCF2131_base( RTC_base ):
	"""
	An abstraction class for PCF2131
	The PCF2131 class can be composed with one of interface class: I2C_target or SPI_target
	"""
	REG_NAME		= (		"Control_1", "Control_2", "Control_3", "Control_4", "Control_5",
							"SR_Reset",
							"100th_Seconds", "Seconds", "Minutes","Hours", "Days", "Weekdays", "Months", "Years",
							"Second_alarm", "Minute_alarm", "Hour_alarm", "Day_alarm", "Weekday_alarm",
							"CLKOUT_ctl",
							"Timestp_ctl1", "Sec_timestp1", "Min_timestp1", "Hour_timestp1", "Day_timestp1", "Mon_timestp1", "Year_timestp1",
							"Timestp_ctl2", "Sec_timestp2", "Min_timestp2", "Hour_timestp2", "Day_timestp2", "Mon_timestp2", "Year_timestp2",
							"Timestp_ctl3", "Sec_timestp3", "Min_timestp3", "Hour_timestp3", "Day_timestp3", "Mon_timestp3", "Year_timestp3",
							"Timestp_ctl4", "Sec_timestp4", "Min_timestp4", "Hour_timestp4", "Day_timestp4", "Mon_timestp4", "Year_timestp4",
							"Aging_offset",
							"INT_A_MASK1", "INT_A_MASK2", "INT_B_MASK1", "INT_B_MASK2",
							"Watchdg_tim_ctl", "Watchdg_tim_val"
						)
	INT_MASK		= { "A": ["INT_A_MASK1", "INT_A_MASK2"], "B": [ "INT_B_MASK1", "INT_B_MASK2" ] }
	REG_ORDER_DT	= ( "subseconds", "seconds", "minutes", "hours", "day", "weekday", "month", "year" )
	REG_ORDER_ALRM	= ( "seconds", "minutes", "hours", "day", "weekday" )
	REG_ORDER_TS	= ( "subseconds", "seconds", "minutes", "hours", "day", "month", "year" )
	
	NUMBER_OF_TIMESTAMP	= 4
	
	def __software_reset( self ):
		self.write_registers( "SR_Reset", 0xA5 )

	def __get_datetime_reg( self ):
		dt		= {}
		length	= len( self.REG_ORDER_DT )
		
		data	= self.read_registers( "100th_Seconds", length )
		data[ 1 ]	&= ~0x80	#	mask OSF flag

		for i, k in zip( range( length ), self.REG_ORDER_DT ):
			dt[ k ]	= RTC_base.bcd2bin( data[ i ] )

		dt[ "year" ]		+= 2000	#	PCF2131 can only store lower 2 digit of year
		dt[ "subseconds" ]	*= 10	#	7th element of datetime tuple is defined as microsenonds. Need from convert 1/00 sec ticks
		dt[ "tzinfo" ]		 = None
			
		return dt

	def __set_datetime_reg( self, dt ):
		dt[ "year" ]		-= 2000
		dt[ "subseconds" ]	//= 10

		data	= [ dt[ k ] for k in self.REG_ORDER_DT ]
		data	= list( map( RTC_base.bin2bcd, data ) )

		self.bit_operation( "Control_1", 0x28, 0x20 )	#	set STOP and clear POR_OVRD
		self.bit_operation( "SR_Reset",  0x80, 0x80 )	#	set CPR
		
		self.write_registers( "100th_Seconds", data )
		
		self.bit_operation( "Control_1", 0x20, 0x00 )	#	clear STOP
		# utime.sleep( 0.122 )	# not neccessary but be sure the RTC count starts after 0ms~122ms from STOP is released

	def __set_alarm( self, int_pin, dt ):
		data	= [ dt[ k ] for k in self.REG_ORDER_ALRM ]
		data	= list( map( RTC_base.bin2bcd, data ) )

		self.write_registers( "Second_alarm", data )

		if int_pin:
			select	= "A" if "A" in int_pin else "B"
			self.bit_operation( self.INT_MASK[ select ][ 0 ], 0x04, 0x00 )
		self.bit_operation( "Control_2", 0x02, 0x02 )

	def __clear_alarm( self ):
		self.bit_operation( "Control_2", 0x10, 0x00 )

	def __cancel_alarm( self, int_pin, dt ):
		self.bit_operation( "Control_2", 0x02, 0x00 )

	def __set_periodic_interrupt( self, int_pin, period ):
		if int_pin:
			select	= "A" if "A" in int_pin else "B"
		
		if period == 0:
			self.bit_operation( "Control_1", 0x03, 0x00 )
			if int_pin:
				self.bit_operation( self.INT_MASK[ select ][ 0 ], 0x30, 0x30 )
			return 0

		v	= 0x02 if period == 60 else 0x01
		self.bit_operation( "Control_1", 0x03, v )
		
		if int_pin:
			self.bit_operation( self.INT_MASK[ select ][ 0 ], 0x30, ~(v << 4) )

		return 60 if period == 60 else 1

	def __set_timestamp_interrupt( self, int_pin, num, last_event ):
		num		-= 1
		r_ofst	 = 7
		r	= self.REG_NAME.index( "Timestp_ctl1" ) + (num * r_ofst)
		v	= 0x00 if last_event else 0x80
		
		self.bit_operation( r, 0x80, v )
		
		if int_pin:
			select	= "A" if "A" in int_pin else "B"
			self.bit_operation( self.INT_MASK[ select ][ 1 ], (0x01 << (3 - num)), ~(0x01 << (3 - num)) )
			self.bit_operation( "Control_5", 0x1 << (7 - num), 0x1 << (7 - num) )

	def __get_timestamp_reg( self, num ):
		dt		= {}
		num		-= 1
		r_ofst	 = 7
		length	= len( self.REG_ORDER_TS )
		r	= self.REG_NAME.index( "Timestp_ctl1" ) + (num * r_ofst)

		data	= self.read_registers( r, length )
		
		dt[ "last" ]	= "first event" if data[ 0 ] & 0x80 else "last event"
		dt[ "active" ]	= "disabled"    if data[ 0 ] & 0x40 else "active"

		data[ 0 ]	&= 0x1F

		for i, k in zip( range( length ), self.REG_ORDER_TS ):
			dt[ k ]	= RTC_base.bcd2bin( data[ i ] )

		dt[ "year" ]		+= 2000	#	PCF2131 can only store lower 2 digit of year
		dt[ "subseconds" ]	*= 50	#	use 50 if Control_1.100TH_S_DIS == 0, else 62.5
		dt[ "tzinfo" ]		 = None

		return dt

	def __interrupt_clear( self ):
		r	= self.REG_NAME.index( "Control_2" )
		rv	= self.read_registers( "Control_2", 3 )
		
		if rv[ 0 ] & 0x90:	# if interrupt flag set in Control_2
			self.write_registers( r + 0, rv[ 0 ] & ~((rv[ 0 ] & 0x90) | 0x49) )	#	datasheet 7.11.5

		if rv[ 1 ] & 0x08:	# if interrupt flag set in Control_3
			self.write_registers( r + 1, rv[ 1 ] & ~(0x08) )

		if rv[ 2 ] & 0xF0:	# if interrupt flag set in Control_4
			self.write_registers( r + 2, rv[ 2 ] & ~(rv[ 2 ] & 0xF0) )

		return rv

	def __oscillator_stopped( self ):
		return True if 0x80 & self.read_registers( "Seconds", 1 ) else False
	
	def __battery_switchover( self, switch ):
		self.bit_operation( "Control_3", 0xE0, 0x00 if switch is True else 0xE0 )	#	battery switch-over function enabled
	
	EVENT_NAME0		= ( "periodic", "watchdog", "alarm", "xx" )	#	"xx" is a dummy to avoid dict-zip bug
	EVENT_FLAG0		= { 0x80, 0x40, 0x10, 0x00 }				#	0x00 is a dummy
	EVENT_NAME1		= ( "battery switch over", "battery low" )
	EVENT_FLAG1		= { 0x08, 0x04 }
	EVENT_NAME2		= ( "ts1", "ts2", "ts3", "ts4" )
	EVENT_FLAG2		= { 0x80, 0x40, 0x20, 0x10 }
	EVENTS			= [ dict( zip( EVENT_NAME0, EVENT_FLAG0 ) ), dict( zip( EVENT_NAME1, EVENT_FLAG1 ) ), dict( zip( EVENT_NAME2, EVENT_FLAG2 ) ),  ]
	
	def __check_events( self, event ):
		list	= []

		for e, f in zip( event, self.EVENTS ):
			for k, v in f.items():
				if e & v:
					list	+= [ k ]
		
		return list

	def __test( self ):
		self.bit_operation( "Control_5", 0xF0, 0xF0 )


class PCF2131_I2C( PCF2131_base, I2C_target ):
	"""
	PCF2131 class with I2C interface
	"""
	def __init__( self, interface, address ):
		I2C_target.__init__( self, interface, address )

class PCF2131_SPI( PCF2131_base, SPI_target ):
	"""
	PCF2131 class with SPI interface
	"""
	def __init__( self, interface, cs ):
		SPI_target.__init__( self, interface, cs )

class __PCF2131__doesnt_work():
	"""
	Doesn't work :(
	Parent class member doesn't appear in instance
	"""
	DEFAULT_ADDR	= (0xA6 >> 1)

	def __new__( cls, interface, address = DEFAULT_ADDR, cs = None ):
		print( "__new__(), {}, {}".format( cls, interface ) )
		
		if isinstance( interface, I2C ):
			return super().__new__( type( PCF2131_I2C( interface, address ) ) )

		if isinstance( interface, SPI ):
			return super().__new__( type( PCF2131_SPI( interface, cs ) ) )

DEFAULT_ADDR	= (0xA6 >> 1)
DEFAULT_CS		= None

def PCF2131( interface, address =  DEFAULT_ADDR, cs = DEFAULT_CS ):
	"""
	A constructor interface for PCF2131

	Parameters
	----------
	interface	: machine.I2C or machine.SPI object
	address		: int, option
		If need to specify (for I2C interface)
	cs			: machine.Pin object
		If need to specify (for SPI interface)

	Returns
	-------
	PCF2131_I2C or PCF2131_SPI object
		returns PCF2131_I2C when interface == I2C
		returns PCF2131_SPI when interface == SPI

	Examples
	--------
	For using I2C
		>>> intf = I2C( 0, freq = (400 * 1000) )
		>>> rtc  = PCF2131( intf )
	For using SPI
		>>> intf = SPI( 0, 500 * 1000, cs = 0 )
		>>> rtc  = PCF2131( intf )
	
	"""
	if isinstance( interface, I2C ):
		return PCF2131_I2C( interface, address )

	if isinstance( interface, SPI ):
		return PCF2131_SPI( interface, cs )

class PCF85063( RTC_base, I2C_target ):
	"""
	PCF85063 class
	"""
	DEFAULT_ADDR	= (0xA2 >> 1)
	REG_NAME		= (	"Control_1", "Control_2",
						"Offset",
						"RAM_byte",
						"Seconds", "Minutes", "Hours", "Days", "Weekdays", "Months", "Years",
						"Second_alarm", "Minute_alarm", "Hour_alarm", "Day_alarm", "Weekday_alarm",
						"Timer_value", "Timer_mode"
						)
	INT_MASK		= { "A": ["INT_A_MASK1", "INT_A_MASK2"], "B": [ "INT_B_MASK1", "INT_B_MASK2" ] }
	REG_ORDER_DT	= ( "seconds", "minutes", "hours", "day", "weekday", "month", "year" )
	REG_ORDER_ALRM	= ( "seconds", "minutes", "hours", "day", "weekday" )
	
	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""
		Parameters
		----------
		i2c		: machine.I2C object
		address	: int, option
			If need to set I2C target address
		
		"""
		super().__init__( i2c, address = address )

	def __software_reset( self ):
		self.bit_operation( "Control_1", 0x10, 0x10 )

	def __get_datetime_reg( self ):
		dt		= {}
		length	= len( self.REG_ORDER_DT )
		
		data	= self.read_registers( "Seconds", length )
		data[ 1 ]	&= ~0x80	#	mask OS flag

		for i, k in zip( range( length ), self.REG_ORDER_DT ):
			dt[ k ]	= RTC_base.bcd2bin( data[ i ] )

		dt[ "year" ]		+= 2000	#	PCF2131 can only store lower 2 digit of year
		dt[ "subseconds" ]	 = 0	#	dummy
		dt[ "tzinfo" ]		 = None
			
		return dt

	def __set_datetime_reg( self, dt ):
		dt[ "year" ]		-= 2000
		dt[ "subseconds" ]	 = 0	#	dummy

		data	= [ dt[ k ] for k in self.REG_ORDER_DT ]
		data	= list( map( RTC_base.bin2bcd, data ) )

		self.bit_operation( "Control_1", 0x20, 0x20 )	#	set STOP
		self.write_registers( "Seconds", data )
		self.bit_operation( "Control_1", 0x20, 0x00 )	#	clear STOP

	def __set_alarm( self, int_pin, dt ):
		data	= [ dt[ k ] for k in self.REG_ORDER_ALRM ]
		data	= list( map( RTC_base.bin2bcd, data ) )

		self.write_registers( "Second_alarm", data )
		self.bit_operation( "Control_2", 0x80, 0x80 )

	def __clear_alarm( self ):
		pass	# will be implemented later

	def __cancel_alarm( self, int_pin, dt ):
		self.bit_operation( "Control_2", 0x80, 0x00 )

	def __set_periodic_interrupt( self, int_pin, period ):
		self.bit_operation( "Timer_mode", 0x06, 0x00 )
		if period == 0:
			return 0
	
		timer_max	= [ r * 255 for r in ( (1 / 4096), (1 / 64), 1, 60 ) ]

		res, tcf	= 60, 0x3
		for m, i in zip( timer_max, range( len( timer_max ) ) ):
			if period <= m:
				res, tcf	= m / 255, i
				break

		tv	= int( period / res )
		self.write_registers( "Timer_value", tv )
		self.bit_operation( "Timer_mode", 0x1E, tcf << 3 | 0x06 )
		
		return tv * res

	def __set_timestamp_interrupt( self, int_pin, num, last_event ):
		pass

	def __get_timestamp_reg( self, num ):
		pass

	def __interrupt_clear( self ):
		rv, wv	= self.bit_operation( "Control_2", 0x48, 0x00 )
		return rv

	def __oscillator_stopped( self ):
		return True if 0x80 & self.read_registers( "Seconds", 1 ) else False
	
	def __battery_switchover( self, switch ):
		pass

	EVENT_NAME		= ( "periodic", "alarm" )
	EVENT_FLAG		= { 0x08, 0x40 }
	EVENTS			= dict( zip( EVENT_NAME, EVENT_FLAG ) )
	
	def __check_events( self, event ):
		list	= []

		for k, v in self.EVENTS.items():
			if event & v:
				list	+= [ k ]
	
		return list

	def __test( self ):
		self.bit_operation( "RAM_byte", 0xF0, 0xF0 )


