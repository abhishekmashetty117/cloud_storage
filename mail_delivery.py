import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

config = configparser.ConfigParser()
config.read(os.path.join('configuration','mail.ini'))
 
port = config['DEFAULT']['mail_port']
smtp_server = config['DEFAULT']['mail_server']
mail_login = config['CREDENTIALS']['mail_username']
mail_password = config['CREDENTIALS']['mail_password']

sender_email = config['CREDENTIALS']['sender']
receiver_email = "mayuridurgad96@gmail.com"
subject = "Verify"
action_url = "www.google.com"
support_url = "www.mashetty.com"
mail_file = 'reset_password_mail.html'

def send_mail_to_user(sender_email,receiver_email,subject,mail_file,action_url,support_url,smtp_server,port,mail_login,mail_password):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    mail_file_path = os.path.join('templates','mail_templates',mail_file)    
    html_file = open(mail_file_path,'r')
    html_content = html_file.read()
    html_content = html_content.replace("{{action_url}}",action_url)
    html_content = html_content.replace("{{support_url}}",support_url)
    html_file.close()
    message.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(mail_login, mail_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

    print('Mail Sent')
