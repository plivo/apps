conference
==========

A simple conference app showing off Plivo's capability. Provisions a number and a pin, which you can call into to get into the conference

This application shows off Plivo's ability as a platfporm.

__Installation__


Clone the repo:

```bash
    $ git clone git@github.com:abishekk92/conference.git
```

Install the Python dependencies:

```bash
    $ pip install -r requirements.txt
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
        connect('conference',host="YOUR-MONGODB_HOST")
     ```
     
  - To run the app
    
    ```bash
        $ foreman start
    ```
  - Please follow the instructions here to [deploy on heroku]( https://devcenter.heroku.com/articles/python)

Or you can simply do the following

  - Get a [Heroku account](https://id.heroku.com/signup). It's free!
  
    ```bash
       $ cd conference
    ```
  - Log into Heroku and upload your public key(assuming it's the first time, you're using Heroku)
    
    ```bash
	$ heroku login
	Enter your Heroku credentials.
	Email: foobar@example.com
	Password:
	Could not find an existing public key.
	Would you like to generate one? [Yn]
	Generating new SSH public key.
	Uploading ssh public key /Users/foobar/.ssh/id_rsa.pub
    ```
  - We need to create an app on Heroku, so that we can deploy
   
    ```bash
	$ heroku create
	Creating stark-window-524... done, stack is cedar
	http://stark-window-524.herokuapp.com/ | git@heroku.com:stark-window-524.git
	Git remote heroku added
    ```
  - Finally to deploy 
     
    ```bash
	  $ git push heroku master
    ```

__Workflow__ : 
   
   - The apps allows one to create conference on a subject and invite people to the conference by adding their mobile numbers.

   !["Create Conference"](https://raw.github.com/abishekk92/conference/master/screenshots/Screenshot%20from%202013-06-15%2023:12:23.png)
 
   - Or people can choose to join one of the already existing conference by dialing into the Plivo Number along with the conference pin.
   
   !["Join a Conference"](https://raw.github.com/abishekk92/conference/master/screenshots/Screenshot%20from%202013-06-15%2023:15:13.png)
   

   - Once the conference is created, the members are notified with the conference number and pin. The number is provisioned on the fly using Plivo's rent number endpoint. The code would look like
     
    ```python
            def rent_number(plivo_api,app_name="Conference Call"):
                app_id=get_appid(plivo_api,app_name)
	            response=plivo_api.get_number_group({"country_iso":"US","region":"california"})
	            group_id=response[1]["objects"][0]["group_id"]
	            response=plivo_api.rent_from_number_group({"group_id":group_id,"app_id":app_id})
	            number=response[1]["numbers"][0]["number"]
	            return number
     ```

   - Once the conference is over and if the moderator has opted in for the conference to be recorded, A message containing the record url is messaged
      
      ```python
                response.addConference(body='plivo',
    			       action= BASE_URL+url_for('submit_recording'),
				       method='GET',
				       record=record_value)
      ```
      The message is sent out using the Plivo API as follows

     ```python 
                def notify(message,mobile):
                    response=plivo_api.send_message({'src':CALLER_ID,
				                                    'dst':mobile,
				                                    'text':message,
				                                    'type':'sms'
			    	                                })
	                return response
     ```
