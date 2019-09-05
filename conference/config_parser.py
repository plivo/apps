def get_config():
	config={}
	for item in open('app.config'):
		key,value=item.split("=")
		config[key]=value.strip()
	return config

