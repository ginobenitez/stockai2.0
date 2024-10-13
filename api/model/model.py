
from flask import Flask, jsonify, request
import yfinance as yf
import os
from xgboost import XGBRegressor  # Use XGBoost instead of RandomForestRegressor
#from sklearn.metrics import mean_absolute_error
import pandas as pd

app = Flask(__name__)

# Function to fetch company data
def get_company_data(ticker):
   
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
    
    if currCompany is None or currCompany.empty:
        return None

    predictor_list = ["Close", "Volume", "Open", "High", "Low"]

    # Create the target column for predicting the next day's 'Close' price
    currCompany["Tomorrow"] = currCompany["Close"].shift(-1)
    currCompany = currCompany.loc["1995-01-01":].copy()

    # Remove rows with NaN in the 'Tomorrow' column due to shifting
    currCompany.dropna(subset=["Tomorrow"], inplace=True)

    # Split the data into training and testing sets
    training = currCompany.iloc[:-110]
    testing = currCompany.iloc[-110:]

    # Initialize the XGBoost model
    model = XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=5, learning_rate=0.1)

    # Fit the model
    model.fit(training[predictor_list], training["Tomorrow"])

    # Make predictions on the testing set
    predictions = model.predict(testing[predictor_list])

    # Calculate mean absolute error for the predictions
    #mae = mean_absolute_error(testing["Tomorrow"], predictions)

    # Create a DataFrame to show actual vs predicted prices
    prediction_results = pd.DataFrame({
        "Date": testing.index.date,
        "Actual Price": testing["Tomorrow"],
        "Predicted Price": predictions
    })

    # Shift the last date for the next prediction
    timestamp = testing.index[-1] + pd.DateOffset(days=1)
    date_only_str = timestamp.date().strftime('%Y-%m-%d')

    # Return the last predicted price as a dictionary
    predc = {
        "Date": date_only_str, 
        "Predicted Price": round(float(predictions[-1]))
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

# Flask API route to plot historical stock data


if __name__ == "__main__":
    port = int(os.environ.get("PORT"))
    host = os.environ.get("HOST")
    # Bind to all available interfaces using "0.0.0.0"
    app.run(host="0.0.0.0", port=port)  # Remove the ssl_context argument

