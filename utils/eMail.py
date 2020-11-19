import smtplib
from email.message import EmailMessage
import configparser
import os

class Email:

    def __init__(self):
        # read configurations like gmail id and password
        cfg = configparser.ConfigParser()
        cfgPath = os.path.dirname(__file__)
        cfgFileName = os.path.join(cfgPath, 'config.ini')
        self.bodyTextFile = os.path.join(cfgPath, 'EmailBody.txt')
        cfg.read(cfgFileName)
        self.userName = cfg['email']['username']
        self.password = cfg['email']['password']

    def createMailBody(self, location, restaurantDataBody):
        self.subject=" Restaurant recommendations in "+ location

        self.emailTxt = ""
        with open(self.bodyTextFile, 'r') as f:
            for line in f.readlines():
                self.emailTxt += line

        self.emailTxt = self.emailTxt % (restaurantDataBody)

    def getmsgInstance(self, to_add):
        msg = EmailMessage()
        msg.set_content(self.emailTxt)
        msg['Subject'] = self.subject
        msg['From'] = self.userName
        msg['To'] = to_add
        return msg

    def sendMail(self, sendAddress, location, restaurantDataBody):
        retVal = 0
        try:
            self.createMailBody(location, restaurantDataBody)
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.userName, self.password)
            server.send_message(self.getmsgInstance(sendAddress))
            server.quit()
        except smtplib.SMTPAuthenticationError as e:
            print(str(e))
            retVal = -1

        return retVal


if __name__ == '__main__':
    resDataBody = 'Test Mail'
    location = 'Bangalore'
    EmailI =Email()
    retVal = EmailI.sendMail('sdb2030@gmail.com', location, resDataBody)
    print(retVal)
