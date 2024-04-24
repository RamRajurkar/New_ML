from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.static_folder = 'static'

data = pd.read_csv('data_cleaned_1 (2).csv')
print(data.head())

print(data['product'], data['category'])
# Clean the data (e.g., remove duplicates, handle missing values)

# Create a TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words='english')

# Create a matrix using the product descriptions
tfidf_matrix = tfidf.fit_transform(data['description'] + ' ' + data['category'] + ' ' + data['sub_category'])

# Calculate the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)



# @app.route('/', methods=['GET', 'POST'])
# def home():
#     return ('Welcome to Grocary Store !')




app.config['MONGO_URI'] = 'mongodb://localhost:27017/Recommendation_System'
app.secret_key = 'ram_secret_key'
mongo = PyMongo(app)

food_and_beverages1 = ['foodgrains', 'oil', 'masala', 'snacks', 'brandedfoods', 'gourmet', 'worldfood', 'beverages']
food_and_beverages2 = ['bakery', 'cakes', 'dairy']
household_and_cleaning = ['cleaning', 'household']
personal_care_and_babycare = ['beauty', 'hygiene', 'babycare']
daily_needs = ['kitchen', 'garden', 'pets']

def recommend_top_products(data, category):
    if not data.empty and category is not None:
        # Check if the category is in the 'category' column
        filtered_data = data[data['category'].apply(lambda x: any(item in x for item in category))]

        # Filter top rated products
        top_rated_products = filtered_data[filtered_data['rating'] > 4.9]

        top_products = []
        for index, row in top_rated_products.iterrows():
            product_dict = {
                'product': row['product'],
                'price': row['sale_price'],  # Assuming 'sale_price' is a column in your DataFrame
                'rating': row['rating']  # Assuming 'rating' is a column in your DataFrame
            }
            top_products.append(product_dict)

        return top_products[:16]
    else:
        return []


@app.route('/', methods=['GET', 'POST'])
def top_products():
    # Assuming data is available in the global scope
    products = recommend_top_products(data, food_and_beverages1)
    print("Top rated products: ")
    print(products)
    for product in products:
        print(product)
    return render_template('index.html', products=products)










def get_recommendations(product_name, cosine_sim=cosine_sim):
    idx = data[data['product'] == product_name].index
    if len(idx) == 0:
        return []  # Return an empty list if product_name is not found
    idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get the top 10 similar products
    product_indices = [i[0] for i in sim_scores]
    return data['product'].iloc[product_indices].tolist()


@app.route('/')
def home():
    # if 'username' in session:
    #     return render_template('index.html', username=session['username'])
    # return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/recommend', methods=['GET'])
def recommend_products():
    product_name = request.args.get('product_name')
    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    recommendations = get_recommendations(product_name)
    return jsonify({'recommendations': recommendations})

@app.route('/display_products', methods=['GET', 'POST'])
def display_products():
    product_name = request.args.get('product_name')
    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    recommendations = get_recommendations(product_name)
    recommended_products = data[data['product'].isin(recommendations)]  # Filter the dataset to get recommended products
    recommended_products_dict = recommended_products.to_dict(orient='records')  # Convert DataFrame to dictionary

    # for product in recommended_products_dict:
    #     product['description'] = text_summary(product['description'])

    return render_template('home.html', recommendations=recommended_products_dict, product=product_name)


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