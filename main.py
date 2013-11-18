#!/usr/bin/env python

# Dependencies
import webapp2
import os
import sys
import random
from random import randint
import types
from google.appengine.ext import ndb

# Apparently this is the way you get python to resolve module directories?
# Will need to Google this later...
sys.path.insert(0, "libs")

# Use Firebase for the realtime components of the app (leaderboard, activity feed)
from firebase import Firebase
from token_generator import create_token

# Setup Firebase admin-enabled stores
authtoken = create_token(os.environ["FIREBASE_SECRET"], {}, {"admin":True})
leaderboardRef = Firebase("https://vdw.firebaseio.com/leaderboard", authtoken)
feedRef = Firebase("https://vdw.firebaseio.com/feed", authtoken)

# Use GAE data store as the primary app data store
class AppUser(ndb.Model):
    phone = ndb.StringProperty(required=True)
    uid = ndb.StringProperty(required=True)
    nick = ndb.StringProperty(default="A Vancouver Hacker")
    email = ndb.StringProperty(default="none provided")
    total_tags = ndb.IntegerProperty(default=0)

class Tag(ndb.Model):
    tagger = ndb.StringProperty(required=True)
    tagged_person = ndb.StringProperty(required=True)
    media_url = ndb.StringProperty()

# Return a JSON-serializeable list from an AppUser query object
def json_serializeable(users):
    result = []
    for user in users:
        result.append({
            "nick":user.nick,
            "total_tags":user.total_tags
        })
    return result

# Return a text count of the number of people a user has met
def count_tags(user):
    # Get current count for user
    met_people = user.total_tags
    noun = "person" if met_people == 1 else "people"

    # Return current tag count
    return "You have met {0} {1} so far.".format(met_people, noun)

# Handle a tag request
def tag_person(current_tagger, tagged_person_id, media_url=None):
    if current_tagger.uid == tagged_person_id:
        return "lolwut? You can't tag yourself!"

    tagged_person = AppUser.query(AppUser.uid == tagged_person_id).get()
    if not tagged_person:
        return "No other player found by the given ID."
    else:
        previousTag = Tag.query(Tag.tagger == current_tagger.uid, Tag.tagged_person == tagged_person_id).get()
        if previousTag:
            return "You have already met this person!"
        else:
            # Create a new tag
            tag = Tag(tagger=current_tagger.uid, tagged_person=tagged_person.uid, media_url=media_url)
            tag.put()

            # Update relevant users
            current_tagger.total_tags = current_tagger.total_tags+1
            current_tagger.put()
            tagged_person.total_tags = tagged_person.total_tags+1
            tagged_person.put()

            # Push relevant Firebase updates
            feedRef.push({
                "tagger":current_tagger.nick,
                "tagged":tagged_person.nick,
                "media_url":media_url
            })

            # generate leaderboard
            leaders = AppUser.query().order(-AppUser.total_tags).fetch(20)
            leaderboardRef.push({
                "leaders":json_serializeable(leaders)
            })

            # Return current tag count
            return "You have checked in with {0}!".format(tagged_person.nick)

# Create a new app user
def new_user(phone):
    # Create a unique 4 character ID for the user - keep trying until
    # we get a unique one
    uid = ""
    done = False
    while not done:
        uid = hex(random.randint(0,65535))[2:]
        existingUser = AppUser.query(AppUser.uid == uid).get()
        done = not existingUser

    # Create new user
    user = AppUser(phone=phone, uid=uid)
    user.put()

    # BAMF!
    return "Thanks for signing up for VanDevWeek Tag! Your ID is: {0}. Text HELP for commands and options.".format(uid)

# Create a webapp class
class SmsHandler(webapp2.RequestHandler):
    def post(self):
        if self.request.get('secret') == os.environ["TWILIO_SECRET"]:
            # Get POST data sent from Twilio
            phone = self.request.get("From")
            body = self.request.get("Body")
            media_url = self.request.get("MediaUrl0")
            print(self.request)

            # Set up XML response for Twilio
            response_message = "<Response><Message>{0}</Message></Response>"
            msg = ""

            new_phone = phone
            if not new_phone.startswith("+1"):
                new_phone = "+1"+new_phone

            # Get the user based on their phone number
            user = AppUser.query(AppUser.phone == new_phone).get()

            # The user is new to the system, try and add them
            if not user:
                msg = new_user(new_phone)

            # Get current number of tags
            elif body.upper().strip().startswith("COUNT"):
                msg = count_tags(user)

            # Tag a user
            elif body.upper().strip().startswith("TAG"):
                user_input = body.strip()[4:]
                if user_input.upper().startswith("HELP"):
                    msg = "Text \"TAG [another player's ID]\" and an optional picture to check in and score points. Introduce yourself to other devs to get their ID :)"
                else:
                    msg = tag_person(user, user_input, media_url)

            # Change nickname
            elif body.upper().strip().startswith("NICK"):
                user_input = body.strip()[5:]
                if user_input.upper().startswith("HELP"):
                    msg = "Text \"NICK [a new nickname]\" to change the nickname that is displayed for you."
                else:
                    new_nick = body.strip()[5:]
                    if len(new_nick) > 0:
                        user.nick = new_nick
                        user.put()
                        msg = "Word. Your new nickname is {0}.".format(user.nick)
                    else:
                        msg = "Please provide a nickname."

            # Change email
            elif body.upper().strip().startswith("EMAIL"):
                user_input = body.strip()[6:]
                if user_input.upper().startswith("HELP"):
                    msg = "Text \"EMAIL [your e-mail]\" to change the e-mail address associated with you. Allows your tags to send you e-mail."
                else:
                    new_email = body.strip()[6:]
                    if len(new_email) > 0:
                        user.email = new_email
                        user.put()
                        msg = "Gotcha. Your e-mail is {0}.".format(user.email)
                    else:
                        msg = "Please provide an e-mail address."

            # Unsubscribe
            elif body.upper().strip().startswith("STOP"):
                user.key.delete()
                msg = "You are now unsubscribed. Text this number again to re-subscribe."

            # Help
            elif body.upper().strip().startswith("HELP"):
                msg = "::VanDevWeek Tag:: Your player ID is: {0}. Nickname: {1}. Commands are HELP, NICK, EMAIL, COUNT, and TAG. Text \"[command name] HELP\" for command-specific help. Text STOP to unsubscribe.".format(user.uid, user.nick)

            # We don't know what they're trying to do
            else:
                msg = "Hi there {0}! Your ID is: {1}. Text HELP for commands and options.".format(user.nick, user.uid)

            # Render XML response to Twilio
            self.response.headers["Content-Type"] = "text/xml"
            self.response.write(response_message.format(msg))
        else:
            # Render XML response to Twilio
            self.response.headers["Content-Type"] = "text/plain"
            self.response.status_int = 403
            self.response.write("You're not Twilio. Get lost.")

# Create URI handlers
app = webapp2.WSGIApplication([
    ("/sms", SmsHandler)
], debug=True)
