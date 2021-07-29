from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_behind_proxy import FlaskBehindProxy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt


app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '9ef1d5a68754c1a8df1f196c00eb79c8'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(120), nullable=True)
    chats = db.Column(db.String(200), nullable=True) # eg: "1 2 3 4 5"
    profile_pic = db.Column(db.String(7), unique=True) # can just be hexidec

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class AllGroupChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chatname = db.Column(db.String(120), unique=True, nullable=False)
    num_users = db.Column(db.Integer, nullable=False)
    private = db.Column(db.Boolean, nullable=False)
    time_created = db.Column(db.DateTime)
    description = db.Column(db.String(120))
    # owner = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    def __repr__(self):
        return f"Chat_Room('{self.chatname}', '{self.num_users}', '{self.time_created}')" 

# Model for a generic chatroom message -- each message is linked to a chat room id
# class Message(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     chat_id = db.Column(db.Integer, db.ForeignKey('AllGroupChats.id'))
#     user_sent_id = db.Column(db.Integer, db.ForeignKey('User.id'), unique=False)
#     time_sent = db.Column(db.DateTime, unique=False, nullable=False)
#     content = db.Column(db.String(900), unique=False, nullable=False)

#     def __repr__(self):
#         return f"Message('{self.content}', '{self.time_sent}')"  

@app.route("/home")
@login_required
def home():
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():  # checks if entries are valid
        passwordhash = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        username = db.session.query(User.id).filter_by(
            username=form.username.data).first() is not None
        if username is False:
            mail = db.session.query(User.id).filter_by(
                email=form.email.data).first() is not None
            if mail is False:
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=passwordhash,
                    bio='', chats='')
                db.session.add(user)
                db.session.commit()
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('login'))  # if so - send to home page
            else:
                flash(f'That email is already taken please try another',
                      'danger')
                return redirect(url_for('register'))
        else:
            flash(f'That username is already taken please try another',
                  'danger')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = db.session.query(User.id).filter_by(
            username=form.username.data).first() is not None
        if username is True:
            password = db.session.query(
                User.password).filter_by(
                username=form.username.data).first()
            password = password[0]
            if bcrypt.check_password_hash(password, form.password.data):
                # on if checked, None if not checked
                remember = request.form.get('Remember')
                if remember == 'on':
                    remember = True
                else:
                    remember = False
                print(remember)
                flash(f'Logged in as {form.username.data}!', 'success')
                user = User.query.filter_by(
                    username=form.username.data).first()
                login_user(user, remember=remember)
                return redirect(url_for('home'))
            else:
                flash(f'Wrong password for {form.username.data}!', 'danger')
                return redirect(url_for('login'))
        else:
            flash(
                f'Account does not exist for {form.username.data}!',
                'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f'Logged out', 'success')
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


@app.route("/<chat_id>")
@login_required
def chat():
    return render_template('chat.html', name=current_user.username)


@app.route("/api/chat/<chat_id>")
def allUsersInChat(chat_id):
    # we can figure this out later
    users = User.query.all()
    userArray = []
    for user in users:
        userObj = {}
        userObj['id'] = user.id
        userObj['username'] = user.username
        userObj['email'] = user.email
        userObj['password'] = user.password
        userArray.append(userObj)
    return jsonify(userArray)


@app.route("/api/User/<get_user>")
def userdata(get_user):
    user = User.query.filter_by(id=get_user).first()
    userObj = {}
    userObj['id'] = user.id
    userObj['username'] = user.username
    userObj['email'] = user.email
    userObj['password'] = user.password
    return jsonify(userObj)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")