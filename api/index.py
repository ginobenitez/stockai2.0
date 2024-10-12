from flask import Flask, jsonify, request
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor as RFR
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/info/<string:ticker>", methods=["GET"])
def get_info(ticker):
    stock = yf.Ticker(ticker)
    return jsonify(stock.info)

@app.route("/api/news/<string:ticker>", methods=["GET"])
def get_news(ticker):
    stock = yf.Ticker(ticker)
    return stock.news

# Function to fetch company data
def get_company_data(ticker):
    end_date = pd.to_datetime('today')
    start_date = pd.to_datetime(end_date) - pd.DateOffset(years=4)  # 4 years of data
    try:
        # Fetch the historical data for the given ticker
        company = yf.Ticker(ticker)
        company_data = company.history("5y")

        print(company_data)
        return company_data

    except Exception as e:
        print(f"Error fetching data for {ticker}. Please try again later.")
        return None

def stock_price_prediction(ticker):
    currCompany = get_company_data(ticker)
    
    predictor_list = ["Close", "Volume", "Open", "High", "Low"]

    # Create the target column for predicting the next day's 'Close' price
    currCompany["Tomorrow"] = currCompany["Close"].shift(-1)
    currCompany = currCompany.loc["1995-01-01":].copy()

    # Remove rows with NaN in the 'Tomorrow' column due to shifting
    currCompany.dropna(subset=["Tomorrow"], inplace=True)

    # Split the data into training and testing sets
    training = currCompany.iloc[:-110]
    testing = currCompany.iloc[-110:]

    # Define the parameter grid for the regressor
    param_grid = {
        'n_estimators': [100],
        'max_depth': [None, 10],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }

    # Initialize the RandomForestRegressor model for regression
    model = RFR(random_state=1)
    
    # Use GridSearchCV to find the best parameters, optimizing for regression metrics
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_absolute_error')
    grid_search.fit(training[predictor_list], training["Tomorrow"])

    # Get the best model from the grid search
    best_model = grid_search.best_estimator_

    # Make predictions on the testing set
    predictions = best_model.predict(testing[predictor_list])

    # Calculate mean absolute error for the predictions
    mae = mean_absolute_error(testing["Tomorrow"], predictions)

    # Shift the last date for the next prediction
    timestamp = testing.index[-1] + pd.DateOffset(days=1)

    # Convert to a regular date and then to string
    date_only_str = timestamp.date().strftime('%Y-%m-%d')

    # Return the last predicted price as a dictionary
    predc = {
        "Date": date_only_str, 
        "Predicted Price": predictions[-1]
    }

    return jsonify(predc)


# Flask API route for stock price prediction
@app.route("/api/predict/<string:ticker>", methods=["GET"])
def predict_stock_price(ticker):
    try:
        predictions = stock_price_prediction(ticker)
        if predictions is None:
            return jsonify({"error": "Prediction failed or no data available"}), 404
        return predictions
    except Exception as e:
        return jsonify({"error predict_stock_prediction": str(e)}), 500

# Function to plot historical data
def plot_historical_data(ticker):
    company = yf.Ticker(ticker)
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=1)
    company_data = company.history(start=start_date, end=end_date)

    plt.figure(figsize=(12, 6))
    plt.plot(company_data.index, company_data['Close'], label=f'{ticker} Close Price', color='b')
    plt.title(f'Historical Close Prices for {ticker} (Last 1 Year)')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid()

    # Save plot to a byte stream
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

# Flask API route to plot historical stock data
"""@app.route("/plot/<string:ticker>", methods=["GET"])
def plot_stock_data(ticker):
    try:
        image_base64 = plot_historical_data(ticker)
        return jsonify({"plot": image_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500"""

if __name__ == "__main__":
    app.run(debug=True)
