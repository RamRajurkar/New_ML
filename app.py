from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
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
bcrypt = Bcrypt(app)

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
                'rating': row['rating'],
                'description': row['description']  # Assuming 'rating' is a column in your DataFrame
            }
            top_products.append(product_dict)

        return top_products[:16]
    else:
        return []


@app.route('/', methods=['GET'])  # Define a route for the home page
def home():
    # Assuming data is available in the global scope
    products = recommend_top_products(data, food_and_beverages1)  # Default category
    return render_template('index.html', products=products)


@app.route('/home_recommendation', methods=['POST'])
def top_products():
    # Assuming data is available in the global scope
    category = request.form.get('category')
    print(category)
    if category is not None:
        if category == 'food_and_beverages1':
            products = recommend_top_products(data, food_and_beverages1)
        elif category == 'food_and_beverages2':
            products = recommend_top_products(data, food_and_beverages2)
        elif category == 'household_and_cleaning':
            products = recommend_top_products(data, household_and_cleaning)
        elif category == 'personal_care_and_babycare':
            products = recommend_top_products(data, personal_care_and_babycare)
        elif category == 'daily_needs':
            products = recommend_top_products(data, daily_needs)
        else:
            products = recommend_top_products(data, food_and_beverages1)  # Default category
    else:
        products = recommend_top_products(data, food_and_beverages1)  # Default category

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
    sim_scores = sim_scores[1:16]  # Get the top 10 similar products
    product_indices = [i[0] for i in sim_scores]
    return data['product'].iloc[product_indices].tolist()


# @app.route('/')
# def home():
#     # if 'username' in session:
#     #     return render_template('index.html', username=session['username'])
#     # return redirect(url_for('login'))
#     return render_template('index.html')

@app.route('/recommend', methods=['GET'])
def recommend_products():
    product_name = request.args.get('product_name')
    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    recommendations = get_recommendations(product_name)
    return jsonify({'recommendations': recommendations})

@app.route('/display_products', methods=['GET', 'POST'])
def display_products():
    product_name = request.args.get('name')
    desc = request.args.get('desc')
    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    recommendations = get_recommendations(product_name)
    recommended_products = data[data['product'].isin(recommendations)]  # Filter the dataset to get recommended products
    recommended_products_dict = recommended_products.to_dict(orient='records')  # Convert DataFrame to dictionary

    # for product in recommended_products_dict:
    #     product['description'] = text_summary(product['description'])

    return render_template('home.html',desc=desc,product_name=product_name, recommendations=recommended_products_dict, product=product_name)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([first_name, last_name, username, email, gender, dob, password, confirm_password]):
            return 'Please fill out all fields', 400

        if password != confirm_password:
            return 'Passwords do not match', 400

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save user to MongoDB
        users = mongo.db.Users
        new_user = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'gender': gender,
            'dob': dob,
            'password': hashed_password
        }
        users.insert_one(new_user)

        return f'Sign-up successful for {first_name} {last_name}'
    
    # For GET requests, return the signup form HTML or render a template
    return render_template('index.html')


    #     users = mongo.db.users
    #     existing_user = users.find_one({'username': request.form['username']})

    #     if existing_user is None:
    #         hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
    #         users.insert_one({'username': request.form['username'], 'password': hashed_password})
    #         session['username'] = request.form['username']
    #         return redirect(url_for('home'))
    #     return jsonify({'error': 'Username already exists'})
    # return render_template('Registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.Users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        return jsonify({'error': 'Invalid username/password'})
    return render_template('Registration.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/recommend_page', methods=['GET', 'POST'])
def product():
    
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)