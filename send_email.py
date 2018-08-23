#!/usr/bin/env python
# _*_ coding: utf-8 _*_
__author__ = 'djk'
__date__ = '18-8-23 下午2:27'


import os
import smtplib
import mimetypes

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def _attachFile(path):
    #来自官方文档
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    filename = os.path.split(path)[1]
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        fp = open(path)
        # Note: we should handle calculating the charset
        msgFile = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'image':
        fp = open(path, 'rb')
        msgFile = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
        msgFile.add_header('Content-ID', '<0>')
        msgFile.add_header('X-Attachment-Id', '0')
    elif maintype == 'audio':
        fp = open(path, 'rb')
        msgFile = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(path, 'rb')
        msgFile = MIMEBase(maintype, subtype)
        msgFile.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        encoders.encode_base64(msgFile)
    # Set the filename parameter
    msgFile.add_header('Content-Disposition', 'attachment', filename=filename)
    return msgFile

def send_email():
    #发件人邮箱，密码，SMTP服务器地址，收件人邮箱，SMTP默认端口25
    # 发件人名称， 收件人名称，标题，正文，附件所在文件夹，附件
    from_addr = ''
    password = ''
    smtp_server = ''
    to_addr = ['', '']
    port = 25 
    from_user = ''
    to_user = ''
    subject = ''
    content = ''
    directory = ''
    attachFile = ''

    #构建邮件
    msg = MIMEMultipart('alternative')
    msg['From'] = _format_addr('%s<%s>' % (from_user, from_addr))
    msg['To'] = ','.join(to_addr)
        # _format_addr('%s<%s>' % (','.join(to_addr), to_addr))
    msg['Subject'] = Header(subject, 'utf-8').encode()

    #邮件内容
    #邮件正文，纯文本显示
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    #邮件正文，HTML显示
    msg.attach(MIMEText('<html><body><h1>%s</h1>' % content
                +'<p>send by <a href="http://www.python.org">Python</a>...</p>'
                +'<p><img src="cid:0"></p>'
                +'</body></html>', 'html', 'utf-8'))
    #邮件附件，单个文件
    msgFile = _attachFile(attachFile)
    msg.attach(msgFile)
    #邮件附件，文件夹
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        msgPath = _attachFile(path)
        msg.attach(msgPath)

    #邮件发送
    server = smtplib.SMTP(smtp_server, port)
    # server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()

send_email()
