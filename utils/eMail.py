import smtplib
from email.message import EmailMessage
import configparser
import os

class Email:

    def __init__(self, restaurantListFile, location):
        self.restaurantListFile = restaurantListFile
        self.location = location
        # read configurations like gmail id and password
        cfg = configparser.ConfigParser()
        cfgPath = os.path.dirname(__file__)
        cfgFileName = os.path.join(cfgPath, 'config.ini')
        bodyTextFile = os.path.join(cfgPath, 'EmailBody.txt')
        cfg.read(cfgFileName)
        self.userName = cfg['email']['username']
        self.password = cfg['email']['password']
        self.createMailBody(restaurantListFile, bodyTextFile)

    def createMailBody(self, restaurantrecommendationfileName, bodyTextFileName):
        self.subject=" Restaurant recommendations in "+ self.location
        body = ""
        with open(restaurantrecommendationfileName, 'r') as f:
            for line in f.readlines():
                body += line

        self.emailTxt = ""
        with open(bodyTextFileName, 'r') as f:
            for line in f.readlines():
                self.emailTxt += line

        self.emailTxt = self.emailTxt % (body)

    def getmsgInstance(self, to_add):
        msg = EmailMessage()
        msg.set_content(self.emailTxt)
        msg['Subject'] = self.subject
        msg['From'] = self.userName
        msg['To'] = to_add
        return msg

    def sendMail(self, sendAddress):
        retVal = 0
        try:
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
    fileName = 'D:\sample.txt'
    location = 'Bangalore'
    EmailI =Email(fileName, location)
    retVal = EmailI.sendMail('sdb2030@gmail.com')
    print(retVal)
