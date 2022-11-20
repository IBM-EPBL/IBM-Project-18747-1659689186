from flask import Flask
# from flask_mail import Mail
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from google_auth_oauthlib.flow import Flow
import ibm_db
import os
import pathlib


from flask import render_template, request, redirect, url_for, session

from pip._vendor import cachecontrol
from google.oauth2 import id_token
from random import randint
import google.auth.transport.requests
import requests
import ibm_db
import json

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



app = Flask(__name__)
# mail = Mail(app)

app.secret_key = b'\x84\xda1\x83@DUX\xf29%}Z<v\xdd'

app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

oauth = OAuth(app)
app.config['GOOGLE_CLIENT_ID'] = '91863464450-chmqoncg99unjfcet63ebab98fjlu8eg.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
app.config['REDIRECT_URI'] = '/gentry/auth'
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=['https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email', 'openid'],
    redirect_uri='http://127.0.0.1:5000/gentry/auth'
)

conn = None

## DB2 Database connectivity
try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2d46b6b4-cbf6-40eb-bbce-6251e6ba0300.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32328;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=nwn08287;PWD=zQNzuapvAUXeDLhx;PROTOCOL=TCPIP",'','')
    print("Successfully connected with db2")
except:
    print("Unable to connect: ", ibm_db.conn_errormsg())

# app.config['MAIL_SERVER']='smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'ibmntims@gmail.com'
# app.config['MAIL_PASSWORD'] = 'ibmteam#28'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)



config = app.config
GOOGLE_CLIENT_ID = config.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = config.get('REDIRECT_URI')


@app.route('/')
@app.route('/entry')
def entry():
    return render_template('entry.html')

@app.route('/recoverymail')
def recoverymail():
    return render_template('recoverymail.html')


@app.route('/dashboard')
def dashboard():

    userid = session['userid']

    products_stock = []
    sql = "SELECT * FROM product WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        products_stock.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    products_count = 0
    products_value = 0
    product_price = {}

    for product in products_stock:
        products_count += product["STOCKCOUNT"]
        products_value += (product["STOCKCOUNT"] * product["PRICE"])
        product_price[product["PRODID"]] = product["PRICE"]
   

    salesdata = []
    sql = "SELECT * FROM sales WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        salesdata.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    sales_count = 0
    sales_value = 0
   

    for sales in salesdata:
        if sales["PRODID"] in product_price.keys():
            sales_count += sales["UNIT"]
            sales_value += (sales["UNIT"] * product_price[sales["PRODID"]])


    return render_template("dashboard.html", products_stock=json.dumps(products_stock), salesdata=json.dumps(salesdata, default=str), products_count=products_count, products_value=products_value, sales_count=sales_count, sales_value=sales_value)


@app.route('/products')
def products():

    userid = session['userid']

    productlist = []
    sql = "SELECT * FROM product WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        productlist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    if productlist:
        return render_template("products.html", productlist=productlist)
    else:
        return render_template("products.html", productlist=[])

@app.route('/newproduct')
def newproduct():
    product = {
        'USERID': '',
        'PRODID': '',
        'PRODNAME': '',
        'CATEGORY': '',
        'BRAND': '',
        'PRICE': '',
        'STOCKCOUNT': ''
    }
    return render_template('productform.html', product= product)

@app.route('/people')
def peoples():

    userid = session['userid']

    peoplelist = []
    sql = "SELECT * FROM people WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        peoplelist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return render_template("people.html", peoplelist=peoplelist)


@app.route('/sales')
def sales():

    userid = session['userid']

    salelist = []
    sql = "SELECT * FROM sales WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        salelist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return render_template("sales.html", salelist=salelist)


@app.errorhandler(404)
def page_not_found(error):
    # status code of that response
    return render_template('page_not_found.html'), 404



@app.route("/adduser", methods=["POST"])
def adduser():
    username = request.form.get("username")
    userid = request.form.get("userid")
    password = request.form.get("password")

    sql = "SELECT * FROM user WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
        return render_template('entry.html', imsg="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO user VALUES (?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, userid)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.execute(prep_stmt)
        return render_template('entry.html', smsg="You are Successfully Registered with IMS, please login using your details")


@app.route("/login", methods=["POST"])
def login():
    userid = request.form.get("userid")
    password = request.form.get("password")
    sql = "SELECT * FROM user WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if not account:
        return render_template('entry.html', wmsg="You are not yet registered, please sign up using your details")
    else:
        if (password == account['PASSWORD']):
            session['username'] = account['USERNAME']
            session['userid'] = userid
            return redirect(url_for('dashboard'))
        else:
            return render_template('entry.html', msg="Please enter the correct password")

# New Method for Google Authentication
@app.route("/gentry")
def gentry():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/gentry/auth")
def gentry_auth():
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    userid = id_info.get('email')
    username = id_info.get('given_name')
    session['userid'] = userid
    session['username'] = username
    sql = "SELECT * FROM user WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if account:
        return redirect(url_for('dashboard'))
    else:
        password = "No_Password"
        insert_sql = "INSERT INTO user VALUES (?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, userid)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.execute(prep_stmt)
        return redirect(url_for('dashboard'))

# New Method end

@app.route('/sendotp', methods=['POST'])
def sendotp():
    if request.method == 'POST':
        userid = request.form.get("userid")
        sql = "SELECT * FROM user WHERE userid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, userid)
        ibm_db.execute(stmt)
        user = ibm_db.fetch_assoc(stmt)
        if not user:
            return render_template('entry.html', wmsg="You are not Signed up IMS")
        else: 
            email_from = 'ibmntims@gmail.com'
            epassword = 'hobseglbddzxypst'
            email_to = userid
            otp = randint(000000, 999999)

            email_message = MIMEMultipart()
            email_message['From'] = email_from
            email_message['To'] = email_to
            email_message['Subject'] = f'IMS OTP email'

            email_string = f'Report email - {otp}'

            # Connect to the Gmail SMTP server and Send Email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_from, epassword)
                server.sendmail(email_from, email_to, email_string)
        
            return render_template('verification.html', userid=userid, otp=otp)


@app.route('/verifyotp', methods=['POST'])
def verifyotp():
    if request.method == 'POST':
        otp = request.form.get('otp')
        cotp = request.form.get('cotp')
        userid = request.form.get('userid')

        if (otp == cotp):
            return render_template('changepswd.html', userid=userid)
        else:
            return redirect(url_for('recoverymail'))



@app.route('/updatepassword', methods=['POST'])
def update_password():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('pswd')
        sql = "UPDATE user SET password = ? WHERE userid =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, password)
        ibm_db.bind_param(stmt, 2, userid)
        ibm_db.execute(stmt)
        return render_template('entry.html', smsg="Password updated successfully")



@app.route('/addproducts', methods=["POST"])
def addproducts():
    if request.method == 'POST':
        userid = session['userid']
        prodid = request.form.get('prodid')
        prodname = request.form.get('prodname')
        category = request.form.get('category')
        brand = request.form.get('brand')
        price = request.form.get('price')
        stockcount = request.form.get('stockcount')

        sql = "SELECT * FROM product WHERE prodid =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, prodid)
        ibm_db.execute(stmt)
        product = ibm_db.fetch_assoc(stmt)

        if product: 
            update_sql = "UPDATE product SET USERID = ?, PRODID = ?, PRODNAME = ?, CATEGORY = ?, BRAND = ?,  PRICE = ?, STOCKCOUNT = ? WHERE prodid = ?"
            prep_stmt = ibm_db.prepare(conn, update_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, prodid)
            ibm_db.bind_param(prep_stmt, 3, prodname)
            ibm_db.bind_param(prep_stmt, 4, category)
            ibm_db.bind_param(prep_stmt, 5, brand)
            ibm_db.bind_param(prep_stmt, 6, price)
            ibm_db.bind_param(prep_stmt, 7, stockcount)
            ibm_db.bind_param(prep_stmt, 8, prodid)
            ibm_db.execute(prep_stmt)   
        else:
            insert_sql = "INSERT INTO product VALUES (?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, prodid)
            ibm_db.bind_param(prep_stmt, 3, prodname)
            ibm_db.bind_param(prep_stmt, 4, category)
            ibm_db.bind_param(prep_stmt, 5, brand)
            ibm_db.bind_param(prep_stmt, 6, price)
            ibm_db.bind_param(prep_stmt, 7, stockcount)
            ibm_db.execute(prep_stmt)
    return redirect(url_for('products'))



@app.route('/addsales', methods=["POST"])
def addsales():
    if request.method == 'POST':
        userid = session["userid"]
        customername = request.form.get('customername') 
        customer_email = request.form.get('customeremail')
        address = request.form.get('address')
        prodid = request.form.get('prodid')
        unit = request.form.get('unit')
        date = request.form.get('date')
        accept = request.form.get('accept')

        sql = "SELECT * FROM people WHERE customer_email =? AND userid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,customer_email)
        ibm_db.bind_param(stmt,2,session['userid'])
        ibm_db.execute(stmt)
        people = ibm_db.fetch_assoc(stmt)

        if people :
            pass
        else :
            insert_sql = "INSERT INTO people VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, customername)
            ibm_db.bind_param(prep_stmt, 3, customer_email)
            ibm_db.bind_param(prep_stmt, 4, address)
            ibm_db.execute(prep_stmt)

        sql = "SELECT stockcount, prodname from product WHERE prodid = ? AND userid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,prodid)
        ibm_db.bind_param(stmt,2,session['userid'])
        ibm_db.execute(stmt)
        stockcount = ibm_db.fetch_both(stmt)
        
        if(int(stockcount[0]) >= int(unit)):
            insert_sql = "INSERT INTO sales VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, prodid)
            ibm_db.bind_param(prep_stmt, 3, customer_email)
            ibm_db.bind_param(prep_stmt, 4, unit)
            ibm_db.bind_param(prep_stmt, 5, date)
            ibm_db.execute(prep_stmt)

            stockcount[0] = int(stockcount[0]) - int(unit)

            sql = "UPDATE product SET stockcount = ? WHERE prodid = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,stockcount[0])
            ibm_db.bind_param(stmt,2,prodid)
            ibm_db.execute(stmt)
            

            if(stockcount[0] <= 10):
      
                email1 = requests.get('https://raw.githubusercontent.com/Praveenkumar-S2805/privacy/main/email.html').text
                email2 = requests.get('https://raw.githubusercontent.com/Praveenkumar-S2805/privacy/main/email2.html').text

                email_from = 'ibmntims@gmail.com'
                epassword = 'hobseglbddzxypst'
                email_to = session['userid']
                # Create a MIMEMultipart class, and set up the From, To, Subject fields
                email_message = MIMEMultipart()
                email_message['From'] = email_from
                email_message['To'] = email_to
                email_message['Subject'] = f'IMS Low Stock Alert Message'

                alert = "<div style = \"text-align: center\"> <strong>Product ID : </strong>" + str(prodid) + "<br/> <strong>Product Name : <strong>" + str(stockcount[1]) + "<br/> <strong>Product Count : </strong>" + str(stockcount[0]) + "</div>"
                # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
                email_message.attach(MIMEText(email1, "html"))
                email_message.attach(MIMEText(alert, "html"))
                email_message.attach(MIMEText(email2, "html"))
                # Convert it as a string
                email_string = email_message.as_string()
                # Connect to the Gmail SMTP server and Send Email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(email_from, epassword)
                    server.sendmail(email_from, email_to, email_string)
        
            return redirect(url_for('sales'))   
        else:
            return redirect(url_for('sales'))

@app.route('/delete/<prodid>/<userid>')
def delete(prodid, userid):
    sql = "SELECT * FROM product WHERE prodid=? AND userid=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, prodid)
    ibm_db.bind_param(stmt, 2, userid)
    ibm_db.execute(stmt)
    product = ibm_db.fetch_row(stmt)
    if product:
        sql = "DELETE FROM product WHERE prodid=? AND userid=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, prodid)
        ibm_db.bind_param(stmt, 2, userid)
        ibm_db.execute(stmt)

    product = []
    sql = "SELECT * FROM product WHERE userid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        product.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    if product:
        return render_template("products.html", product=product, msg="Delete successfully")

@app.route('/edit/<prodid>/<userid>', methods=['GET', 'POST'])
def edit(prodid, userid):
    product = []
    sql = "SELECT * FROM product WHERE prodid=? AND userid=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, prodid)
    ibm_db.bind_param(stmt, 2, userid)
    ibm_db.execute(stmt)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        product.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    if product:
        return render_template("productform.html", product= product[0])
    return redirect(url_for('products'))


@app.route('/exit')
def exit():
    session.clear()
    session.pop('name', default=None)
    session.pop('email', default=None)
    return redirect("/entry")



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)