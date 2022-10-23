def get_css():
	print( "get_css()" )
	s	= """\
<style>
html {
	font-size: 80%;
	font-family: Arial;
	display: inline-block;
	text-align: center;
}
body {
	font-size: 1.0rem;
	font-color: #000000;
	vertical-align: middle;
}
div {
	border: solid 1px #EEEEEE;
	box-sizing: border-box;
	text-align: center;
	font-size: 1.5rem;
	padding: 5px;
}
.header {
	border: solid 1px #EEEEEE;
	text-align: center;
	font-size: 1.5rem;
	padding: 1.0rem;
}
.info {
	text-align: center;
	font-size: 1.0rem;
}
.datetime {
	font-size: 3.0rem;
}
.control_panel {
	box-sizing: border-box;
	text-align: left;
	font-size: 1.0rem;
}
.slider_table_row {
	height: 3.0rem;
}
.item_R {
	background-color: #FFEEEE;
}
.item_G {
	background-color: #EEFFEE;
}
.item_B {
	background-color: #EEEEFF;
}
.reg_table {
	box-sizing: border-box;
	text-align: left;
	font-size: 1.0rem;
}
.reg_table_row {
	height: 1.0rem;
}
.foot_note {
	text-align: center;
	font-size: 1rem;
	padding: 0.5rem;
}

input[type="range"] {
	-webkit-appearance: none;
	appearance: none;
	cursor: pointer;
	outline: none;
	height: 5px; width: 85%;
	background: #E0E0E0;
	border-radius: 10px;
	border: solid 3px #C0C0C0;
}
input[type="range"]::-webkit-slider-thumb {
	-webkit-appearance: none;
	background: #707070;
	width: 20px;
	height: 20px;
	border-radius: 50%;
	box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, 0.15);
}
input[type="range"]:active::-webkit-slider-thumb {
	box-shadow: 0px 5px 10px -2px rgba(0, 0, 0, 0.3);
}
input[type="text"] {
	/* width: 2em; */
	height: 1em;
	font-size: 100%;
	text-align: center;
	border: solid 0px #FFFFFF;
}
.table_LEDC {
	background-color: #EEEEEE;
	border-collapse: collapse;
	width: 100%;
}
.td_LEDC {
	border: solid 1px #FFFFFF;
	text-align: center;
}
.table_TEMP {
	background-color: #FFFFFF;
	border-collapse: collapse;
}
.td_TEMP {
	border: solid 1px #EEEEEE;
	text-align: center;
}
.input_text_TMP {
	width: 10em;
}
.para {
	display: flex;
}
.log_panel, .info_panel {
	border: solid 0px #FFFFFF;
	padding: 5px;
}
.table_RTC {
	background-color: #EEEEEE;
	border-collapse: collapse;
	width: 100%;
}
.td_RTC {
	border: solid 1px #FFFFFF;
	text-align: center;
}
</style>
"""
	return s
