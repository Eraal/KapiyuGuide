
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offices')
def offices():
    return render_template('offices.html')

@app.route('/securityprivacy')
def securityprivacy():
    return render_template('securityprivacy.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)