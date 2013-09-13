call forward
==========

This application is a jab at trying to showcase a wide variety of Plivo's API like Direct Dialing, Call Recording, Text Messaging,Renting number, Application API to build an app which provides user with a plivo number and a voice mail number which when called to would forward the incoming to call to the specified SIP Endpoint or Mobile Phone. If the call is not answered the call is automatically transferred to the Voice Mail, wherein the caller can record his message. A link to the voice message would be texted to the user at his mobile number

__Installation__


Clone the repo:

```bash
    git clone git@github.com:abishekk92/forward.git
```

Install the Python dependencies:

```bash
    pip install -r requirements.txt
```
Note: 

  - You would need pip to be installed. Instructions on how to install pip for variety of operating systems can be found [here](http://www.pip-installer.org/en/latest/installing.html)

  - The app uses MongoDB as the datastore, you can install it following the instruction found [here](http://docs.mongodb.org/manual/installation/)
  
  - The app heavily uses Plivo's API, please make sure to get a [free developer account](http://plivo.com/)
  
  - Update the AUTH_ID and AUTH_TOKEN in the app.config as follows 
  
    ```python
        AUTH_ID="YOUR-AUTH-ID"
        AUTH_TOKEN="YOUR-AUTH-TOKEN"
        BASE_URL="APP-BASE-URL"
    ```
    
  - Update the MongoDB host in models.py with your values as follows
     
     ```python
        connect('forward',host="YOUR-MONGODB_HOST")
     ```
     
  - To run the app
    
    ```bash
        foreman start
    ```
  - Please follow the instructions here to [deploy on heroku]( https://devcenter.heroku.com/articles/python)

__Workflow__ : 
   
   - The app doubles up as a call forwarding and a voice mail system. You can create an entry in the table to get a plivo number and voice mail number, which can be used for call forwarding and voice mail respectively.

   !["Call Forward"](https://raw.github.com/abishekk92/foward/master/screenshots/forward.png)
 
   

   - The number is provisioned on the fly using Plivo's rent number endpoint. The code would look like
     
    ```python
            def rent_number(plivo_api,app_name):
                app_id=get_appid(plivo_api,app_name)
	            response=plivo_api.get_number_group({"country_iso":"US","region":"california"})
	            group_id=response[1]["objects"][0]["group_id"]
	            response=plivo_api.rent_from_number_group({"group_id":group_id,"app_id":app_id})
	            number=response[1]["numbers"][0]["number"]
	            return number
     ```

   - The Call forwarding is done using Plivo's Direct Dialing. By setting the path to the XML as the answer_url, as soon as the call is answered, the XML would get executed on Plivo. It is done using plivo helper as follows
     
     ```python
		response=plivo.Response()
		response.addSpeak("Please wait while we are forwarding your call")
		response.addDial(callerName=CALLER_NAME).addUser(SIP)
		response.addDial(callerId=CALLER_ID).addNumber(MOBILE)
		response.addSpeak("The number you're trying is not reachable at the moment. You are being redirected to the voice mail")
		response.addDial(callerId=CALLER_ID,
				action=BASE_URL+url_for('voice_mail'),
				method='GET').addNumber(VOICEMAIL_NUMBER)
		response=make_response(response.to_xml())
     ```
  
   - If the mobile phone is not reachable, it's automatically forwarded to the voice mail, which prompts the user for a message. This is done as 
     
     ```python
           	response=plivo.Response()
		response.addSpeak("Please leave your message after the beep")
		response.addRecord(action=BASE_URL+url_for('message'),method='GET')
		response.addSpeak("Thank you, your message has been recorded")
		response.addHangup()
		response=make_response(response.to_xml())
		response.headers['Content-Type']='text/xml'
     ```
   - Once the voice mail has been recieved and the call is terminated, the RecordUrl obtained from Plivo is sent as a text message to the user as a notification.
  
    ```python
		response=PLIVO_API.send_message({'src':CALLER_ID,
					 'dst':MOBILE,
					 'text': MESSAGE
					})
    ```
