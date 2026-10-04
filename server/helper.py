import json
import base64
import config
import random
import string
from hashlib import sha256


def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")


def group_id_generator(size=12, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))



def generate_pub_server_group(): #ONE TIME RUN
	if config.pub_server_group:
		if config.pub_server_group_id == '':
			pub_server_group_code = group_id_generator()
			if config.DEBUG:
				print(f"generated public group id: {pub_server_group_code}")
			save_config("pub_server_group_id", pub_server_group_code)
			return pub_server_group_code
		else:
			return config.pub_server_group_id
	else:
		return ""

def generate_server_code(): #ONE TIME RUN
	if config.server_id == '':
		serv_info = f'{{ "domain":"{config.server_domain}", "port":"{config.server_api_port}", "pub_group":"{generate_pub_server_group()}" }}'
		serv_info_bytes = serv_info.encode("ascii")
		base64_bytes = base64.b64encode(serv_info_bytes)
		base64_string = base64_bytes.decode("ascii")
		if config.DEBUG:
			print(f"generated server id: {base64_string}")
		save_config("server_id", base64_string)
		save_config("first_time", False)
		return base64_string
	else:
		if config.DEBUG:
			print("SERVER ID ALREADY GENERATED SKIPPING..")
		pass

def hash_pwd(pw):
	hzt = sha256(pw.encode('utf-8')).hexdigest()
	return hzt

def check_db_login(l , pass_hash):
	if config.DEBUG:
		#for testing it`s login tester and password test
		if l == "tester" and pass_hash == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08":
			return True
		else:
			pass
			
	else:
		return False

def check_db_by_login(l):
	if config.DEBUG:
		#for testing it`s login tester
		if l == "tester":
			return True
		else:
			pass
			
	else:
		return False