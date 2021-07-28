from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
# from forms import RegistrationForm, LoginForm, Submit
from flask_sqlalchemy import SQLAlchemy
from flask_behind_proxy import FlaskBehindProxy

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '9ef1d5a68754c1a8df1f196c00eb79c8'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")