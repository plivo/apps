'''
Application SMS URL Usage:  http://localhost:5000/forward/?numbers=1415xxxxxxx
Application Email URL Usage:  http://localhost:5000/forward/?emails=k@plivo.com

frm: Actual Sender
to: Plivo Sending Number
numbers: Actual Reciever

Full Paramters frm Plivo:
&frm=1415xxxxxxx&to=1415xxxxxxx&text=Hello

Gunmail Usage: http://localhost:5000/reverse/?
'''

import re
import plivo
import plivoxml
import os
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse
import requests
from redis import Redis
from flask import Flask, render_template, request, make_response

mail_domain = str(os.environ.get('MAILGUN_SERVER_NAME', 'samples.mailgun.org'))
mail_domain_incoming = 'my.' + mail_domain
mail_auth_key = str(os.environ.get('MAILGUN_ACCESS_KEY',
                'key-3ax6xnjp29jd6fds4gc373sgvjxteol0'))

plivo_auth_id = str(os.environ['PLIVO_AUTH_ID'])
plivo_token = str(os.environ['PLIVO_AUTH_TOKEN'])
plivo_number = str(os.environ['PLIVO_NUMBER'])

plivo_client = plivo.RestAPI(plivo_auth_id, plivo_token)

redis_server = str(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
redis_url = urlparse(redis_server)
redis_host=redis_url.hostname
redis_port=redis_url.port
if not redis_port:
    redis_port = 6379
redis_db = 0

try:
    redis_client = Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_url.password)
except:
    raise Exception('Add the Redis Add-On. Or set up Redis!')

CHAR_LIMIT = 240
DEFAULT_KEY_EXPIRY = 900

app = Flask(__name__)


"""
This is a method which sends emails to Gunmail.

  Args:
    number -- Number to Send to.
    frm_address -- Email Address to Send to.
    text -- Content of Email to Send.

  Returns:
    Plivo API Response

  Raises:
"""
def send_message(number, text):
    try:
         value = redis_client.get(number)
    except:
         value = False
    if value:
        print ('Sending outbound SMS')
        params = {"src": plivo_number, "dst": number, "text": text}
        response = plivo_client.send_message(params)
        print (str(response))
    else:
        response = 'Cant send SMS to: '+number
        print(response)
    return response

"""
This is a method which sends emails to Gunmail.

  Args:
    emails -- List of Emails to Send to.
    frm_address -- Email Address to Send to.
    frm_name -- Email Addressee to Send to.
    text -- Content of Email to Send.

  Returns:

  Raises:
"""
def send_email(emails, frm_address, frm_name, text):
    requests.post(("https://api.mailgun.net/v2/"+mail_domain+"/messages"),
                  auth=("api", mail_auth_key),
                  data={"from": frm_name + " <" + frm_address + ">",
                   "to": emails.split(','),
                   "subject": "You Have a Message frm: " + frm_name + ".",
                   "text": text
                   })

"""
This is the method that takes parameters from Gunmail. It also
sends messages.

  Args:

  Returns:

  Raises:
"""
@app.route('/reverse/', methods=['POST'])
def reverse():
    to = request.form.get('recipient')
    frm = request.form.get('sender')
    subject = request.form.get('subject')
    text = request.form.get('stripped-text')

    try:
        to_search = '^(.*)@' + mail_domain_incoming + '$'
        to_number = re.search(to_search, to).group(1)
    except:
        to_number = None
    if not to_number:
        print ('No valid Number')
        print ('To: ' + to)
        print ('From: ' + frm)
        print ('Subject: ' + subject)
        print ('Text: ' + text)
        raise Exception("Invalid to number passed")
    if not text:
        text = ''
    if frm:
        text = 'From: ' + frm + ';' + text
    if subject:
        text = 'Subject: ' + subject + ';' + text

    text_list = []
    start_index = 0
    # CHAR_LIMIT is the safe limit for long SMS in plivo
    if len(text) <= CHAR_LIMIT:
        text_list.append(text)
    while len(text) > (start_index + CHAR_LIMIT):
        text_list.append(text[start_index:(start_index + CHAR_LIMIT)])
        start_index += CHAR_LIMIT

    response_list = []
    for send_text in text_list:
        response = send_message(to_number, send_text)
        response_list.append(response)
    return render_template('response_template.xml', response=response_list)

"""
This is the method that takes user parameters, returns an XML.
It also sends emails.

  Args:

  Returns:
   Response as an XML

  Raises:
"""
@app.route('/forward/', methods=['GET', 'POST'])
def forward():
    if request.method == 'GET':
        frm = request.args['From']
        to = request.args['To']
        text = request.args['Text']
        numbers = request.args.get('Numbers')
        emails = request.args.get('Emails')
    elif request.method == 'POST':
        frm = request.form['From']
        to = request.form['To']
        text = request.form['Text']
        numbers = request.form.get('Numbers')
        emails = request.form.get('Emails')
    r = plivoxml.Response()
    if numbers or emails:
        if numbers:
            print ("Sending SMS")

            text = 'From: '+str(frm) + '; ' + text
            numbers = numbers.split(',')
            numbers = '<'.join(numbers)
            params = {
               'src' : str(to),
               'dst' : numbers,
               'type' : 'sms',
               }
            r.addMessage(text, **params)

        if emails:
            print ("Sending emails")

            frmEmail = str(frm) + '@' + mail_domain_incoming

            #Unmodified Text Here.
            try:
                redis_client.set(frm, 'True')
                redis_client.expire(frm, DEFAULT_KEY_EXPIRY)
            except:
                pass

            send_email(str(emails), frmEmail, frm, text)

            emails = emails.split(',')
            emails = '<'.join(emails)
            text = 'From: '+str(frm) + '; ' + text
            params = {
               'src' : str(frmEmail),
               'dst' : emails,
               'type' : 'sms',
               }
            #TODO: Add Email Type as Valid.
            #r.addMessage(body, **params)
        else:
            r.addHangup()
    response = make_response(r.to_xml())
    response.headers["Content-type"] = "text/xml"
    return response

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host = "0.0.0.0", port = port, debug = True)

