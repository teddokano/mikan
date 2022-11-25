COMPILE	= mpy-cross

MPY	= 	__init__.mpy		\
		GPIO.mpy			\
		interface.mpy		\
		LED_controller.mpy	\
		RTC.mpy				\
		stepper_motor.mpy	\
		temp_sensor.mpy

all : $(MPY)

%.mpy : %.py
	$(COMPILE) $<
