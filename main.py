#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import sys
sys.path.insert(0, 'libs')
from firebase import Firebase
import random
import types


class SmsHandler(webapp2.RequestHandler):
    def post(self):
    	phone = self.request.get('From')
    	body = self.request.get('Body')
    	users = usersRef.get()
    	# The user is trying to sign-up
    	if body.upper().strip() == 'SIGNUP':
    		if type(users) is types.NoneType:
    			users = []
    		found = False
    		# loop through users and see if this is a new person
    		for k, v in users.iteritems():
    			print v
    			if v[u'phone'] == phone:
    				found = True
    				msg = "<Response>You're already signed up! Your code is: " + v[u'uid'] + "</Response>" 
    		# if they're new, give them a UID and store it
    		if not found:
    			uid = hex(random.randint(0,65535))
    			usersRef.push({'phone': phone, 'uid': uid})
    			msg = "<Response>Thanks for signing-up! Your code is: " + uid + "</Response>"

    	# The user is trying to tag
    	elif body.upper().strip().startswith('TAG'):
    		# store the SMS message
    		messagesRef.push({'body': self.request.get('Body')})
      		msg = "Thanks! We've recorded your tag"
    	# We don't know what they're trying to do
    	else:
    		msg = "<Response>Sorry, I didn't understand that command. You can either SIGNUP or TAG.</Response>"

    	self.response.write(msg)


usersRef = Firebase('https://vdw.firebaseio.com/users')
messagesRef = Firebase('https://vdw.firebaseio.com/messages', auth_token='rkli7ILTCdMZNFpaZVkoVFWz5FSP08pCKdNjyY2A')

app = webapp2.WSGIApplication([
    ('/sms', SmsHandler)
], debug=True)
