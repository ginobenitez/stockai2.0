import os
from flask import Flask, jsonify, request
import yfinance as yf

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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', "8080"))
    app.run(host="0.0.0.0", port=port)
