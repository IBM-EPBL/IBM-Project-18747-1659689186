from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/Login')
def Login():
    return render_template('Login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    return render_template('signin.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/products', methods=['GET', 'POST'])
def products():
    return render_template('products.html')


@app.route('/peoples', methods=['GET', 'POST'])
def peoples():
    return render_template('peoples.html')


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    return render_template('reports.html')


@app.errorhandler(404)
def page_not_found(error):
    # status code of that response
    return render_template('page_not_found.html'), 404
