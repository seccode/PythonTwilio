import pytz
import time
import datetime
import schedule
import numpy as np
from collections import defaultdict
from urllib.parse import urlencode
from twilio.rest import Client, TwilioRestClient
from twilio.twiml.voice_response import VoiceResponse, Gather
import config as cfg


class Reminder():
    def __init__(self,messenger):
        self.messenger = messenger
        self.responded = False

    def checkResponse(self,since=4):
        res = self.messenger.getReceivedMessages(since=since)
        for response in res[cfg.contacts["Marina"]]:
            if response.lower() in cfg.acceptedResponses:
                return True
        return False

    def initialMessage(self):
        self.responded = False
        self.messenger.sendMessage(body=np.random.choice(
            cfg.initialMessages), contact="Marina")
        return

    def secondaryMessage(self):
        responded = self.checkResponse(since=4)
        if not responded:
            self.messenger.sendMessage(body=np.random.choice(
                cfg.reminders),contact="Marina")
        else:
            self.responded = True
            self.messenger.sendMessage(body=np.random.choice(
                cfg.responses), contact="Marina")
        return

    def tertiaryMessage(self):
        if self.responded:
            return
        newResponded = self.checkResponse(since=8)
        if not newResponded:
            self.messenger.sendMessage(body=np.random.choice(
                cfg.reminders), contact="Marina")
        else:
            self.messenger.sendMessage(body=np.random.choice(
                cfg.responses),contact="Marina")
        return
    
    def run(self):
        schedule.every().day.at("10:00").do(self.initialMessage)
        schedule.every().day.at("14:00").do(self.secondaryMessage)
        schedule.every().day.at("18:00").do(self.tertiaryMessage)

        while True:
            schedule.run_pending()
            time.sleep(58)
        return


class AutomatedMessenger():
    def __init__(self):
        self.account_sid = cfg.account_sid
        self.auth_token = cfg.auth_token
        self.client = Client(self.account_sid, self.auth_token)
        self.number = cfg.number
        self.contacts = cfg.contacts

    def runReminder(self):
        reminder = Reminder(self)
        reminder.run()

    def makeCall(self, message="", contact=None, number=None, url="https://twimlets.com/message?"):
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

    def getReceivedMessages(self, since=None):
        '''
        Return dictionary of messages
            - Key: Contact
            - Value: Received Message List
        '''
        if since:
            ref_time = datetime.datetime.combine(
                datetime.date.today(), datetime.time(15, 0)).replace(tzinfo=pytz.utc)

        ret = defaultdict(list)
        messages = self.client.messages.list()
        for record in messages:
            if record.to == self.number:
                if since:
                    diff = record.date_sent - ref_time
                    if diff > datetime.timedelta(seconds=0) and diff < datetime.timedelta(hours=since):
                        ret[record.from_].append(record.body)
                else:
                    ret[record.from_].append(record.body)
        return ret

    def sendMessage(self, body='', contact=None, number=None):
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
        print("Sent '{}' to {}".format(body, to_))
        return message


if __name__ == "__main__":
    cb = AutomatedMessenger()

    # res = cb.getReceivedMessages(since=5)
    # res = cb.getAllMessages()

    # for key, value in res.items():
    #     print(key)
    #     for v in value:
    #         print(v)
    #     print("\n")

    cb.runReminder()
