import os

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
BROKER_URI = os.environ['CLOUDAMQP_URL']

URL= 'http://immense-scrubland-3463.herokuapp.com'
COUNTER_URL='http://cryptic-bastion-8418.herokuapp.com/call/1'
