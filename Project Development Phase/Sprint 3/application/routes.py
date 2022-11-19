from application import app
from application import ibm_db
from application import conn
from application import mail
from flask import render_template, request, redirect, url_for, session
from flask_mail import Message
import requests
import ibm_db
import json

config = app.config
GOOGLE_CLIENT_ID = config.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = config.get('REDIRECT_URI')

@app.route('/')
@app.route('/entry')
def entry():
    return render_template('entry.html')
        
@app.route('/dashboard')
def dashboard():
    products_stock = []
    sql = "SELECT prodid, prodname, stockcount FROM product"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        products_stock.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    print("*********************************")
    print(products_stock)
    print("*********************************")

    salesdata = []
    sql = "SELECT * FROM sales"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        salesdata.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    print("*********************************")
    print(salesdata)
    print("*********************************")

    return render_template("dashboard.html", products_stock=json.dumps(products_stock), salesdata = json.dumps(salesdata, default=str))

@app.route('/people')
def peoples():
    peoplelist = []
    print(peoplelist)
    sql = "SELECT * FROM people"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        peoplelist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return render_template("people.html", peoplelist = peoplelist)
    

@app.route('/products')
def products():
    productlist = []
    sql = "SELECT * FROM product"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        productlist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
        
    if productlist:
        return render_template("products.html", productlist = productlist)
    else:
        return render_template("products.html", productlist = [])


@app.route('/exit')
def exit():
    session.clear()
    session.pop('name', default=None)
    session.pop('email', default=None)
    return redirect("/entry")
    

@app.errorhandler(404)
def page_not_found(error):
    # status code of that response
    return render_template('page_not_found.html'), 404



@app.route("/adduser", methods=["POST"])
def adduser():
    username = request.form.get("username")
    userid = request.form.get("userid")
    password = request.form.get("password")
    
    sql = "SELECT * FROM user WHERE username = ?" 
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
        return render_template('entry.html', msg="You are already a member, please login using your details")
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
    username = request.form.get("username")
    password = request.form.get("password")
    sql = "SELECT * FROM user WHERE username = ?" 
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if not account:
        return render_template('entry.html', msg="You are not yet registered, please sign up using your details")
    else:
        if(password == account['PASSWORD']):
            username = account['USERNAME']
            userid = account['USERID']
            
            session['username'] = username
            session['userid'] = userid
            return redirect(url_for('dashboard'))
        else:
            return render_template('entry.html', msg="Please enter the correct password")


#google authetication 
@app.route("/gentry")
def gentry():
    if request.args.get("next"):
        session["next"] = request.args.get("next")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?scope=https://www.googleapis.com/auth/userinfo.profile&access_type=offline&include_granted_scopes=true&response_type=code&redirect_uri=http://127.0.0.1:5000/gentry/auth&client_id={GOOGLE_CLIENT_ID}")

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

    r = requests.get(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={r.json()["access_token"]}').json()
    
    print("====================================================")
    print(r) 
    print("====================================================")

    # {'id': '106348779594867279670', 
    #   'email': 'veerammal3112@gmail.com',
    #    'verified_email': True, 
    # 'name': 'Veerammal S',
    #  'given_name': 'Veerammal',
    #  'family_name': 'S',
    #  'picture': 'https://lh3.googleusercontent.com/a/ALm5wu3zFDxNGRdpy8_z_GjCKe2ZyvaxGpxs6YoUduQb=s96-c', 
    # 'locale': 'en'}

    if r.get('email') == None:
        session['userid'] =  None
    else:
        session['userid'] = r['email']
    
    session['username'] = r['name']
    return redirect(url_for('dashboard'))

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
        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        user = ibm_db.fetch_assoc(stmt)
        print(user)
        if not user :
            return render_template('entry.html', msg="You are not Signed up IMS")
        else :
            password = user['PASSWORD']
            msg = Message('IMS PASSWORD',sender ='2k19cse069@kiot.ac.in', recipients = [email])
            msg.body = 'Use This Password for login purposes. Password = ' + password
            mail.send(msg)
            print("The mail was sent successfully")
            return render_template('entry.html')

@app.route('/addpeoples', methods=["POST"])
def addpeoples():
    if request.method == 'POST':
        userid = request.form.get('userid')
        customername = request.form.get('customername')
        customer_email = request.form.get('customeremail')
        address = request.form.get('address')
        
        sql = "SELECT * FROM people WHERE customer_email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,customer_email)
        ibm_db.execute(stmt)
        people = ibm_db.fetch_assoc(stmt)

        if people :
            return render_template('peoples.html', msg="You are a Customer of IMS")
        else :
            insert_sql = "INSERT INTO people VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, customername)
            ibm_db.bind_param(prep_stmt, 3, customer_email)
            ibm_db.bind_param(prep_stmt, 4, address)
            ibm_db.execute(prep_stmt)
    
    return render_template('peoples.html',msg="peoples added successfully")

@app.route('/addsales', methods=["POST"])
def addsales():
    if request.method == 'POST':
        userid = request.form.get('userid')
        prodid = request.form.get('prodid')
        customer_email = request.form.get('customer_email')
        unit = request.form.get('unit')
        date = request.form.get('date')
        
        sql = "SELECT * FROM sales WHERE customer_email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,customer_email)
        ibm_db.execute(stmt)
        sales = ibm_db.fetch_assoc(stmt)

        if sales :
            return render_template('sales.html', msg="You already made a Sales")
        else :
            insert_sql = "INSERT INTO sales VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, prodid)
            ibm_db.bind_param(prep_stmt, 3, customer_email)
            ibm_db.bind_param(prep_stmt, 4, unit)
            ibm_db.bind_param(prep_stmt, 5, date)
            ibm_db.execute(prep_stmt)
    
    return render_template('sales.html',msg="Sales added successfully")

@app.route('/sales')
def sales():
    salelist = []
    sql = "SELECT * FROM sales"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        salelist.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)   
    return render_template("sales.html", salelist = salelist)

@app.route('/addproducts', methods=["POST"])
def addproducts():
    if request.method == 'POST':
        userid = request.form.get('userid')
        prodid = request.form.get('prodid')
        prodname = request.form.get('prodname')
        category = request.form.get('category')
        brand = request.form.get('brand')
        description = request.form.get('description')
        price = request.form.get('price')
        stockcount = request.form.get('stockcount')

        sql = "SELECT * FROM product WHERE userid =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,userid)
        ibm_db.execute(stmt)
        product = ibm_db.fetch_assoc(stmt)

        if product :
            return render_template('products.html', msg="You already have a product")
        else :
            insert_sql = "INSERT INTO product VALUES (?,?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, userid)
            ibm_db.bind_param(prep_stmt, 2, prodid)
            ibm_db.bind_param(prep_stmt, 3, prodname)
            ibm_db.bind_param(prep_stmt, 4, category)
            ibm_db.bind_param(prep_stmt, 5, brand)
            ibm_db.bind_param(prep_stmt, 6, description)
            ibm_db.bind_param(prep_stmt, 7, price)
            ibm_db.bind_param(prep_stmt, 8, stockcount)
            ibm_db.execute(prep_stmt)
    return render_template('products.html',msg="product added successfully")
