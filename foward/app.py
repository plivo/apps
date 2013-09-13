from flask import Flask,request,Response,make_response,url_for,render_template

import plivo

from config_parser import get_config

from helper import rent_number

from model import create_forward_entry,get_details_from,get_mobile

configs=get_config()

PLIVO_API=plivo.RestAPI(configs["AUTH_ID"],configs["AUTH_TOKEN"])



CALLER_ID="19512977322"
BASE_URL="http://ancient-taiga-3101.herokuapp.com"
app = Flask(__name__)

app.debug=True

@app.route('/')

def index():
	return render_template('index.html') 

@app.route('/save')

def save():
	sip=request.args.get('sip','')
	mobile=request.args.get('mobile','')
	caller_name=request.args.get('caller_name','')
	voicemail_number,plivo_number=map(lambda app_name:rent_number(PLIVO_API,app_name),["Voice Mail","Call Forward"])
	create_forward_entry(sip,mobile,caller_name,
			     voicemail_number,plivo_number)
	return "Your plivo phone number is %s" %(plivo_number)

@app.route('/forward')

def forward():
	plivo_number=request.args.get('To','')
	CALLER_NAME,SIP,MOBILE,VOICEMAIL_NUMBER=get_details_from(plivo_number)
	response=plivo.Response()
	response.addSpeak("Please wait while we are forwarding your call")
'''
	addDial adds Dial element to Reponse. Dial element is useful in Direct Dialing, that is when the request is made to the route containing the XML,Plivo executes each of the element one by one. When it encounters Dial it calls the first Dial element and goes on to the next one, should it fail and so on.
	Dial elements can be Dial:User or Dial:Number
	<Dial callerName="callerName">@sip_endpoint</Dial>
	<Dial callerId="caller_id">phone_number</Dial>
'''
	response.addDial(callerName=CALLER_NAME).addUser(SIP)
	response.addDial(callerId=CALLER_ID).addNumber(MOBILE)
	response.addSpeak("The number you're trying is not reachable at the moment. You are being redirected to the voice mail")
	response.addDial(callerId=CALLER_ID,
			action=BASE_URL+url_for('voice_mail'),
			method='GET').addNumber(VOICEMAIL_NUMBER)
	response=make_response(response.to_xml())
	response.headers['Content-Type']='text/xml'
	
	return response


@app.route('/voice/mail')

def voice_mail():
	response=plivo.Response()
	
	'''
	 Adds speak element to the already created ResponseElement. Now the XML would look something like
	 <Response> <Speak> Hello welcome to my awesome app! </Speak> </Response>. When the XML is executed at Plivo's end, these words would be spoken
	'''
	
	response.addSpeak("Please leave your message after the beep")
	
	'''
	Adds a Record Element to Response. This is useful when the call needs to be recorded.
	<Record action="" method="GET|POST"/>
	'''

	response.addRecord(action=BASE_URL+url_for('message'),method='GET')
	response.addSpeak("Thank you, your message has been recorded")
	response.addHangup() ## Adds Hangup Element, when the control enters this element while executing the XML, It Hangs up the current call
	response=make_response(response.to_xml())
	response.headers['Content-Type']='text/xml'
	
	return response


@app.route('/message')


def message():
	record_url=request.args.get('RecordUrl','')
	plivo_number=request.args.get('To','')
	MESSAGE="Hey, we have received a voice message for you. You can access them at %s" %(record_url)
	MOBILE=get_mobile(plivo_number)
	
	'''
	send_message from plivo_helper lib sends text message to the given number from the specified caller_id
	'''
	
	response=PLIVO_API.send_message({'src':CALLER_ID,
					 'dst':MOBILE,
					 'text': MESSAGE
					})
	return response




if __name__ == '__main__':
       app.run(host='0.0.0.0')

