 # App for call blast.
from flask import Flask,render_template,request,g,Response
from flask.ext.sqlalchemy import SQLAlchemy
from uuid import uuid4

import plivoxml as plivo
from datetime import datetime,date
from dateutil.parser import parse

import time
import tasks


app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class Entries(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    request_id = db.Column(db.String(40), nullable=False, unique=True)
    auth_id = db.Column(db.String(20), nullable=False)
    auth_token = db.Column(db.String(40), nullable=False)
    from_number = db.Column(db.String(40), nullable=False)
    message = db.Column(db.Text, nullable=True)
    audio_url = db.Column(db.String(200),nullable=True)
    audio_first = db.Column(db.Boolean)
    csv_url = db.Column(db.String(200), nullable=False)
    cps = db.Column(db.Integer, default=2)
    fire_dt = db.Column(db.DateTime)
    status = db.Column(db.Boolean)


    def __init__(self,request_id, auth_id, auth_token,from_number, message, audio_url, audio_first, csv_url, cps, fire_dt, status):
        self.request_id = request_id
        self.auth_id = auth_id
        self.auth_token = auth_token
        self.from_number = from_number
        self.message = message
        self.audio_url = audio_url
        self.audio_first = audio_first
        self.csv_url = csv_url
        self.cps = cps
        self.fire_dt = fire_dt
        self.status = status

    def __repr__(self):
        return '<Entry %d:%r>' % (self.id, self.from_number)


def push_data(auth_id, auth_token, from_number, message, audio_url, audio_order, csv_url, cps,fire_dtime):
    request_id = str(uuid4())
    entry = Entries(request_id,auth_id, auth_token, from_number,message, audio_url, audio_order, csv_url,cps, fire_dtime, True)

    db.session.add(entry)
    db.session.commit()

    # Change this into a scheuler
    print "Request %s processed for %s." % (request_id, fire_dtime)
    #tasks.validate_message.delay(request_id)
    return request_id


@app.route('/')
def index():
    return render_template('user_input.html')

@app.route('/input', methods=['POST'])
def input():
    if request.method == 'POST':

        date_string = request.form['date']+' '+request.form['time']

        fire_dtime = parse(date_string)

        if request.form['order'] == 'after':
            order = False
        else:
            order = True

        print "Pushing request!", request.form

        request_id = push_data(request.form['id'],request.form['token'],request.form['from_no'],request.form['message'],request.form['audio'],order, request.form['csv'],request.form['cps'],fire_dtime)

        print "We have a lift of"
        return "Got Data: Messge id is %s" % request_id

@app.route('/call/<request_id>',methods=['POST','GET'])
def content(request_id):
    '''Send the content corresponding to message id.'''
    response = plivo.Response()
    response.addWait(length=1)

    entry = Entries.query.filter_by(request_id=request_id).first()

    if entry.audio_first:
        response.addPlay(body=entry.audio_url)
        response.addWait(length=1)
        response.addSpeak(body=entry.message)
    else:
        response.addSpeak(body=entry.message)
        response.addWait(length=1)
        response.addPlay(body=entry.audio_url)
    return Response(str(response), mimetype='text/xml')

@app.route('/verify/<request_id>', methods = ['POST', 'GET'])
def verify(request_id):
    response = plivo.Response()
    response.addWait(length=1)
    response.addGetDigits(action=app.config['URL']+'/enable/'+request_id, method="POST", finishOnKey='#', numDigits=1, playBeep=True, validDigits='1').addSpeak(body="Do you confirm the call blast? Use 1 to confirm and any other digit to cancel.")
    response.addSpeak(body="No Input recieved.")
    return Response(str(response), mimetype='text/xml')

@app.route('/enable/<request_id>', methods=['POST'])
def enable(request_id):
    if request.method == 'POST':
        data = request.form['Digits']
        print 'data veriy: ', data

        if data[0] == '1':
            print "Customer enabled"
            tasks.fire_bulk_call.delay(request_id)
        else:
            print "customer disabled"
        return "spawned calls"

if __name__ == "__main__":
    app.run()
