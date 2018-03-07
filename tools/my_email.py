#! /usr/bin/python
# coding: utf-8
# -*- encoding: gb2312 -*-
# reference: https://imapclient.readthedocs.io/en/master/

from imapclient import IMAPClient
import email


class MailRobot(object):
    def __init__(self, host='imap.163.com'):
        self.server = IMAPClient(host)

    def login(self, username, password):
        print self.server.login(username, password)

    def receive_email(self):
        self.server.select_folder(u'INBOX')
        result = self.server.search(['FROM', 'newsletter@e.topcashback.com'])
        for msgid, data in self.server.fetch(result, ['BODY.PEEK[]']).items():
            message = email.message_from_string(
                data['BODY[]'])  # data.keys() ['SEQ', 'BODY[]']
            subject, coding = email.header.decode_header(message['Subject'])[0]
            subject = subject.decode(coding)
            sender = email.header.decode_header(message['From'])
            print subject, sender
            maintype = message.get_content_maintype()
            if maintype == 'multipart':
                payloads = message.get_payload()
                for payload in payloads:
                    if payload.get_content_maintype() == 'text':
                        print payload.get_payload(decode=True)
            elif maintype == 'text':
                print message.get_payload(decode=True)
        print self.server.logout()


if __name__ == '__main__':
    mail_robot = MailRobot()
    mail_robot.login('18367811193@163.com', '')
    mail_robot.receive_email()
