#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import json

import requests
from flask import Flask, request
import globalVar
from utils import db

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

# process received messages
@app.route('/', methods=['POST'])
def webhook():
    db.clear()
    db.create()
    #log( db.showAll())

    USER = ""
    QUESTION = ""

    # endpoint for processing incoming messaging events
    data = request.get_json()
    #log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                log("---------- INCOMING MESSAGE: -----------")
                log(messaging_event)


                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    message_text = messaging_event["message"]["text"]  # the message's text
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    USER = db.identifyUser( sender_id )
                    QUESTION = db.questionUser( sender_id )
                    if (message_text == "RESET" or message_text == "START" or message_text == "STOP"):
                        if message_text == "STOP":
                            pair_id = db.findMatchingId( sender_id )
                            if message_text == "STOP" and USER == "CLIENT" and pair_id:
                                send_message(pair_id, "The conversation has been ended. Thank you for your help.\nYou are on standby until next client contacts for help.")
                                send_message(sender_id, "The conversation has been ended. Thank you for using Trevor. Type RESET to ask another question.")
                                send_rating(sender_id)
                                db.unpair( sender_id, pair_id )
                                db.updateLawyerQuestion("WAITITNG")
                                pair_id = db.findMatchingId( sender_id )
                                while pair_id == None and db.questionUser( pair_id ) != "DONE" :
                                    pair_id = db.findMatchingId( sender_id )
                                if pair_id != None and db.questionUser( pair_id ) == "DONE" :
                                    log( pair_id )
                                    db.updateLawyerQuestion("DONE")
                                    send_message( pair_id, "You have been connected to a legal advisor. \n\nThis is the information he or she has provided:\nName: %s \nState: %s\n Below is his or her answer."%( db.getLawyerName( sender_id ), db.getLawyerState( sender_id ) ) )
                                    send_message( sender_id, "You have been connected to a client. \n\nThis is the information your client has provided:\nAge: %d \nState: %s \nTopic: %s \nBelow is his or her inquiry"%( db.getClientAge( pair_id ), db.getClientState( pair_id ), db.getClientTopic(pair_id) ))
                            elif message_text == "STOP" and USER == "LAWYER" and pair_id:
                                send_message(sender_id, "The conversation has been ended. Thank you for your help.\nYou are on standby until next client contacts for help.")
                                send_message(pair_id, "The conversation has been ended. Thank you for using Trevor.")
                                send_rating(pair_id)
                                db.unpair( pair_id, sender_id )
                                db.updateLawyerQuestion("WAITITNG")
                                pair_id = db.findMatchingId( sender_id )
                                while pair_id == None and db.questionUser( pair_id ) != "DONE" :
                                    pair_id = db.findMatchingId( sender_id )
                                if pair_id != None and db.questionUser( pair_id ) == "DONE" :
                                    log( pair_id )
                                    db.updateLawyerQuestion("DONE")
                                    send_message( pair_id, "You have been connected to a legal advisor. \n\nThis is the information he or she has provided:\nName: %s \nState: %s\n Below is his or her answer."%( db.getLawyerName( sender_id ), db.getLawyerState( sender_id ) ) )
                                    send_message( sender_id, "You have been connected to a client. \n\nThis is the information your client has provided:\nAge: %d \nState: %s \nTopic: %s \nBelow is his or her inquiry"%( db.getClientAge( pair_id ), db.getClientState( pair_id ), db.getClientTopic(pair_id) ))
                        else:
                            USER = ""
                            QUESTION = ""
                            db.removeId( sender_id )
                            send_start(sender_id) # VOLUNTEER OR CLIENT?

                    elif message_text == "HELP":
                        send_message(sender_id, "Type STOP to end conversation.")
                        send_message(sender_id, "Type RESET to restart.")


                    log("-------USER: " + USER)
                    log("-------QUESTION: " + QUESTION)

                    if USER == "CLIENT":

                        if QUESTION == "AGE":
                            send_message(sender_id, "received " + message_text)
                            if message_text != "SKIP":
                                db.updateClientAge(sender_id, int( message_text ) )
                            db.updateClientQuestion(sender_id, "STATE")
                            send_message(sender_id, "(OPTIONAL - for your legal advisor to better understand your case) \nEnter in your state (eg. NY) or enter SKIP:")                        #send_message("Enter in the initials of your state (eg: NY or PA) OR enter SKIP:")
                            # save message_text as STATE
                            QUESTION = "STATE"

                        elif QUESTION == "STATE":
                            send_message(sender_id, "received " + message_text)
                            if message_text != "SKIP":
                                db.updateClientState( sender_id, message_text)
                            db.updateClientQuestion(sender_id, "DONE")
                            send_message(sender_id, "We will connect you to your volunteer legal advisor shortly.")
                            pair_id = db.findMatchingId( sender_id )
                            while pair_id == None and db.questionUser( pair_id ) != "DONE" :
                                pair_id = db.findMatchingId( sender_id )
                            if pair_id != None and db.questionUser( pair_id ) == "DONE" :
                                log( pair_id )
                                #send_message( pair_id, "Legal adivisor and client connection established. \n\nThis is the information he or she has provided:\nName: %s \nState: %s\n Below is his or her answer."%( db.getLawyerName( pair_id ), db.getLawyerState( pair_id ) ) )
                                send_message( sender_id, "You have been connected to a legal advisor. \n\nThis is the information he or she has provided:\nName: %s \nState: %s\n Below is his or her answer."%( db.getLawyerName( pair_id ), db.getLawyerState( pair_id ) ) )
                                send_message( pair_id, "You have been connected to a client. \n\nThis is the information your client has provided:\nAge: %d \nState: %s \nTopic: %s \nBelow is his or her inquiry"%( db.getClientAge( sender_id ), db.getClientState( sender_id ), db.getClientTopic(sender_id) ))

                        elif QUESTION == "DONE":
                            #send_message( sender_id, "handshake betch")
                            pair_id = db.findMatchingId( sender_id )
                            send_message( pair_id, message_text )
                            # save message_text as STATE

                    elif USER == "VOLUNTEER":

                        if QUESTION == "NAME":
                            send_message(sender_id, "received " + message_text)
                            if message_text != "SKIP":
                                db.updateLawyerName(sender_id, message_text  )
                            db.updateLawyerQuestion(sender_id, "STATE")
                            send_message(sender_id, "(Enter in your state (eg. NY) or enter SKIP:")                        #send_message("Enter in the initials of your state (eg: NY or PA) OR enter SKIP:")
                            # save message_text as STATE
                            QUESTION = "STATE"

                        elif QUESTION == "STATE":
                            send_message(sender_id, "received " + message_text)
                            if message_text != "SKIP":
                                db.updateLawyerState( sender_id, message_text)
                            db.updateLawyerQuestion(sender_id, "DONE")
                            send_message(sender_id, "You will be contacted by a client shortly.")
                            pair_id = db.findMatchingId( sender_id )
                            while pair_id == None and db.questionUser( pair_id ) != "DONE" :
                                pair_id = db.findMatchingId( sender_id )
                            if pair_id != None and db.questionUser( pair_id ) == "DONE" :
                                log( pair_id )
                                send_message( pair_id, "You have been connected to a legal advisor. \n\nThis is the information he or she has provided:\nName: %s \nState: %s\n Below is his or her answer."%( db.getLawyerName( sender_id ), db.getLawyerState( sender_id ) ) )
                                send_message( sender_id, "You have been connected to a client. \n\nThis is the information your client has provided:\nAge: %d \nState: %s \nTopic: %s \nBelow is his or her inquiry"%( db.getClientAge( pair_id ), db.getClientState( pair_id ), db.getClientTopic(pair_id) ))
                        elif QUESTION == "DONE":
                            #send_message( sender_id, "second handshake betch")
                            pair_id = db.findMatchingId( sender_id )
                            send_message( pair_id, message_text )



                    else:
                        log("----------- MESSAGE NOT CAUGHT -----------")

                    '''

                    if( db.findMatchingId( sender_id ) != None ):
                        new_recipient_id = findMatchingId( sender_id )
                        send_message( new_recipient_id, message_text )
                    else:
                        send_message( sender_id, "Are you a lawyer or client?")

                    '''
                    # respond

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]

                    action = messaging_event["postback"]["payload"]
                    log("------- BUTTON PRESSED: " + action)

                    if action == "VOLUNTEER":
                        USER = "VOLUNTEER"
                        #send_message(sender_id, "You are a volunteer")
                        tempDict = { }
                        tempDict['id'] = sender_id
                        tempDict['name'] = 'N/A'
                        tempDict['currState'] = 'N/A'
                        db.addLawyer( tempDict )
                        db.updateLawyerQuestion( sender_id, "NAME" )
                        send_message( sender_id, "Enter in your name:")
                    elif action == "CLIENT":
                        USER = "CLIENT"
                        #send_message(sender_id, "You are a client")
                        tempDict = { }
                        tempDict['id'] = sender_id
                        tempDict['focus'] = 'N/A'
                        tempDict['currState'] = 'N/A'
                        tempDict['age'] = 0
                        #db.addClient( {'id':sender_id, 'age' : 0, 'focus' : 'N/A', 'currState' : 'N/A'} )
                        db.addClient( tempDict )
                        send_categories(sender_id)
                    elif action == "IMMIGRATION_LAW" or action == "CITIZENSHIP" or action == "VISA":
                        db.updateClientFocus( sender_id, action )
                        log( db.questionUser( sender_id ) )
                        db.updateClientQuestion(sender_id, "AGE" )
                        send_message(sender_id, "(OPTIONAL - for your legal advisor to better understand your case) \nEnter in your age OR enter SKIP:")

    return "ok", 200

# BOTH: VOLUNTEER OR CLIENT?
def send_start(recipient_id):
    #log("sending message to {recipient}: {text}".format(recipient=recipient_id), text="Hello, I'm Trevor. Would you like to volunteer your legal services or ask a legal question?")
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
         "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"button",
                "text":"Hello, I'm Trevor. Would you like to volunteer your legal services or ask a legal question?",
                "buttons":[
                  {
                    "type":"postback",
                    "title":"Volunteer",
                    "payload":"VOLUNTEER"
                  },
                  {
                    "type":"postback",
                    "title":"Ask Question",
                    "payload":"CLIENT"
                  }
                ]
              }
            }
        }
    })
    #log("<-------DATA")
    log(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

# CLIENT: 4 CATEGORIES
def send_categories(recipient_id):
    #log("sending message to {recipient}: {text}".format(recipient=recipient_id), text="Hello, I'm Trevor. Would you like to volunteer your legal services or ask a legal question?")
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
         "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"button",
                "text":"Choose a category that best suits your question:",
                "buttons":[
                  {
                    "type":"postback",
                    "title":"Immigration Law",
                    "payload":"IMMIGRATION_LAW"
                  },
                  {
                    "type":"postback",
                    "title":"Citizenship",
                    "payload":"CITIZENSHIP"
                  },
                  {
                    "type":"postback",
                    "title":"VISA",
                    "payload":"VISA"
                  }
                ]
              }
            }
        }
    })
    log(data)
    #log( USER )
    #log( QUESTION )
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_rating(recipient_id):
    #log("sending message to {recipient}: {text}".format(recipient=recipient_id), text="Hello, I'm Trevor. Would you like to volunteer your legal services or ask a legal question?")
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
         "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"button",
                "text":"Please rate the legal help you've received. This helps better our quality of legal advisors.",
                "buttons":[
                  {
                    "type":"postback",
                    "title":"★★★★★",
                    "payload":"5"
                  },
                  {
                    "type":"postback",
                    "title":"★★★",
                    "payload":"3"
                  },
                  {
                    "type":"postback",
                    "title":"★",
                    "payload":"1"
                  }
                ]
              }
            }
        }
    })
    log(data)
    #log( USER )
    #log( QUESTION )
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

# GENERAL: message
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
