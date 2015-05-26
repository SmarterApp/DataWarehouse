'''
Created on May 5, 2015

@author: tosako
'''
from email.mime.text import MIMEText
import smtplib


def sendmail(mail_server, mail_port, mail_from, mail_to, mail_return_path, mail_subject, aws_mail_username, aws_mail_password, mail_content):
    if mail_server is not None and mail_server != 'None':
        message = MIMEText(mail_content)
        message["Subject"] = mail_subject
        message["From"] = mail_from
        message["Return-Path"] = mail_from if mail_return_path is None else mail_return_path
        message["To"] = mail_to

        with smtplib.SMTP_SSL(mail_server, mail_port) as mail:
            mail.login(aws_mail_username, aws_mail_password)
            mail.send_message(message)
            mail.quit()
            return True
    return False
