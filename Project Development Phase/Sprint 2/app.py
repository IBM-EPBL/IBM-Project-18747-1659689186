from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import requests
import ibm_db
from pyzbar import pyzbar
import cv2

def draw_barcode(decoded, image):
    # n_points = len(decoded.polygon)
    # for i in range(n_points):
    #     image = cv2.line(image, decoded.polygon[i], decoded.polygon[(i+1) % n_points], color=(0, 255, 0), thickness=5)
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top), 
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image

def decode(image):
    # decodes all barcodes from an image
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        # draw the barcode
        image = draw_barcode(obj, image)
        # print barcode type & data
        print("Type:", obj.type)
        print("Data:", obj.data)
        print()

    return image

GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
REDIRECT_URI = '/gentry/auth'

app = Flask(__name__)
# mail = Mail(app) # instantiate the mail class
app.secret_key = b'\x84\xda1\x83@DUX\xf29%}Z<v\xdd'

app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
oauth = OAuth(app)

conn = None

## DB2 Database connectivity
try:
    conn = ibm_db.connect("",'','')
    print("Successfully connected with db2")
except:
    print("Unable to connect: ", ibm_db.conn_errormsg())

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
@app.route('/entry')
def entry():
    return render_template('entry.html')
        
@app.route('/dashboard')
def dashboard():
    # check if the users exist or not
    # if not session.get("name"):
    #     # if not there in the session then redirect to the login page
    #     return redirect("/entry")
    # if current_user.is_autheticated and session['logged_in']:
    # if  session['logged_in']:

    # for view list of sales
    salelist = []
    print(salelist)
    sql = "SELECT * FROM sales"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        salelist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    if salelist:
        return render_template("dashboard.html", salelist = salelist)
    # return render_template('dashboard.html')    
    # else:
    #     return render_template('entry.html')

#google authetication 
@app.route("/gentry")
def gentry():
    # if request.args.get("next"):
    #     session["next"] = request.args.get("next")
    return redirect(f"")

@app.route("/gentry/auth")
def gentry_auth():
    r = requests.post("https://oauth2.googleapis.com/token", 
    data={
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": request.args.get("code"),
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:5000/gentry/auth"
    })

    r = requests.get(f'').json()
    if r.get('email') == None:
        session['email'] =  None
    else:
        session['email'] = r['email']
    
    session['name'] = r['name']
    return redirect(url_for('dashboard'))

@app.route('/exit')
def exit():
    session.clear()
    session.pop('name', default=None)
    session.pop('email', default=None)
    return redirect("/entry")

@app.route('/recoverymail')
def recoverymail():
    # print("Inside recoverymail")
    # msg = Message('Hello',sender ='ims@gmail.com',recipients = ['ims@gmail.com'])
    # msg.body = 'Hello Flask message sent from Flask-Mail'
    # mail.send(msg)
    return render_template('recoverymail.html')

@app.route('/sendpassword', methods=['POST'])
def sendpassword():
    if request.method == 'POST':
        email = request.form.get('email')
        print("inside sendotp")
        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        user = ibm_db.fetch_assoc(stmt)
        print("============================================")
        print(user)
        if not user :
            return render_template('entry.html', msg="You are not Signed up IMS")
        else :
            print("***************************")
            print(user['PASSWORD'])
            password = user['PASSWORD']
            msg = Message('IMS PASSWORD',sender ='ims@gmail.com',recipients = [email])
            msg.body = 'Use This Password for login purposes. Password = ' + password
            mail.send(msg)
            print("The mail was sent successfully")
            return render_template('entry.html')

@app.route('/addpeoples', methods=["POST"])
def addpeoples():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        
        sql = "SELECT * FROM people WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        people = ibm_db.fetch_assoc(stmt)

        if people :
            return render_template('peoples.html', msg="You are a Customer of IMS")
        else :
            insert_sql = "INSERT INTO people VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, address)
            ibm_db.execute(prep_stmt)
    
    return render_template('peoples.html',msg="peoples added successfully")

@app.route('/peoples')
def peoples():
    peoplelist = []
    print(peoplelist)
    sql = "SELECT * FROM people"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        peoplelist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    if peoplelist:
        return render_template("peoples.html", peoplelist = peoplelist)

@app.route('/addsales', methods=["POST"])
def addsales():
    if request.method == 'POST':
        id = request.form.get('id')
        email = request.form.get('email')
        unit = request.form.get('unit')
        date = request.form.get('date')

        
        sql = "SELECT * FROM sales WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        sales = ibm_db.fetch_assoc(stmt)

        if sales :
            return render_template('dashboard.html', msg="You already made a Sales")
        else :
            insert_sql = "INSERT INTO sales VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, id)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, unit)
            ibm_db.bind_param(prep_stmt, 4, date)
            ibm_db.execute(prep_stmt)
    
    return render_template('dashboard.html',msg="Sales added successfully")
    
@app.route('/reports')
def reports():
    return render_template('reports.html')    

@app.errorhandler(404)
def page_not_found(error):
    # status code of that response
    return render_template('page_not_found.html'), 404

@app.route("/adduser", methods=["POST"])
def adduser():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    
    sql = "SELECT * FROM user WHERE email = ?" 
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
        return render_template('entry.html', msg="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO user VALUES (?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.bind_param(prep_stmt, 2, name)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.execute(prep_stmt)
        return render_template('entry.html', msg="You are Successfully Registered with IMS, please login using your details")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    sql = "SELECT * FROM user WHERE email = ?" 
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if not account:
        return render_template('entry.html', msg="You are not yet registered, please sign up using your details")
    else:
        if(password == account['PASSWORD']):
            email = account['EMAIL']
            name = account['NAME']
            
            session['name'] = name
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('entry.html', msg="Please enter the correct password")

@app.route('/addproducts', methods=["POST"])
def addproducts():
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        category = request.form.get('category')
        brand = request.form.get('brand')
        description = request.form.get('description')
        price = request.form.get('price')
        count = request.form.get('count')

        sql = "SELECT * FROM product WHERE name =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,id)
        ibm_db.execute(stmt)
        product = ibm_db.fetch_assoc(stmt)

        if product :
            return render_template('products.html', msg="You already have a product")
        else :
            insert_sql = "INSERT INTO product VALUES (?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, id)
            ibm_db.bind_param(prep_stmt, 2, name)
            ibm_db.bind_param(prep_stmt, 3, category)
            ibm_db.bind_param(prep_stmt, 4, brand)
            ibm_db.bind_param(prep_stmt, 5, description)
            ibm_db.bind_param(prep_stmt, 6, price)
            ibm_db.bind_param(prep_stmt, 7, count)
            ibm_db.execute(prep_stmt)
        return render_template('products.html',msg="product added successfully")

@app.route('/products')
def products():
    productlist = []
    print(productlist)
    sql = "SELECT * FROM product"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        productlist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
        
    if productlist:
        return render_template("products.html", productlist = productlist)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
    cap = cv2.VideoCapture(0)
    while True:
        # read the frame from the camera
        _, frame = cap.read()
        # decode detected barcodes & get the image
        # that is drawn
        # frame, decoded_objects = decode(frame)
        frame =  decode(frame)
        # show the image in the window
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    
