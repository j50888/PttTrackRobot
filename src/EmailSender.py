#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header

class Sender:
    def __init__(self, jsonGmailParams):
        self.mailUser= jsonGmailParams['smtp']['account']
        self.mailPass= jsonGmailParams['smtp']['password']
        self.mailRecevier = jsonGmailParams["receiverEmailAddress"]

    def notifyClient(self, jsonArticle, taskType):
        sender = 'from@PttTracker.com'
        receivers = [self.mailRecevier]

        strMessage = 'Task: ' + taskType + '\n' + \
                     'link: ' + jsonArticle['url'] + '\n\n\n' + \
                     '-------------------------------------\n' + \
                     'This email is sent from PttTrackRobot'

        message = MIMEText(strMessage, 'plain', 'utf-8')
        message['From'] = Header("PttTrackRobot", 'utf-8')
        message['To'] =  Header("User", 'utf-8')

        subject = '[PttTracker] Article ' + jsonArticle['article_title'] + ' tracked!'
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.starttls()
            smtpObj.login(self.mailUser, self.mailPass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print ("Send to", self.mailRecevier)
        except smtplib.SMTPException:
            print ("Error: 无法发送邮件")
