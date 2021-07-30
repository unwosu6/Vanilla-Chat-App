# Not necessary right now!

# from main import app

# @app.route("/")
# def home():
#     return render_template('home.html')

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():  # checks if entries are valid
#         passwordhash = bcrypt.generate_password_hash(
#             form.password.data).decode('utf-8')
#         username = db.session.query(User.id).filter_by(
#             username=form.username.data).first() is not None
#         if username is False:
#             mail = db.session.query(User.id).filter_by(
#                 email=form.email.data).first() is not None
#             if mail is False:
#                 user = User(
#                     username=form.username.data,
#                     email=form.email.data,
#                     password=passwordhash)
#                 db.session.add(user)
#                 db.session.commit()
#                 flash(f'Account created for {form.username.data}!', \
#                 'success')
#                 return redirect(url_for('home'))  # if so - send to home page
#             else:
#                 flash(f'That email is already taken please try another',
#                       'danger')
#                 return redirect(url_for('register'))
#         else:
#             flash(f'That username is already taken please try another',
#                   'danger')
#             return redirect(url_for('register'))
#     return render_template('register.html', title='Register', form=form)

# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         username = db.session.query(User.id).filter_by(
#             username=form.username.data).first() is not None
#         if username is True:
#             password = db.session.query(
#                 User.password).filter_by(
#                 username=form.username.data).first()
#             password = password[0]
#             if bcrypt.check_password_hash(password, form.password.data):
#                 # on if checked, None if not checked
#                 remember = request.form.get('Remember')
#                 if remember == 'on':
#                     remember = True
#                 else:
#                     remember = False
#                 print(remember)
#                 flash(f'Logged in as {form.username.data}!', 'success')
#                 user = User.query.filter_by(
#                     username=form.username.data).first()
#                 login_user(user, remember=remember)
#                 return redirect(url_for('profile'))
#             else:
#                 flash(f'Wrong password for {form.username.data}!', 'danger')
#                 return redirect(url_for('login'))
#         else:
#             flash(
#                 f'Account does not exist for {form.username.data}!',
#                 'danger')
#             return redirect(url_for('login'))
#     return render_template('login.html', title='Login', form=form)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash(f'Logged out', 'success')
#     return redirect(url_for('home'))
