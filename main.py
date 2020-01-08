import time
from collections import defaultdict
from urllib.parse import urlencode
from twilio.rest import Client, TwilioRestClient
from twilio.twiml.voice_response import VoiceResponse, Gather
import config as cfg

class AutomatedMessenger():
    def __init__(self):
        self.account_sid = cfg.account_sid
        self.auth_token = cfg.auth_token
        self.client = Client(self.account_sid, self.auth_token)
        self.number = cfg.number
        self.contacts = cfg.contacts

    def runReminder(self):
        return

    def makeCall(self,message="",contact=None,number=None,url="https://twimlets.com/message?"):
        if not contact and not number:
            print("No valid contact specified")

        if contact in self.contacts:
            to_ = self.contacts[contact]
        else:
            to_ = number

        call = self.client.calls.create(
                    from_=self.number,
                    to=to_,
                    url=url + urlencode({'Message': message}))
        return call

    def getAllMessages(self):
        '''
        Return dictionary of messages
            - Key: Contact
            - Value: Message List
        '''
        ret = defaultdict(list)
        messages = self.client.messages.list()
        for record in messages:
            if record.from_ == self.number:
                ret[record.to].append(record.body)
            else:
                ret[record.from_].append(record.body)
        return ret

    def getReceivedMessages(self):
        '''
        Return dictionary of messages
            - Key: Contact
            - Value: Received Message List
        '''
        ret = defaultdict(list)
        messages = self.client.messages.list()
        for record in messages:
            if record.to == self.number:
                ret[record.from_].append(record.body)
        return ret
    
    def sendMessage(self,body='',contact=None,number=None):
        if not contact and not number:
            print("No valid contact specified")

        if contact in self.contacts:
            to_ = self.contacts[contact]
        else:
            to_ = number
        
        message = self.client.api.account.messages.create(
                from_=self.number,
                to=to_,
                body=body,
        )
        print("Sent '{}' to {}".format(body,to_))
        return message


if __name__ == "__main__":
    cb = AutomatedMessenger()
    # res = cb.getReceivedMessages()
    # res = cb.getAllMessages()
    cb.runReminder()

