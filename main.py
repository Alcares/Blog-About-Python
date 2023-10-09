from imports import *
from db import select, insert_row

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        super().__init__()


@login_manager.user_loader
def load_user(user_id):
    user_result = select(f"SELECT * FROM users WHERE id={user_id}")
    user = User(user_result['id'])
    return user


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = select(f"SELECT * FROM users WHERE email='{form.email.data}'")
        except:
            pass
        if type(user) != TypeError:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        num_of_users = select("SELECT COUNT(*) FROM users")['count']
        insert_row(f"INSERT INTO users VALUES ({num_of_users + 1}, '{form.email.data}', '{hash_and_salted_password}', '{form.name.data}')")
        user = select(f"SELECT * FROM users WHERE email='{form.email.data}'")
        new_user = User(user['id'])
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        try:
            user = select(f"SELECT * FROM users WHERE email='{form.email.data}'")
        except:
            pass
        if type(user) == TypeError:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        else:
            if not check_password_hash(user['password'], password):
                flash('Password incorrect, please try again.')
                return redirect(url_for('login'))
            else:
                user = User(user['id'])
                login_user(user)
                return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    posts = select('SELECT * FROM blog_posts', fetch_all=True)
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = select(f'SELECT * FROM blog_posts WHERE id={post_id}', fetch_all=False)
    comment_form = CommentForm()
    all_comments = select(
                    f"""
                    select 
                        u.email,
                        c.text,
                        u.name
                    from comments c
                    left outer join blog_posts b
                        on c.post_id = b.id
                    left outer join users u
                        on u.id = c.author_id
                    where 
                        b.id = {post_id}
                    """,
                    fetch_all=True
    )
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        id_max = select("SELECT MAX(id) FROM comments")['max']
        print('hehe', comment_form.comment_text.data, current_user.id, requested_post['id'])
        insert_row(f"INSERT INTO comments VALUES ({id_max + 1}, '{comment_form.comment_text.data}', {current_user.id}, {requested_post['id']})")

    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form, comments=all_comments)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        row_count = select("SELECT MAX(id) FROM blog_posts")['max']
        insert_row(f"INSERT INTO blog_posts VALUES ({row_count + 1}, {current_user.id}, '{form.title.data}', '{form.subtitle.data}', '{date.today().strftime('%B %d, %Y')}', '{form.body.data}', '{form.img_url.data}')")
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = select(f"SELECT * FROM blog_posts WHERE id={post_id}")
    print(post_id)
    print(post)
    edit_form = CreatePostForm(
        title=post['title'],
        subtitle=post['subtitle'],
        img_url=post['img_url'],
        author=post['author_id'],
        body=post['body']
    )
    if edit_form.validate_on_submit():
        insert_row(f"UPDATE blog_posts SET title='{edit_form.title.data}', subtitle='{edit_form.subtitle.data}', img_url='{edit_form.img_url.data}', author_id={current_user.id}, body='{edit_form.body.data}' WHERE id={post_id}")
        return redirect(url_for("show_post", post_id=post_id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    insert_row(f"DELETE FROM blog_posts WHERE id={post_id}")
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html", current_user=current_user)

# Optional: You can inclue the email sending code from Day 60:
# DON'T put your email and password here directly! The code will be visible when you upload to Github.
# Use environment variables instead (Day 35)

# MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
# MAIL_APP_PW = os.environ.get("PASSWORD_KEY")

# @app.route("/contact", methods=["GET", "POST"])
# def contact():
#     if request.method == "POST":
#         data = request.form
#         send_email(data["name"], data["email"], data["phone"], data["message"])
#         return render_template("contact.html", msg_sent=True)
#     return render_template("contact.html", msg_sent=False)
#
#
# def send_email(name, email, phone, message):
#     email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
#     with smtplib.SMTP("smtp.gmail.com") as connection:
#         connection.starttls()
#         connection.login(MAIL_ADDRESS, MAIL_APP_PW)
#         connection.sendmail(MAIL_ADDRESS, MAIL_APP_PW, email_message)


if __name__ == "__main__":
    app.run(debug=False)

# TODO Optional: add contact me email functionality
# TODO display max 5 posts on main page
