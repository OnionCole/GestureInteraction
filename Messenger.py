import requests

class Messenger:

    def __init__(self, contact, msg):
        self.contact = contact
        self.msg = msg
        self.send()

    def send(self):
        response = requests.post('https://events-api.notivize.com/applications/e8d7d50f-c335-4047-a250-3b8dfefb0696/event_flows/ecf05920-0d0a-4877-818b-717c82c49566/events', json={"contact": self.contact, "msg": self.msg, "signal_present": True, "signal_processor": ""})
        print(response)
