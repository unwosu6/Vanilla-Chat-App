from flask import Flask, render_template, url_for, flash, redirect, request, \
    jsonify
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_behind_proxy import FlaskBehindProxy
from flask_login import UserMixin, LoginManager, login_user, logout_user, \
    current_user, login_required
from flask_bcrypt import Bcrypt
import pickle
from imgur import upload_img
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '9ef1d5a68754c1a8df1f196c00eb79c8'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.config['UPLOAD_FOLDER'] = 'temp'
app.config['MAX_CONTENT_PATH']= '100000000'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(20), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(120), nullable=True)
    # eg: "1 2 3 4 5" -- we will attempt a pickle obj
    chats = db.Column(db.PickleType, nullable=False)
    profile_pic = db.Column(db.String(120), unique=True)  # can just be hexidec
    Message = db.relationship("Message", backref="user", lazy=True)
    AllGroupChats = db.relationship("AllGroupChats", backref="user", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class AllGroupChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chatname = db.Column(db.String(120), unique=True, nullable=False)
    num_users = db.Column(db.Integer, nullable=False)
    private = db.Column(db.Boolean, nullable=False)
    time_created = db.Column(db.DateTime)
    description = db.Column(db.String(120))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    Message = db.relationship("Message", backref="all_group_chats", lazy=True)
    User = db.relationship("User", foreign_keys=[owner])

    def __repr__(self):
        return (
            f"Chat_Room('{self.chatname}', '{self.num_users}',"
            f"'{self.time_created}')"
        )


# Model for a generic chatroom message -- each message is linked to a chat
# room id
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('all_group_chats.id'))
    user_sent_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        unique=False)
    time_sent = db.Column(db.DateTime, unique=False, nullable=False)
    content = db.Column(db.String(900), unique=False, nullable=False)
    User = db.relationship("User", foreign_keys=[user_sent_id])
    AllGroupChats = db.relationship("AllGroupChats", foreign_keys=[chat_id])

    def __repr__(self):
        return f"Message('{self.content}', '{self.time_sent}')"


@app.route("/home")
@login_required
def home():
    return render_template('home.html')


@app.route("/chats")
def chats():
    return render_template('chats.html')


@app.route("/about")
def about():
    return render_template('about.html')


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
                file = "pickles/" + form.username.data + "-chats.p"
                f = open(file, "w+")
                f.close()
                with open(file, 'wb') as handle:
                    pickle.dump([0], handle)
                    print("created pickle")
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=passwordhash,
                    bio='', chats=file)
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
    return render_template('profile.html', current_user=current_user)


@app.route("/<chat_id>")
@login_required
def chat(chat_id):
    return render_template(
        'chat.html',
        chat_id=chat_id,
        name=current_user.username)


@app.route("/edit_profile", methods=['POST','GET'])
@login_required
def edit_profile():
    if request.method == 'POST':
        f = request.files['files']
        print(f)
        print(type(f))
        filename = secure_filename(f.filename)
        print(filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(upload_img(filename))
#         print(upload_img(f))
#         print(type(profile_picture))
#         if profile_picture is not None:
#             print(profile_picture)
    return render_template('edit_profile.html')

@app.route("/api/profile/<user_id>")
def usersPublicChats(user_id):
    user = User.query.filter_by(id=user_id).first()
    public_chat_list = pickle.load(user.chats, "rb")
    chats = AllGroupChats.query.filter_by(private=False).all()
    chats_array = []
    for chat in chats:
        if chat.chat_id in public_chat_list:
            chatObj = {}
            chatObj['id'] = chat.id
            chatObj['chatname'] = chat.chatname
            chatObj['num_users'] = chat.num_users
            chatObj['private'] = chat.private
            chatObj['time_created'] = chat.time_created
            chatObj['description'] = chat.description
            chatObj['owner'] = chat.owner
            chats_array.append(chatObj)
    return jsonify(chats_array)


@app.route("/api/publicchats")
def allPublicChats():
    chats = AllGroupChats.query.filter_by(private=False).all()
    chats_array = []
    for chat in chats:
        chatObj = {}
        chatObj['id'] = chat.id
        chatObj['chatname'] = chat.chatname
        chatObj['num_users'] = chat.num_users
        chatObj['private'] = chat.private
        chatObj['time_created'] = chat.time_created
        chatObj['description'] = chat.description
        chatObj['owner'] = chat.owner
        chats_array.append(chatObj)
    return jsonify(chats_array)


@app.route("/api/chat/<chat_id>/messages")
def allMessagesInChat(chat_id):
    msgs = Message.query.filter_by(chat_id=chat_id).all()
    chat_array = []
    for msg in msgs:
        msgObj = {}
        msgObj['id'] = msg.id
        msgObj['chat_id'] = msg.chat_id
        msgObj['user_sent_id'] = msg.user_sent_id
        msgObj['time_sent'] = msg.time_sent
        msgObj['content'] = msg.content
        chat_array.append(msgObj)
    return jsonify(chat_array)


@app.route("/api/chat/<chat_id>/users")
def allUsersInChat(chat_id):
    # we can figure this out later
    users = User.query.all()
    user_array = []
    for user in users:
        userObj = {}
        # "if user is logged in"
        userObj['id'] = user.id
        userObj['username'] = user.username
        userObj['display_name'] = user.display_name
        userObj['email'] = user.email
        userObj['password'] = user.password
        userObj['bio'] = user.bio
        userObj['chats'] = pickle.load(user.chats, "rb")
        userObj['profile_pic'] = user.profile_pic
        user_array.append(userObj)
    return jsonify(user_array)


@app.route("/api/AllUsers")
def allUsers():
    # we can figure this out later
    users = User.query.all()
    user_array = []
    for user in users:
        userObj = {}
        userObj['id'] = user.id
        userObj['username'] = user.username
        userObj['display_name'] = user.display_name
        userObj['email'] = user.email
        userObj['password'] = user.password
        userObj['bio'] = user.bio
        file = "pickles/" + user.username + "-chats.p"
        with open(file, 'rb') as handle:
            userObj['chats'] = pickle.load(handle)
            print('opened pickle object')
        userObj['profile_pic'] = user.profile_pic
        user_array.append(userObj)
    return jsonify(user_array)


@app.route("/api/User/<get_user>")
def userdata(get_user):
    user = User.query.filter_by(id=get_user).first()
    userObj = {}
    userObj['id'] = user.id
    userObj['username'] = user.username
    userObj['display_name'] = user.display_name
    userObj['email'] = user.email
    userObj['password'] = user.password
    userObj['bio'] = user.bio
    userObj['chats'] = user.chats
    userObj['profile_pic'] = user.profile_pic
    return jsonify(userObj)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")