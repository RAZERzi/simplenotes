import sqlite3
from flask import Flask, request, render_template, redirect, g

app = Flask(__name__)

# Number of posts to display per page
POSTS_PER_PAGE = 10

# Create a function to connect to the database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('posts.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * POSTS_PER_PAGE

    db = get_db()
    cursor = db.cursor()
    
    # Calculate the total number of posts
    cursor.execute('SELECT COUNT(*) FROM posts')
    total_posts = cursor.fetchone()[0]

    # Calculate the total number of pages
    total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE

    # Retrieve posts for the current page
    cursor.execute('SELECT * FROM posts ORDER BY id DESC LIMIT ? OFFSET ?', (POSTS_PER_PAGE, offset))
    posts = cursor.fetchall()

    return render_template('index.html', posts=posts, total_posts=total_posts, total_pages=total_pages, POSTS_PER_PAGE=POSTS_PER_PAGE)

@app.route('/create', methods=['POST'])
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
    db.commit()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        edited_title = request.form.get('edited_title')
        edited_content = request.form.get('edited_content')
        
        cursor.execute('UPDATE posts SET title=?, content=? WHERE id=?', (edited_title, edited_content, id))
        db.commit()
        return redirect('/')
    
    cursor.execute('SELECT * FROM posts WHERE id = ?', (id,))
    post = cursor.fetchone()
    return render_template('edit.html', post=post)

@app.route('/delete/<int:id>')
def delete_post(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (id,))
    db.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
