

from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.metrics import precision_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

# Function to fetch company data
def get_company_data(ticker):
    """sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    sp500['Symbol'] = sp500['Symbol'].str.replace('.', '-')
    symbols_list = sp500['Symbol'].unique().tolist()
    end_date = '2023-09-27'
    start_date = pd.to_datetime(end_date) - pd.DateOffset(365*8)

    df = yf.download(tickers=symbols_list, start=start_date, end=end_date).stack()
    df.index.names = ['date', 'ticker']
    return df[df.index.get_level_values('ticker') == ticker]"""

    try:
        company = yf.Ticker(ticker)
        company_data = company.history(period = "max")
        return company_data
    except Exception as e:
        print("Error fetching data for company, please check again")
        print(e)
        return None

# Function for stock price prediction
def stock_price_prediction(ticker):
    currCompany = get_company_data(ticker)
    if currCompany.empty:
        return None, None

    predictor_list = ["Close", "Volume", "Open", "High", "Low"]
    currCompany["Tomorrow"] = currCompany["Close"].shift(-1)
    currCompany["Target"] = (currCompany["Tomorrow"] > currCompany["Close"]).astype(int)
    currCompany = currCompany.loc["1995-01-01":].copy()

    # Split the data into training and testing sets
    training = currCompany.iloc[:-110]
    testing = currCompany.iloc[-110:]

    param_grid = {
        'n_estimators': [100],
        'max_depth': [None, 10],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }

    model = RFC(random_state=1)
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='precision')
    grid_search.fit(training[predictor_list], training["Target"])

    best_model = grid_search.best_estimator_
    preds = best_model.predict(testing[predictor_list])
    precision = precision_score(testing["Target"], preds)

    label_mapping = {0: "Sell", 1: "Buy"}
    actual_labels = [label_mapping[val] for val in testing["Target"]]
    predicted_labels = [label_mapping[val] for val in preds]

    predictions = pd.DataFrame({
        "Date": testing.index.date,
        "Actual": actual_labels,
        "Predicted": predicted_labels
    })
    return predictions, precision

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

# Flask API route to get company stock data
@app.route("/data/<string:ticker>", methods=["GET"])
def get_company_stock_data(ticker):
    try:
        data = get_company_data(ticker)
        if data is None or data.empty:
            return jsonify({"error": "Company not found or no data available"}), 404
        return jsonify(data.reset_index().to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask API route for stock price prediction
@app.route("/predict/<string:ticker>", methods=["GET"])
def predict_stock_price(ticker):
    try:
        predictions, precision = stock_price_prediction(ticker)
        if predictions is None or predictions.empty:
            return jsonify({"error": "Prediction failed or no data available"}), 404
        return jsonify({
            "predictions": predictions.to_dict(orient='records'),
            "precision": precision
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask API route to plot historical stock data
@app.route("/plot/<string:ticker>", methods=["GET"])
def plot_stock_data(ticker):
    try:
        image_base64 = plot_historical_data(ticker)
        return jsonify({"plot": image_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
