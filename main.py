from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog')
def blog_page():
    blog_id = request.args.get('id')
    blogs = Blog.query.all()

    if blog_id:
        post = Blog.query.get(blog_id)
        blog_title = post.title
        blog_body = post.body

        return render_template('entries.html', title="Blog Entry #"+blog_id, blog_title=blog_title, blog_body=blog_body)
    
    sort = request.args.get('sort')

    if (sort=="newest"):
        blogs = Blog.query.order_by(Blog.created.desc()).all()
    elif (sort=="oldest"):
        blogs = Blog.query.order_by(Blog.created.asc()).all()
    else:
        blogs = Blog.query.all()

    return render_template('blog.html', title="Blog!", blogs=blogs)

@app.route('/newpost')
def post():
    return render_template('newpost.html', title='New Post')

@app.route('/newpost', methods=['POST'])
def validate_post():

    title = request.form['title']
    body = request.form['body']

    title_error = ""
    body_error = ""

    if title =="":
        title_error = "Title cannot be blank."

    if body =="":
        body_error = "Blog content cannot be blank."

    if not title_error and not body_error:
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()
        blog = new_blog.id
        return redirect('/blog?id={0}'.format(blog))
    else:
        return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error )

    
if __name__ == '__main__':
    app.run()