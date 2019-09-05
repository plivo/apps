
'''
Uses the Application API to look up for the app_id using the app_name. In the list of application and their related info obtained from the API,its iterated until the app with the desired name is obtained
'''

def get_appid(plivo_api,app_name="Conference Call"):
	for application in plivo_api.get_applications()[1]['objects']:
		if application['app_name'] == app_name:
			app_id=application['app_id']
	return app_id
'''
In order to provision the users with a new number on the fly, we make use of Rent number API. It happes in the two steps as follows
1. First we need to get the group_id of the group from which we want to rent the number. This can be done by querying get_number_group which allsows us to specify different paramters like country,region,voice/sms etc..,

2. For simplicity's sake let us pick the first group. Using the group_id and the app_id we obtained earlier we can use rent_from_number_group, to rent from the group_id and link it to the app with the given app_id
'''
def rent_number(plivo_api,app_name="Conference Call"):
	app_id=get_appid(plivo_api,app_name)
	response=plivo_api.get_number_group({"country_iso":"US","region":"california"})
	group_id=response[1]["objects"][0]["group_id"]
	response=plivo_api.rent_from_number_group({"group_id":group_id,"app_id":app_id})
	number=response[1]["numbers"][0]["number"]
	return number

'''
    Generates a 4-digit pin based on the conference number that is generated. It is basically the first 4-digits of the digital sum of the confernece number
'''

def generate_pin(conference_number):
	numbers=list(conference_number)
	conference_pin="".join(map(lambda pair: str(reduce(lambda pair_a,pair_b:int(pair_a)+int(pair_b),pair)),zip(numbers[::2],numbers[1::2])))[:4]
	return conference_pin


