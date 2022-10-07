from flask import Flask, render_template, request
import ibm_db

## Flask app configuration
app = Flask(__name__)

if (__name__ == "__main__ "):
    app.run(use_reloader=False)

## DB2 Database connectivity
try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=8e359033-a1c9-4643-82ef-8ac06f5107eb.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30120;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=bww66896;PWD=0YcAhCOWECLFnFbQ;PROTOCOL=TCPIP",'','')
except:
    print("Unable to connect: ", ibm_db.conn_errormsg())

## Application Routing
@app.route("/")
@app.route("/signin")
def signin() :
    return render_template('signin.html')

@app.route("/index")
def home() :
    return render_template('index.html')

@app.route("/about")
def about() :
    return render_template('about.html')

@app.route("/signup")
def signup():
    return render_template("signup.html")

## Registering user
@app.route("/adduser", methods=['GET', 'POST'])
def adduser() :
    if request.method == 'POST' :
        email = request.form['email']
        username = request.form['username']
        roll_number =  request.form['roll_number']
        password = request.form['password'] 

        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('signin.html', msg="You are already a member, please login using your details")
        else:
            insert_sql = "INSERT INTO user VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, email)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.bind_param(prep_stmt, 3, roll_number)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
    return render_template('index.html')

## Login user
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
       
        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            if(str(password) == str(account['PASSWORD']).strip()):
                return render_template('index.html')
            else:
                return render_template('signin.html', msg = "password is invalid")
        else:
            return render_template('signin.html', msg = "email is invalid")