from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:U9G67QjOLUKVOKHT@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'UV7KLxgDEj'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') 
       
    def __init__(self, username, password):
        self.username = username
        self.password = password


    def __repr__(self):
       return '<User %r>' % self.username

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog_page():
    user_id = request.args.get('userid') ###userid?
    blog_id = request.args.get('id')
    blogs = Blog.query.all()
    blog = Blog.query.filter_by(id=blog_id).first()

    if blog_id:
        blog_title = blog.title
        blog_body = blog.body
        
        return render_template('entries.html', blog=blog, blog_title=blog_title, blog_body=blog_body)

    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', blogs=posts)

    return render_template('blog.html', title="Blog!", blogs=blogs)


@app.route('/newpost')
def post():
    return render_template('newpost.html', title='New Post')


@app.route('/newpost', methods=['POST'])
def validate_post():

    owner = User.query.filter_by(username=session['username']).first()

    title = request.form['title']
    body = request.form['body']

    title_error = ""
    body_error = ""

    if title =="":
        title_error = "Title cannot be blank."

    if body =="":
        body_error = "Blog content cannot be blank."

    if not title_error and not body_error:
        new_blog = Blog(title, body, owner) ##owner?
        db.session.add(new_blog)
        db.session.commit()
        blog = new_blog.id
        return redirect('/blog?id={0}'.format(blog))
    else:
        return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():

    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if not user:
            flash('User password incorrect, or user does not exist', 'error')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        # TODO - validate user's data
        password_error = ""
        username_error = ""
        verify_error = ""

        if password == "":
            password_error = "Password cannot be blank"
        if len(password) <= 3:
            password_error = "Password must be greater than 3 characters"
        if " " in password:
            password_error = "Password cannot contain a space"
        if password != verify:
            verify_error = "The passwords do not match"

        if username == "":
            username_error = "Username cannot be blank"
        if len(username) > 20 or len(username) <= 3:
            username_error = "Username must be greater than 3 characters and no more than 20"
        if " " in username:
            username_error = "Username cannot contain a space"
        if existing_user:
            username_error = "Username already registered"

        if not existing_user and not username_error and not password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            # TODO - user better response messaging
            return render_template('signup.html', username=username, password_error=password_error, username_error=username_error, verify_error=verify_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

    
if __name__ == '__main__':
    app.run()