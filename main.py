from flask import Flask, render_template, url_for, flash, redirect, request, \
    jsonify
from forms import RegistrationForm, LoginForm, NewChat, SendMessage, \
    BecomeMember, Leave, InviteToChat, EditChat
from flask_sqlalchemy import SQLAlchemy
from flask_behind_proxy import FlaskBehindProxy
from flask_login import UserMixin, LoginManager, login_user, logout_user, \
    current_user, login_required
from flask_bcrypt import Bcrypt
import pickle
from imgur import upload_img
from youtube import get_search_results, extract_info_json, video_url
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
from giphy import build_url, get_results, parse_json
from pytz import timezone
import pytz
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
app.config['MAX_CONTENT_PATH'] = '100000000'

# Model to store all users


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(20), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(120), nullable=True)
    chats = db.Column(db.PickleType, nullable=False)
    profile_pic = db.Column(db.String(120), unique=False)
    Message = db.relationship("Message", backref="user", lazy=True)
    AllGroupChats = db.relationship("AllGroupChats", backref="user", lazy=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"

# Model to store all chatrooms


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


# Model for a chatroom message -- each message is linked to a chatroom id
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


@app.route("/")
@app.route("/home")
def home():
    if not current_user.is_authenticated:
        # Anonymous user
        return redirect(url_for('welcome'))
    return render_template('home.html', current_user=current_user)


@app.route("/welcome")
def welcome():
    return render_template('welcome.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
                    profile_pic='https://i.imgur.com/5UgSAH3.png',
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f'Logged out', 'success')
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/profiles/<user_id>", methods=['GET', 'POST'])
@login_required
def other_profile(user_id):
    user = load_user(user_id)
    curr_user = load_user(current_user.id)
    if user:
        # create list of current user's private chats to invite the user to
        now = datetime.utcnow()
        print(user.profile_pic)
        if (now-user.last_active) < timedelta(minutes=10):
            activity = 'status-circle'
            active = True
        else:
            activity = 'status-circle-red'
            active = False
        curr_user_private_chats = []
        with open(curr_user.chats, 'rb') as handle:
            curr_user_chats = pickle.load(handle)
            for chat_id in curr_user_chats:
                chat = AllGroupChats.query.get(chat_id)
                if chat.private:
                    curr_user_private_chats.append((chat.id, chat.chatname))
        form = InviteToChat()
        form.chatname.choices = curr_user_private_chats
        if form.validate_on_submit():
            chat_id = form.chatname.data
            join_chat(user_id, chat_id)
            print("... at least the button works?")
            # how do we collect input from a dropdown menu?!
            # need to add user to private chat user list and add chat to user's
            # chat list
        return render_template(
            'other_profile.html',
            user=user, form=form,
            name=user.username,
            current_user=current_user,
            activity=activity,
            active=active)
    return render_template('home.html')

# MUST FIX MUST FIX
# @app.route("/profile/<user_id>", methods=['GET', 'POST'])
# @login_required
# def other_profile(user_id):
#     user = User.query.filter_by(id=user_id).first()
#     form = InviteToChat()
#     if form.validate_on_submit():  # create chat button
#         chatname = db.session.query(AllGroupChats.id).filter_by(
#             chatname=form.chatname.data).first() is not None
#         if chatname is False:
#             file = "pickles/" + form.chatname.data + "-userslist.p"
#             f = open(file, "w+")
#             f.close()
#             with open(file, 'wb') as handle:
#                 pickle.dump([current_user.id], handle)
#                 print("created pickle")
#             private = request.form.get('Private')
#             if private == 'on':
#                 private = True
#             else:
#                 private = False
#             chat = AllGroupChats(
#                 chatname=form.chatname.data,
#                 display_name=form.display_name.data,
#                 description=form.description.data,
#                 private=private,
#                 users_list=file,
#                 num_users=1,
#                 time_created=datetime.now(),
#                 owner=current_user.id)
#             db.session.add(chat)
#             db.session.commit()
#             with open(current_user.chats, 'rb') as handle:
#                 users_chat_list = pickle.load(handle)
#                 users_chat_list.append(chat.id)
#                 with open(current_user.chats, 'wb') as handle:
#                     pickle.dump(users_chat_list, handle)
#             flash(f'Chat: {form.chatname.data} has been created!', 'success')
#             return redirect(url_for('profile'))
#         else:
#             flash(f'Chat name: "{form.chatname.data}"' +
#             ' is already taken please try another',
#                   'danger')
#             return redirect(url_for('profile'))
#     return render_template(
#         'other_profile.html',
#         user=user,
#         form=form)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = NewChat()
    if form.validate_on_submit():  # create chat button
        chatname = db.session.query(AllGroupChats.id).filter_by(
            chatname=form.chatname.data).first() is not None
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
            flash(f'Chat: "{form.chatname.data}" has been created!', 'success')
            return redirect(url_for('profile'))
        else:
            flash(
                f'Chat name: "{form.chatname.data}" is already taken please' +
                ' try another', 'danger')
            return redirect(url_for('profile'))
    return render_template(
        'profile.html',
        name=current_user.username,
        form=form, current_user=current_user)


def leave_chat(user_id, chat_id):
    user_id = int(user_id)
    chat_id = int(chat_id)
    # remove chat from user's chat list
    user = User.query.get(user_id)
    file = user.chats
    with open(file, 'rb') as handle:
        users_chats_list = pickle.load(handle)
        if chat_id in users_chats_list:
            users_chats_list.remove(chat_id)
            with open(file, 'wb') as handle:
                pickle.dump(users_chats_list, handle)
    # remove user from chat's user list
    chat = AllGroupChats.query.get(chat_id)
    file = chat.users_list
    with open(file, 'rb') as handle:
        chat_users_list = pickle.load(handle)
        if user_id in chat_users_list:
            chat_users_list.remove(user_id)
            chat.num_users = len(chat_users_list)
            db.session.commit()
            with open(file, 'wb') as handle:
                pickle.dump(chat_users_list, handle)
            flash(
                f'{user.username} has left chat: "{chat.display_name}"!' +
                ' You will no longer see it on your chats list!',
                'success')
        else:
            flash(
                f'{user.username} is not in the chat: "{chat.display_name}".',
                'danger')


# function to allow user to leave a chat
def join_chat(user_id, chat_id):
    user_id = int(user_id)
    chat_id = int(chat_id)
    # add chat to user's chat list
    user = User.query.get(user_id)
    file = user.chats
    with open(file, 'rb') as handle:
        users_chats_list = pickle.load(handle)
        # no double joining of chats
        if chat_id not in users_chats_list:
            users_chats_list.append(chat_id)
            with open(file, 'wb') as handle:
                pickle.dump(users_chats_list, handle)
    # add user to chat's users list
    chat = AllGroupChats.query.get(chat_id)
    file = chat.users_list
    with open(file, 'rb') as handle:
        chat_users_list = pickle.load(handle)
        # no double joining of chats
        if user_id not in chat_users_list:
            chat_users_list.append(user_id)
            chat.num_users = len(chat_users_list)
            db.session.commit()
            with open(file, 'wb') as handle:
                pickle.dump(chat_users_list, handle)
            flash(
                f'{user.username} has joined chat: "{chat.display_name}"!',
                'success')
        else:
            flash(
                f'{user.username} is already in chat: "{chat.display_name}".',
                'danger')


@app.route("/<chat_id>", methods=["GET", "POST"])
@login_required
def chat(chat_id):
    form = SendMessage()
    chat = AllGroupChats.query.filter_by(id=chat_id).first()
    chatname = chat.display_name
    if request.method == 'POST':
        form_name = ""
        if 'form-name' in request.form:
            form_name = request.form['form-name']
        if form_name == 'remove chat from profile':
            leave_chat(current_user.id, chat_id)
        if form_name == 'add chat to profile':
            join_chat(current_user.id, chat_id)

    if form.validate_on_submit():  # send message button
        print('validate')
        if '/youtube' in form.msg.data:
            api_key = "AIzaSyBGkGFRJ1Lzdsizug87FXPAl-yLuOjucdU"
            keyword = form.msg.data[9:]
            print(keyword)
            results = get_search_results(api_key, keyword)
            video_id = extract_info_json(results)
            url = video_url(video_id)
            print(url)
            form.msg.data = url
            print('true')
        elif '/giphy' in form.msg.data:
            keyword = form.msg.data[7:]
            print(keyword)
            gif_url = build_url('gifs', keyword)
            json = get_results(gif_url)
            gif = parse_json(json)
            print(gif)
            form.msg.data = gif
        elif '/sticker' in form.msg.data:
            keyword = form.msg.data[9:]
            print(keyword)
            sticker_url = build_url('stickers', keyword)
            json = get_results(sticker_url)
            sticker = parse_json(json)
            print(sticker)
            form.msg.data = sticker
        msg = Message(
            chat_id=chat_id,
            user_sent_id=current_user.id,
            time_sent=datetime.now(),
            content=form.msg.data)
        db.session.add(msg)
        db.session.commit()
        form.msg.data = ""
    chat_num = Message.query.all()
    chat_num = len(chat_num)
#     chat_num = chat_num - 1
    print(chat_num)
    return render_template(
        'chats.html', chatname=chatname,
        chat_id=chat_id, form=form, chat_num=chat_num)


@ app.route("/edit_chat/<chat_id>", methods=['GET', 'POST'])
@ login_required
def edit_chat(chat_id):
    chat = AllGroupChats.query.get(int(chat_id))
    thisChatname = chat.chatname
    if chat:
        # create list of current chat's users to remove or make owner
        chats_users = []
        chats_users_to_remove = [(0, '[remove no one]')]
        with open(chat.users_list, 'rb') as handle:
            chats_users_list = pickle.load(handle)
            for user_id in chats_users_list:
                user = User.query.get(user_id)
                chats_users.append((user.id, user.username))
                chats_users_to_remove.append((user.id, user.username))
        form = EditChat()
        form.owner.choices = chats_users
        form.user.choices = chats_users_to_remove
        # collect data that has been edited
        if form.validate_on_submit():
            bad_user_id = form.user.data
            if bad_user_id != 0:
                leave_chat(bad_user_id, chat_id)
            owner_user_id = form.owner.data
            chat.owner = owner_user_id
            chat.description = form.description.data
            chat.display_name = form.display_name.data
            db.session.commit()
            flash(f'Chat Updated!', 'success')
            return redirect(url_for('profile'))
        return render_template(
            'edit_chat.html',
            form=form, thisChatname=thisChatname)
    return render_template('home.html', current_user=current_user)
# I presume this is wrong
# @app.route("/edit_profile", methods=['POST', 'GET'])
# @login_required
# def edit_profile():
#     imgur = ''
#     if request.method == 'POST':
#         f = request.files['files']
#         print(f)
#         print(type(f))
#         filename = secure_filename(f.filename)
#         print(filename)
#         f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         imgur = upload_img(filename)
#         current_user.profile_pic = imgur
#         db.session.commit()
#         print(imgur)
#         return render_template('edit_profile.html', profile_pic=imgur)
# #         print(upload_img(f))
# #         print(type(profile_picture))
# #         if profile_picture is not None:
# #             print(profile_picture)
#     return render_template('edit_profile.html', profile_pic=imgur)


@ app.route("/edit_profile", methods=['POST', 'GET'])
@ login_required
def edit_profile():
    imgur = ''
    if request.method == 'POST':
        f = request.files['files']
        bio = request.form['bio']
        display = request.form['dis-name']
        print(f)
        print(bio)
        print(display)
        print(type(f))
        filename = secure_filename(f.filename)
        print('filename: ' + filename)
        if filename:
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imgur = upload_img(filename)
            current_user.profile_pic = imgur
        current_user.bio = bio
        current_user.display_name = display
        db.session.commit()
        flash(f'Profile Updated!', 'success')
        return redirect(url_for('profile'))
#         print(upload_img(f))
#         print(type(profile_picture))
#         if profile_picture is not None:
#             print(profile_picture)
    return render_template('edit_profile.html', current_user=current_user)


@ app.route("/api/profile/PublicChats/<user_id>")
def usersPublicChats(user_id):
    return getUserChats(user_id, False)


@ app.route("/api/profile/PrivateChats/<user_id>")
def userPrivateChats(user_id):
    return getUserChats(user_id, True)


@ app.route("/api/profile/PrivateChats/<user_id>/<other_user_id>")
def sharedPrivateChats(user_id, other_user_id):
    # get both users' data
    user = User.query.filter_by(id=user_id).first()
    other_user = User.query.filter_by(id=other_user_id).first()
    chats_array = []
    # load the user's public/private chat list
    with open(user.chats, 'rb') as handle, \
            open(other_user.chats, 'rb') as other_handle:
        public_chat_list = pickle.load(handle)
        other_user_public_chat_list = pickle.load(other_handle)
        chats = AllGroupChats.query.filter_by(private=True).all()
        # load chats from all chats table
        for chat in chats:
            if chat.id in public_chat_list \
                    and chat.id in other_user_public_chat_list:
                chatObj = {}
                chatObj['id'] = chat.id
                chatObj['chatname'] = chat.chatname
                chatObj['display_name'] = chat.display_name
                with open(chat.users_list, 'rb') as handle:
                    chatObj['users_list'] = pickle.load(handle)
                chatObj['num_users'] = chat.num_users
                chatObj['private'] = chat.private
                chatObj['time_created'] = chat.time_created
                chatObj['description'] = chat.description
                owner = User.query.filter_by(id=chat.owner).first()
                chatObj['owner'] = owner.username
                chatObj['owner_id'] = chat.owner
                chats_array.append(chatObj)
    return jsonify(chats_array)


def getUserChats(user_id, private):
    # get the user data
    user = User.query.filter_by(id=user_id).first()
    chats_array = []
    # load the user's public/private chat list
    with open(user.chats, 'rb') as handle:
        public_chat_list = pickle.load(handle)
        chats = AllGroupChats.query.filter_by(private=private).all()
        # load chats from all chats table
        for chat in chats:
            if chat.id in public_chat_list:
                chatObj = {}
                chatObj['id'] = chat.id
                chatObj['chatname'] = chat.chatname
                chatObj['display_name'] = chat.display_name
                with open(chat.users_list, 'rb') as handle:
                    chatObj['users_list'] = pickle.load(handle)
                chatObj['num_users'] = chat.num_users
                chatObj['private'] = chat.private
                chatObj['time_created'] = chat.time_created
                chatObj['description'] = chat.description
                owner = User.query.filter_by(id=chat.owner).first()
                chatObj['owner'] = owner.username
                chatObj['owner_id'] = chat.owner
                chats_array.append(chatObj)
    return jsonify(chats_array)


@ app.route("/api/profile/PublicChats/all")
def allPublicChats():
    chats = AllGroupChats.query.filter_by(private=False).all()
    chats_array = []
    for chat in chats:
        chatObj = {}
        chatObj['id'] = chat.id
        chatObj['chatname'] = chat.chatname
        chatObj['display_name'] = chat.display_name
        with open(chat.users_list, 'rb') as handle:
            chatObj['users_list'] = pickle.load(handle)
        chatObj['num_users'] = chat.num_users
        chatObj['private'] = chat.private
        chatObj['time_created'] = chat.time_created
        chatObj['description'] = chat.description
        owner = User.query.filter_by(id=chat.owner).first()
        chatObj['owner'] = owner.username
        chatObj['owner_id'] = chat.owner
        chats_array.append(chatObj)
    chats_array = sorted(
        chats_array,
        key=lambda x: x['num_users'],
        reverse=True)
    return jsonify(chats_array)

# MIGHT DELETE -- UNSURE WHAT GOAL IS HERE -- disregard this message


@ app.route("/api/chat/<chat_id>/messages")
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
        # msgObj['user_sent_display_name'] = user.display_name
        if user.display_name != "":
            msgObj['user_sent_display_name'] = user.display_name
        else:
            msgObj['user_sent_display_name'] = user.username
        eastern = timezone('US/Eastern')
        local_time = msg.time_sent.astimezone(eastern)
        time = local_time
        msgObj['time'] = time.strftime(
            "%I") + ":" + time.strftime("%M") + " " + time.strftime("%p")
        msgObj['date'] = time.strftime(
            "%b") + " " + time.strftime("%d") + ", " + time.strftime("%Y")
        msgObj['content'] = msg.content
        chat_array.append(msgObj)
    return jsonify(chat_array)


@ app.route("/api/chat/<chat_id>/users")
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


@ app.route("/api/AllUsers")
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
        file = user.chats
        with open(file, 'rb') as handle:
            userObj['chats'] = pickle.load(handle)
            print('opened pickle object')
        userObj['profile_pic'] = user.profile_pic
        user_array.append(userObj)
    return jsonify(user_array)


@ app.route("/api/User/<get_user>")
def userdata(get_user):
    user = User.query.filter_by(id=get_user).first()
    userObj = {}
    userObj['id'] = user.id
    userObj['username'] = user.username
    userObj['display_name'] = user.display_name
    userObj['email'] = user.email
    userObj['password'] = user.password
    userObj['bio'] = user.bio
    file = user.chats
    with open(file, 'rb') as handle:
        userObj['chats'] = pickle.load(handle)
        print('opened pickle object')
    userObj['profile_pic'] = user.profile_pic
    return jsonify(userObj)


@app.before_request
def update_last_active():
    current_user.last_active = datetime.utcnow()
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
