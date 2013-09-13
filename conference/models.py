from mongoengine import *

connect('conference',host="MONGODB-URL")

class Conference(Document):
	subject=StringField()
	phone=IntField()
	members=ListField(IntField())
	record=BooleanField()
	conference_number=IntField()
	conference_pin=IntField(max_value=9999)


def get_all_conference():
	return map(lambda conference: conference,Conference.objects)

def create_conference(subject, phone, members, 
		record, conference_number, conference_pin):
	conference=Conference()
	conference.subject=subject
	conference.phone=phone
	conference.members=members
	conference.record=record
	conference.conference_number=conference_number
	conference.conference_pin=conference_pin
	conference.save()
	print "Conference created"


def get_mobile(number):
	conference=Conference.objects.get(conference_number=number)
	return conference.phone

def get_record(number):
	conference=Conference.objects.get(conference_number=number)
	return conference.record
