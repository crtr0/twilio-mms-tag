#Twilio MMS Tag

**TL;DR - Let people use SMS (and MMS) to play tag.**

Twilio MMS Tag is a web application that lets people "tag" one another using SMS/MMS. It employs the following technologies:
* [Twilio MMS](http://twilio.com/mms)
* [Firebase](http://firebase.com)
* [Google App Engine](http://cloud.google.com)

When players register to play, they are assigned a random 4-digit hex code. When they meet someone new, they ask if the person is playing DevWeek tag. If so, they simply send an SMS with that person's code to "tag" them. Both parties (tagger and tagee) are awarded points for making the connection. They can also (optionally) send an MMS with a picture of the person they met.

This app was deployed most recently during [Vancouver Dev Week](http://devweektag.appspot.com). 
