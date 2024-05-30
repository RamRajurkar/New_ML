Sure, here's the complete `README.md` content in one block:


# Product Recommendation System
```sh
This Flask application provides product recommendations using collaborative filtering and sentiment analysis. The application leverages various machine learning techniques to recommend products based on user preferences and reviews.
```

## Features

- **Product Search**: Users can search for products.
- **Collaborative Filtering Recommendations**: Personalized product recommendations based on user ratings.
- **Sentiment Analysis**: Analyzes sentiment of product descriptions.
  
## Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/yourusername/product-recommendation-system.git
   cd product-recommendation-system
   ```

2. **Create and activate a virtual environment**:

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Download the dataset**:

   - Place your dataset file `data_cleaned_1 (2).csv` in the project root directory.

## Usage

1. **Run the Flask application**:

   ```sh
   flask run
   ```

   By default, the application will run on `http://127.0.0.1:5000`.

2. **Access the application**:

   - Go to `http://127.0.0.1:5000` in your web browser.

## Endpoints

- **Home Page** (`/`): Displays the product search page.
- **Recommendations** (`/recommend`): Provides product recommendations based on user ID.
  - **Request Parameters**:
    - `user_id` (required): The ID of the user for whom to generate recommendations.
  - **Response**:
    - JSON object containing a list of recommended product IDs.
- **Display Products** (`/home`): Displays the home page with product recommendations.
  - **Request Parameters**:
    - `product_name` (required): The name of the product to display recommendations for.
  - **Response**:
    - Renders the home page with product recommendations.

## Project Structure

```
product-recommendation-system/
├── templates/
│   ├── product.html
│   └── home.html
├── data_cleaned_1 (2).csv
├── app.py
└── requirements.txt
```

## Dependencies

- Flask
- Pandas
- Scikit-learn
- Surprise
- TextBlob

Make sure to install the required Python packages by running `pip install -r requirements.txt`.

## Example

Here is an example of how to get recommendations for a user with ID `123`:

```sh
curl http://127.0.0.1:5000/recommend?user_id=123
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

This application uses data from a sample dataset and various Python libraries for machine learning and natural language processing.
```

Feel free to modify the content according to your specific project details and requirements.
