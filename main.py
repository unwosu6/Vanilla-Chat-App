from flask import Flask, render_template, url_for, flash, redirect, request, \
    jsonify
from forms import RegistrationForm, LoginForm, NewChat, SendMessage, BecomeMember, Leave
from flask_sqlalchemy import SQLAlchemy
from flask_behind_proxy import FlaskBehindProxy
from flask_login import UserMixin, LoginManager, login_user, logout_user, \
    current_user, login_required
from flask_bcrypt import Bcrypt
import pickle
from datetime import datetime
import os


app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '9ef1d5a68754c1a8df1f196c00eb79c8'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

IMAGES = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = IMAGES


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(20), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(120), nullable=True)
    chats = db.Column(db.PickleType, nullable=False)
    profile_pic = db.Column(db.String(120), unique=True)
    Message = db.relationship("Message", backref="user", lazy=True)
    AllGroupChats = db.relationship("AllGroupChats", backref="user", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class AllGroupChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chatname = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    users_list = db.Column(db.PickleType, nullable=False)
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
    pfp = os.path.join(app.config['UPLOAD_FOLDER'], 'genericpfp.png')
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
                    pickle.dump([], handle)
                    print("created pickle")
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=passwordhash,
                    display_name='',
                    profile_pic=pfp,
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


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = NewChat()
    if form.validate_on_submit():  # checks if entries are valid
        chatname = db.session.query(User.id).filter_by(
            username=form.chatname.data).first() is not None
        if chatname is False:
            file = "pickles/" + form.chatname.data + "-userslist.p"
            f = open(file, "w+")
            f.close()
            with open(file, 'wb') as handle:
                pickle.dump([current_user.id], handle)
                print("created pickle")
            private = request.form.get('Private')
            if private == 'on':
                private = True
            else:
                private = False
            chat = AllGroupChats(
                chatname=form.chatname.data,
                display_name=form.display_name.data,
                description=form.description.data,
                private=private,
                users_list=file,
                num_users=1,
                time_created=datetime.now(),
                owner=current_user.id)
            db.session.add(chat)
            db.session.commit()
            with open(current_user.chats, 'rb') as handle:
                users_chat_list = pickle.load(handle)
                users_chat_list.append(chat.id)
                with open(current_user.chats, 'wb') as handle:
                    pickle.dump(users_chat_list, handle)
            flash(f'Chat: {form.chatname.data} has been created!', 'success')
            return redirect(url_for('profile'))
        else:
            flash(f'That chatname is already taken please try another',
                  'danger')
            return redirect(url_for('profile'))
    # create_chat()
    return render_template(
        'profile.html',
        name=current_user.username,
        form=form)

# function to allow user to leave a chat


def leave_chat(user_id, chat_id):
    # remove chat from user's chat list
    user = User.query.filter_by(id=user_id).first()
    file = user.chats
    with open(file, 'rb') as handle:
        users_chats_list = pickle.load(handle)
        users_chats_list.remove(chat_id)
        with open(file, 'wb') as handle:
            pickle.dump(users_chats_list, handle)
    # remove user from chat's user list
    chat = AllGroupChats.query.filter_by(id=chat_id).first()
    file = chat.users_list
    with open(file, 'rb') as handle:
        chat_users_list = pickle.load(handle)
        chat_users_list.remove(user_id)
        chat.num_users = len(chat_users_list)
        db.session.commit()
        with open(file, 'wb') as handle:
            pickle.dump(chat_users_list, handle)


# function to allow user to leave a chat
def join_chat(user_id, chat_id):
    # add chat to user's chat list
    user = User.query.filter_by(id=user_id).first()
    file = user.chats
    with open(file, 'rb') as handle:
        users_chats_list = pickle.load(handle)
        # no double joining of chats
        if user_id not in users_chats_list:
            users_chats_list.append(chat_id)
            with open(file, 'wb') as handle:
                pickle.dump(users_chats_list, handle)
    # add user to chat's users list
        chat = AllGroupChats.query.filter_by(id=chat_id).first()
    file = chat.users_list
    with open(file, 'rb') as handle:
        chat_users_list = pickle.load(handle)
        # no double joining of chats
        if chat_id not in chat_users_list:
            chat_users_list.append(user_id)
            chat.num_users = len(chat_users_list)
            db.session.commit()
        with open(file, 'wb') as handle:
            pickle.dump(chat_users_list, handle)


@app.route("/<chat_id>", methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    form = SendMessage()
#     form2 = BecomeMember()
#     form3 = Leave()
    chat = AllGroupChats.query.filter_by(id=chat_id).first()
    print(chat)
    chatname = chat.chatname
    # TODO: add these two buttons to chat page
#         if form3.validate_on_submit():
#         leave_chat(current_user.id, chat_id)
#         flash(f'You have left chat: {chat.display_name}! You will no longer see it on chats list!', 'success')
#         return redirect(url_for('/profile'))
#     if form2.validate_on_submit():
#         join_chat(current_user.id, chat_id)
#         flash(f'You have joned chat: {chat.display_name}! You can access it from you chats list', 'success')
    if request.method == "POST":
        # name='leave_chat' value='leave' in html
        if request.form.get('leave_chat') == 'leave':
            leave_chat(current_user.id, chat_id)
            flash(
                f'You have left chat: {chat.display_name}! You will no longer see it on chats list!',
                'success')
            return redirect(url_for('/profile'))
        if request.form.get('become_memeber') == 'become member':
            join_chat(current_user.id, chat_id)
            flash(
                f'You have joined chat: {chat.display_name}! You can access it from you chats list',
                'success')
    if form.validate_on_submit():  # checks if entries are valid
        print('validate')
        msg = Message(
            chat_id=chat_id,
            user_sent_id=current_user.id,
            time_sent=datetime.now(),
            content=form.msg.data)
        print('made message object, hopefully')
        db.session.add(msg)
        db.session.commit()
        print("commited message")
    return render_template(
        'chats.html',
        chat_id=chat_id, chatname=chatname,
        current_user=current_user, form=form)


@app.route("/api/profile/PublicChats/<user_id>")
def usersPublicChats(user_id):
    return getUserChats(user_id, False)


@app.route("/api/profile/PrivateChats/<user_id>")
def userPrivateChats(user_id):
    return getUserChats(user_id, True)


def getUserChats(user_id, private):
    user = User.query.filter_by(id=user_id).first()
    chats_array = []
    with open(user.chats, 'rb') as handle:
        public_chat_list = pickle.load(handle)
        chats = AllGroupChats.query.filter_by(private=private).all()
        for chat in chats:
            if chat.id in public_chat_list:
                chatObj = {}
                chatObj['id'] = chat.id
                chatObj['chatname'] = chat.chatname
                with open(chat.users_list, 'rb') as handle:
                    chatObj['users_list'] = pickle.load(handle)
                chatObj['num_users'] = chat.num_users
                chatObj['private'] = chat.private
                chatObj['time_created'] = chat.time_created
                chatObj['description'] = chat.description
                owner = User.query.filter_by(id=chat.owner).first()
                chatObj['owner'] = owner.username
                chats_array.append(chatObj)
    return jsonify(chats_array)


@app.route("/api/PublicChats")
def allPublicChats():
    chats = AllGroupChats.query.filter_by(private=False).all()
    chats_array = []
    for chat in chats:
        chatObj = {}
        chatObj['id'] = chat.id
        chatObj['chatname'] = chat.chatname
        with open(chat.users_list, 'rb') as handle:
            chatObj['users_list'] = pickle.load(handle)
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
        # get user pfp, username, and display_name
        user = User.query.filter_by(id=msg.user_sent_id).first()
        msgObj['user_sent_pfp'] = user.profile_pic
        msgObj['user_sent_username'] = user.username
        msgObj['user_sent_display_name'] = user.display_name
        time = msg.time_sent
        msgObj['time'] = time.strftime(
            "%I") + ":" + time.strftime("%M") + " " + time.strftime("%p")
        msgObj['date'] = time.strftime(
            "%b") + time.strftime("%d") + ", " + time.strftime("%Y")
        msgObj['content'] = msg.content
        chat_array.append(msgObj)
    return jsonify(chat_array)

# MIGHT DELETE -- UNSURE WHAT GOAL IS HERE


@app.route("/api/chat/<chat_id>/users")
def allActiveUsersInChat(chat_id):
    # we can figure this out later
    users = AllGroupChats.query.filter_by(id=chat_id).first()
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
        file = user.chats
        with open(file, 'rb') as handle:
            userObj['chats'] = pickle.load(handle)
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
        # file = "pickles/" + user.username + "-chats.p"
        file = user.chats
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
