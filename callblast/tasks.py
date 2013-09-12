from sqlalchemy import create_engine, MetaData, Table

from celery import Celery
from config import URL,COUNTER_URL,SQLALCHEMY_DATABASE_URI, BROKER_URI
import plivo

import urllib2
import csv
import logging
import time

# default rabbitmq
celery = Celery('tasks', cache='amqp', broker=BROKER_URI)

@celery.task
def fire_bulk_call(id):
    print "Bulk call entry point for :", id

    db = create_engine(SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(db)
    entries = Table('entries', metadata, autoload=True)
    esel = entries.select()

    data = esel.execute(request_id=id).first()
    print "Data got:", data

    to = ''
    # Get csv file
    numbers = urllib2.urlopen(data.csv_url)
    reader = csv.reader(numbers)

    cps = data['cps']
    server = plivo.RestAPI(data['auth_id'], data['auth_token'])

    numberlist = []

    #Limit this with cps 3*cps does the job
    for number in reader:
        numberlist.append(number[0])

    to = ''

    while len(numberlist):
        for i in range(0,cps*3):
            if len(numberlist):
                if to == '':
                    to = numberlist.pop()
                else:
                    to += '<' + numberlist.pop()

        params = { 'from' : data['from_number'],
                        'to' : to,
                        'answer_url' : URL+'/call/'+id,
                        # Debug purposes
                        'ring_url' : COUNTER_URL
                    }

        print 'Making Bulk Call:',params
        resp = server.make_call(params)
        print resp

        # Figure out.
        to = ''

@celery.task
def validate_message(id):
    '''fire the validation and thus fire the calls'''
    print "Validating: ", id

    db = create_engine(SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(db)
    entries = Table('entries', metadata, autoload=True)
    esel = entries.select()

    data = esel.execute(request_id=id).first()

    print "Got data:", data['from_number']

    params = {   'from' : 1000,
                 'to'   : data['from_number'],
                 'answer_url' : URL+'/verify/'+id
    }

    print "Params are: ", params

    # Do plivo magic
    p = plivo.RestAPI(data['auth_id'],data['auth_token'])
    resp = p.make_call(params)
    print "Fired: ", resp
