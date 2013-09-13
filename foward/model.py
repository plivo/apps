from mongoengine import *

connect('call_forward',host="mongodb://forward:forward@dharma.mongohq.com:10078/call_forward")

class Forward(Document):
	sip=StringField()
	mobile=IntField()
	caller_name=StringField()
	voicemail_number=IntField()
	plivo_number=IntField()
def create_forward_entry(sip,mobile,caller_name,voicemail_number,plivo_number):
	forward_table=Forward()
	forward_table.sip=sip
	forward_table.mobile=mobile
	forward_table.caller_name=caller_name
	forward_table.voicemail_number=voicemail_number
	forward_table.plivo_number=plivo_number
	forward_table.save()
	print "Entry created in Forward table"
def get_details_from(number=0):
	forward_table=Forward.objects.get(plivo_number=number)
	return (forward_table.caller_name,forward_table.sip,
		forward_table.mobile,forward_table.voicemail_number
		)
def get_mobile(number):
	try:
		forward_table=Forward.objects.get(plivo_number=number)
	except:
		forward_table=Forward.objects.get(voicemail_number=number)

	return forward_table.mobile
