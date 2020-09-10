from flask import Flask,jsonify,request,render_template
from test_data import books
import sqlite3

app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

####################
##work on books.db##
####################

# http://127.0.0.1:5000/books

@app.route('/books',methods=['GET','POST'])
def return_books():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()
    return jsonify(all_books)

#############################################
##work on books data stored in test_data.py##
#############################################


@app.route('/v1/books/id', methods=['GET'])
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return render_template('error_no_id.html')
    results = []
    for book in books:
        if book['id'] == id:
            results.append(book)
    return jsonify(results)

#####################
##works on books.db##
#####################

# http://127.0.0.1:5000/v2/books/id?author=Connie+Willis&published=1999
# http://127.0.0.1:5000/v2/books/id?published=2010
# http://127.0.0.1:5000/v2/books/id?author=Connie+Willis


@app.route('/v2/books/id', methods=['GET'])
def api_filter():
    query_parameters = request.args
    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

if __name__ == "__main__":
    app.run(debug=True)