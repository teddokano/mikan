COMPILE	= mpy-cross

MPY	= 	__init__.mpy		\
		DUT_GENERALCALL.mpy	\
		DUT_LEDC.mpy			\
		DUT_RTC.mpy			\
		DUT_TEMP.mpy			\
		no_sound_data.mpy	\
		utils.mpy			

all : $(MPY)

%.mpy : %.py
	$(COMPILE) $<
