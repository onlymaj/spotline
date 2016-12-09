# Import smtplib for the actual sending function
import smtplib
import config
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Import the email modules we'll need
from email.mime.text import MIMEText


def sendMail(TO,SUBJ,CONT):
    msg = MIMEMultipart()
    msg['From'] = config.MSERVER_FR
    msg['To'] = TO
    msg['Subject'] = SUBJ
    msg.attach(MIMEText(CONT, 'plain'))
    try:
        server = smtplib.SMTP(config.MSERVER, config.MSERVER_PORT)
        server.starttls()
        server.login(config.MSERVER_UN, config.MSERVER_PW)
        text = msg.as_string()
        server.sendmail( config.MSERVER_UN, TO, text)
        server.quit()
        print "Sending mail to "+TO+  ' For ' + SUBJ + ' Successfully sent !'
    except Exception,e:
        print "Sending mail to "+TO+  ' For ' + SUBJ + ' Failed because ',e


    # Send the message via our own SMTP server, but don't include the
    # envelope header.
#    try:
#        server = smtplib.SMTP(config.MSERVER,config.MSERVER_PORT)
#        smtp.starttls()
#
#        server.login(config.MSERVER_UN,config.MSERVER_PW)
#        server.sendmail(fromMy, to,msg)
#        server.quit()
##        s = smtplib.SMTP(SERVER)
##        s.sendmail(FROM, [TO], msg.as_string())
#        print "Sending mail to "+TO+  ' For ' + SUBJ + ' Successfully sent !'
#    except Exception,e:
#        print "Sending mail to "+TO+  ' For ' + SUBJ + ' Failed . ',e
#    else:
#        s.quit()
#
#
