## here will be api calls
import base64
import config
import json
import os
import random
import string
def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")

def uid_generator(size=20, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def make_user_data_first_time(display_name, login,email,description,avatar_url,connected_server):
	uid = uid_generator()

	os.mkdir("udata")
	os.mkdir(config.user_download_path)

	user_data = {
	    "uid": uid,
	    "login": login,
	    "email": email,
	    "display_name": display_name,
	    "description": description,
	    "avatar_url": avatar_url,
	    "connected_server": connected_server,

	    "settings": {
	        "theme": "dark", 
	        "language": "en",
	        "notifications": {
	            "sound_enabled": True,
	            "desktop_alerts": True,
	            "show_preview": True,
	        },
	        "privacy": {
	            "show_online_status": True,
	            "send_read_receipts": True,
	        },
	    },
	    

	    "chat_state": {
	        "pinned_chats": [],
	        "muted_chats": [],
	        "archived_chats": [],
	        "blocked_uids": [],
	    },
	    
	    "device": {
	        "platform": "desktop",
	        "app_version": "0.0.1",
	    },
	}

	with open("udata/UserData.json", "w") as ufile:
		ufile.write(json.dumps(user_data))
		ufile.close()
	with open("udata/UserDM.json", "w") as udmfile:
		udmfile.write("")
		udmfile.close()
	with open("udata/UserGroups.json", "w") as ugfile:
		ugfile.write("")
		ugfile.close()


def decode_server_key(key):
	key_bytes = key.encode("ascii")
	key_string_bytes = base64.b64decode(key_bytes)
	key_decoded = key_string_bytes.decode("ascii")
	return key_decoded

def check_server_availability(key):
	decode_result = decode_server_key(key)
	server_info = json.loads(decode_result)
	s_domain = server_info["domain"]
	s_port = server_info["port"]
	s_pub_gr = server_info["pub_group"]
	save_config("server_key", key)
	save_config("server_domain", s_domain)
	save_config("server_api_port", s_port)
	save_config("pub_server_group_id", s_pub_gr)
	if config.DEBUG:
		print(f"recieved server key: {key}")
		print(f"decoded server key: {decode_result}\nserver_domain: {s_domain} \nserver_api_port: {s_port} \npub_server_group_id: {s_pub_gr}")
	return True

def login(login, password):
	if config.TESTING:
		if login == "tester" and password == "12345":
			return True
		else:
			return False

def check_reg(login):


	return False

def register(login, password):

	return True
