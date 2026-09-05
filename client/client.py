## here will be api calls

import config

def decode_server_key(key):
	pass
def check_server_availability(key):
	if config.DEBUG:
		print(f"recieved server key: {key}")

	decode_result = decode_server_key(key)

	if config.DEBUG:
		print(f"decoded server key: {decode_result}")
	# here will be logic
	return True

def login(login, password):

	return True


def check_reg(login):

	return False


def register(login, password):

	return True
