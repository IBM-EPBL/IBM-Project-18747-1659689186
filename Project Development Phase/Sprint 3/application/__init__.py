from flask import Flask
from flask_mail import Mail
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import ibm_db

app = Flask(__name__)

app.secret_key = b'\x84\xda1\x83@DUX\xf29%}Z<v\xdd'

app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

oauth = OAuth(app)
app.config['GOOGLE_CLIENT_ID'] = '91863464450-chmqoncg99unjfcet63ebab98fjlu8eg.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
app.config['REDIRECT_URI'] = '/gentry/auth'

conn = None

## DB2 Database connectivity
try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2d46b6b4-cbf6-40eb-bbce-6251e6ba0300.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32328;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=nwn08287;PWD=zQNzuapvAUXeDLhx;PROTOCOL=TCPIP",'','')
    print("Successfully connected with db2")
except:
    print("Unable to connect: ", ibm_db.conn_errormsg())

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '2k19cse069@kiot.ac.in'
app.config['MAIL_PASSWORD'] = 'Harshini@3112'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

from application import routes