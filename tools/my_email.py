#! /usr/bin/python
# coding: utf-8
# -*- encoding: gb2312 -*-
# reference: https://imapclient.readthedocs.io/en/master/

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imapclient import IMAPClient, SEEN
from smtplib import SMTP
import email
from email.header import decode_header
from email.utils import parseaddr
from lxml import etree


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def guess_charset(msg):
    # 先从msg对象获取编码
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，从Content-Type字段获取
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos+8:].strip('\"\'')
    return charset


class Mailer(object):
    def __init__(self, mode='receive'):
        if mode == 'send':
            self.server = SMTP('smtp.163.com')
        else:
            self.server = IMAPClient('imap.163.com')

    def login(self, email='', pswd=''):
        self.email = email
        self.server.login(email, pswd)

    def is_pku_mail(self, msg):
        """判断邮件是否是想要的测试邮件，发件人是"""
        print msg['Date']
        msg_from = msg.get('From')
        hdr, addr = parseaddr(msg_from)
        name = decode_str(hdr)
        msg_subject = decode_str(msg.get('Subject'))
        print '%s <%s> : %s' % (name, addr, msg_subject)
        if name == '' and addr == '':
            return True
        return False

    def parse_mail(self, msg):
        """解析邮件内容，"""
        if msg.is_multipart():
            parts = msg.get_payload()
            for i, part in enumerate(parts):
                self.parse_mail(part)
        else:
            content_type = msg.get_content_type()
            if content_type in ['text/plain', 'text/html']:
                # 纯文本或html内容
                content = msg.get_payload(decode=True)
                charset = guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                    html_ct = etree.HTML(content)
                    verify_url = html_ct.xpath('')
                    if verify_url:
                        self.set_seen_flag()
            else:
                # 不是纯文本，作为附件处理
                print 'Attachment: %s' % content_type

    def set_seen_flag(self):
        """把邮件标记为已读"""
        self.server.set_flags(self.msg_id, SEEN)

    def receive_email(self):
        """选择收件箱，搜索未读的邮件"""
        self.server.select_folder('INBOX')
        unseen = self.server.search('UNSEEN')
        msg_results = self.server.fetch(unseen, 'BODY.PEEK[]')
        for msg_id, msg_str in msg_results.items():
            msg = email.message_from_string(msg_str['BODY[]'])
            if self.is_pku_mail(msg):
                # 是pku测试邮件才解析邮件内容
                self.msg_id = msg_id
                self.parse_mail(msg)

    def send_mail(self, subject, file_name, mail_to, text=''):
        main_msg = email.MIMEMultipart.MIMEMultipart()
        ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        text_msg = email.MIMEText.MIMEText(text, _charset="utf-8")
        main_msg.attach(text_msg)
        file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
        with open(file_name, 'rb') as data:
            file_msg.set_payload(data.read())
        email.Encoders.encode_base64(file_msg)
        file_msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_name))
        main_msg.attach(file_msg)
        main_msg['From'] = self.email
        main_msg['To'] = mail_to
        main_msg['Subject'] = subject
        main_msg['Date'] = email.Utils.formatdate()
        try:
            self.server.sendmail(self.email, mail_to, main_msg.as_string())
        finally:
            self.server.quit()

    def logout(self):
        self.server.logout()
