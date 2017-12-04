from flask import Flask, redirect, url_for, \
				  request, render_template, json
from pymongo import MongoClient
import pymongo
import os
import socket
from bson import ObjectId



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


client = MongoClient('mongodb://backend:27016/dockerdemo')
db = client.blogpostDB

app = Flask(__name__)

@app.route("/")
def landing_page():
    posts = get_all_posts()
    
    return render_template('blog.html', posts=json.loads(posts),isEditing=False,isOnMain=True)


@app.route('/add_post', methods=['POST'])
def add_post():

    new()
    return redirect(url_for('landing_page'))


@app.route('/remove_all')
def remove_all():
    db.blogpostDB.delete_many({})

    return redirect(url_for('landing_page'))




## Services

@app.route("/posts", methods=['GET'])
def get_all_posts():
    
    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]
    return JSONEncoder().encode(posts)

@app.route("/posts", methods=['PUT'])
def edit_post(post_id,item_doc):
    db.blogpostDB.find_one_and_replace({'_id': ObjectId(post_id)}, item_doc)
    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]
    return JSONEncoder().encode(posts)

@app.route("/posts", methods=['DELETE'])
def delete_post(post_id):
    db.blogpostDB.delete_one({'_id': ObjectId(post_id)})
    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]
    return JSONEncoder().encode(posts)


@app.route('/new', methods=['POST'])
def new():

    item_doc = {
        'title': request.form['title'],
        'post': request.form['post']
    }
    db.blogpostDB.insert_one(item_doc)

    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]

    return JSONEncoder().encode(posts[-1])
@app.route("/delete_this/<post_id>")
def delete_blog(post_id):
    delete_post(post_id)
    return redirect(url_for('landing_page'))


@app.route("/post/<post_id>")
def edit_page(post_id):
    post = get_one(post_id)
    return render_template('blog.html', isEditing=True, currentBlog=json.loads(post),isOnMain=False)
@app.route('/edit/<post_id>', methods=['POST'])
def edit(post_id):
    item_doc = {
        'title': request.form['title'],
        'post': request.form['post']
    }
    edit_post(post_id,item_doc)
    return redirect(url_for('landing_page'))

    # return JSONEncoder().encode(posts[-1])
### Insert function here ###

def get_one(post_id):
    post = db.blogpostDB.find_one({'_id': ObjectId(post_id)})
    return JSONEncoder().encode(post)


############################



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
