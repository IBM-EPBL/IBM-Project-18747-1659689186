from flask import Flask, render_template, request, redirect, url_for, session, redirect
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)

oauth = OAuth(app)

app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GOOGLE_CLIENT_ID'] = "91863464450-chmqoncg99unjfcet63ebab98fjlu8eg.apps.googleusercontent.com"
app.config['GOOGLE_CLIENT_SECRET'] = "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"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

google = oauth.register(
    
    name = 'google',
    client_id = app.config["GOOGLE_CLIENT_ID"],
    client_secret = app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs = {'scope': 'openid email profile'},
    
)

# Google login route
@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


# Google authorize route
@app.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = oauth.google.authorize_access_token()
    resp = google.get('userinfo').json()
    print(f"\n{resp}\n")
    return "You are successfully signed in using google"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/entry')
def entry():
    return render_template('entry.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/peoples')
def peoples():
    return render_template('peoples.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.errorhandler(404)
def page_not_found(error):
    # status code of that response
    return render_template('page_not_found.html'), 404
