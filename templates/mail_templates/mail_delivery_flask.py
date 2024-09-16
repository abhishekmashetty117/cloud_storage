# importing libraries 
from flask import Flask 
from flask_mail import Mail, Message 
import configparser

config = configparser.ConfigParser()
config.read('mail.ini')

app = Flask(__name__) 
mail = Mail(app) # instantiate the mail class 

# configuration of mail 
app.config['MAIL_SERVER']= config['DEFAULT']['MAIL_SERVER']
app.config['MAIL_PORT'] = config['DEFAULT']['MAIL_PORT']
app.config['MAIL_USERNAME'] = config['CREDENTIALS']['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = config['CREDENTIALS']['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = config['DEFAULT']['MAIL_USE_TLS']
app.config['MAIL_USE_SSL'] = config['DEFAULT']['MAIL_USE_SSL']
mail = Mail(app) 

subject = 'Password Reset Request'
sender = config['CREDENTIALS']['sender']
recipient = ['mayuridurgad96@gmail.com']
reply_to = config['CREDENTIALS']['reply_to'] 
content = 'Hello Flask message sent from Flask-Mail'
##subject,sender,content,*recipient
##html=render_template(template_name_or_list="otp.html", **context)
@app.route('/', methods = ['GET'])
def send_mail_to_users():
    msg = Message( 
		subject, 
		sender = sender, 
		recipients = [*recipient],
                reply_to = reply_to,
                html="""<h1 style="color:blue;">Testing mail</h1>"""
		) 
    msg.body = content
    mail.send(msg) 
    return 'Sent'

if __name__ == '__main__': 
    app.run(debug = True) 
