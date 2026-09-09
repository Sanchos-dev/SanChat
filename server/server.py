#this is the main file on server

import config
import helper

if config.first_time:
	helper.generate_server_code()
else:
	if config.DEBUG:
		print("SERVER ID ALREADY GENERATED SKIPPING..")
		


