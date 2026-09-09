import json
import base64
import config
import random
import string

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

