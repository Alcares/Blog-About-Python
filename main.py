from imports import *
from db import *
from aut import run_driver

POSTS_PER_PAGE = 3

MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
MAIL_APP_PW = os.environ.get("PASSWORD_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

DEPTH_LEVEL = 0

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        super().__init__()


@login_manager.user_loader
def load_user(user_id):
    user_result = get_user_by_id(user_id)
    user = User(user_result['id'], user_result['name'])
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
            user = get_user(form.email.data)
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
        insert_users(num_of_users + 1, form.email.data, hash_and_salted_password, form.name.data)
        user = get_user(form.email.data)
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
            user = get_user(form.email.data)
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
                user = User(user['id'], user['name'])
                login_user(user)
                return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/', methods=["GET", "POST"])
def get_all_posts():
    result = False
    order = False
    if request.args.get('search') and request.args.get('order'):
        result = request.form['search_bar']
        order = request.args.get('order')
        query = f"""SELECT
                        *
                        FROM blog_posts
                        LEFT OUTER JOIN users
                            ON users.id = blog_posts.author_id
                        WHERE title ilike '%{result}%'
                        ORDER BY {order}
                        """
    elif request.args.get('search'):
        result = request.form['search_bar']
        query = f"""SELECT
                            name,
                            blog_posts.id,
                            title,
                            subtitle,
                            date,
                            body,
                            img_url,
                            num_comments
                        FROM blog_posts
                        LEFT OUTER JOIN users
                            ON users.id = blog_posts.author_id
                        WHERE title ilike '%{result}%'
                        ORDER BY date DESC
                        """
    elif request.args.get('order'):
        order = request.args.get('order')
        query = f"""SELECT
                        name,
                        blog_posts.id,
                        title,
                        subtitle,
                        date,
                        body,
                        img_url,
                        num_comments
                    FROM blog_posts
                    LEFT OUTER JOIN users
                        ON users.id = blog_posts.author_id
                    ORDER BY {order}
                    """
    else:
        query = """
                SELECT
                    name,
                    blog_posts.id,
                    title,
                    subtitle,
                    date,
                    body,
                    img_url,
                    num_comments
                FROM blog_posts
                LEFT OUTER JOIN users
                    ON users.id = blog_posts.author_id
                ORDER BY num_comments DESC
                """
    if not request.args.get('depth'):
        query = f"""
                SELECT * FROM ({query}) as p
                LIMIT {POSTS_PER_PAGE}
                """
    else:
        depth = int(request.args.get('depth'))
        query = f"""
                 SELECT * FROM ({query}) as p
                 OFFSET {depth * POSTS_PER_PAGE}
                 LIMIT {POSTS_PER_PAGE}
                     """
        posts = select(query, fetch_all=True)
        return render_template("index.html", all_posts=posts, current_user=current_user, search=result, order=order, depth=depth)
    posts = select(query, fetch_all=True)
    return render_template("index.html", all_posts=posts, current_user=current_user, search=result, order=order)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = get_post(post_id)
    comment_form = CommentForm()
    all_comments = get_comments(post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        id_max = select("SELECT MAX(id) FROM comments")['max']
        insert_comment(id_max + 1, comment_form.comment_text.data, current_user.id, requested_post['id'])
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

@app.route("/new-submission", methods=["GET", "POST"])
def new_submission():
    form = CreatePostForm()
    if form.validate_on_submit():
        row_count = select("SELECT MAX(id) FROM blog_posts")['max']
        add_user_blog_post(row_count+1, current_user.id, form.title.data, form.subtitle.data, date.today().strftime('%B %d, %Y'), form.body.data, form.img_url.data)
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)



@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = get_post(post_id)
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
        update_post(edit_form.title.data, edit_form.subtitle.data,
                    edit_form.img_url.data, current_user.id, edit_form.body.data, post_id)
        return redirect(url_for("show_post", post_id=post_id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    del_post(post_id)
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(MAIL_ADDRESS, MAIL_APP_PW)
        connection.sendmail(MAIL_ADDRESS, MAIL_ADDRESS, email_message)





@app.route("/plot")
def ploted(current_user):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()

    posts = select(f'SELECT blog_posts.id, blog_posts.num_comments FROM blog_posts LEFT OUTER JOIN users ON users.id = blog_posts.author_id WHERE users.id = {current_user} ORDER BY date asc', fetch_all=True)
    post_id = [post['id'] for post in posts]
    post_comm = [post['num_comments'] for post in posts]
    print(post_id, post_comm)
    ax.plot(post_id, post_comm)
    ax.set_xlabel('Post Id')
    ax.set_ylabel('Number of Comments')
    print(post_comm)
    ax.set_yticks(range(0, max(post_comm) + 1))
    ax.set_xticks(post_id)
    ax.grid(True)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'data:image/png;base64,{data}'


@app.route("/dashboard/<user_id>")
def dashboard(user_id):
    try:
        user = get_user_by_id(user_id)
        print(user['name'])
    except:
        user = select(f"SELECT * FROM users WHERE name = '{user_id}'")
        user_id = user['id']
        print('except',user['name'], user_id)
    print('HEHE', user_id)
    plot = ploted(user_id)
    print(plot)
    return render_template("dashboard.html", user=user, graph=plot)


@app.route('/submissions', methods=["GET", "POST"])
@admin_only
def all_submissions():
    posts = select('SELECT * FROM user_posts', fetch_all=True)
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route('/simulate_user_activity')
def keep_active():
    run_driver()
    send_email('marcin', 'marcin@asdf.com', '4237941234', 'Poszło! Selenium aktywuje strone')


if __name__ == "__main__":
    app.run(debug=False)


# TODO prevent from sql injections (prepare statement)
# TODO make admin able to accept post submissions
# TODO add a trigger to update comment count while making a new comment
