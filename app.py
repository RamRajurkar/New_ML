from flask import Flask, jsonify, render_template, request, url_for
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     return ('Welcome to Grocary Store !')

from flask_pymongo import PyMongo
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import bcrypt

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Recommendation_System'
app.secret_key = 'ram_secret_key'
mongo = PyMongo(app)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': request.form['username'], 'password': hashed_password})
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        return jsonify({'error': 'Username already exists'})
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        return jsonify({'error': 'Invalid username/password'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)