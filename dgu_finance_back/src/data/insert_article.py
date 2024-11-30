import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri)
db = client.get_database(os.environ.get("MONGO_DATABASE"))
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
item_collection = db["article"]

def get_nasdaq_tickers():
    nasdaq_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    try:
        nasdaq_data = pd.read_csv(nasdaq_url, sep='|')
        tickers = nasdaq_data['Symbol'].dropna().tolist()
        tickers = [ticker for ticker in tickers if ticker != 'Symbol']
        return tickers
    except Exception as e:
        print(f"Error fetching NASDAQ tickers: {e}")
        return []

def get_news_sentiment(ticker):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if 'feed' in data:
        articles = []
        for article in data['feed']:
            article_data = {
                "title": article.get('title', 'No title'),
                "url": article.get('url', 'No URL'),
                "summary": article.get('summary', 'No summary'),
                "sentiment": article.get('overall_sentiment_label', 'No sentiment')
            }
            articles.append(article_data)

        existing_doc = item_collection.find_one({"code": ticker})

        if existing_doc:
            existing_urls = {article['url'] for article in existing_doc.get("article", [])}
            new_articles = [article for article in articles if article["url"] not in existing_urls]
            if new_articles:
                item_collection.update_one(
                    {"code": ticker},
                    {"$push": {"article": {"$each": new_articles}}}
                )
                print(f"{ticker}의 새로운 뉴스가 추가되었습니다.")
            else:
                print(f"{ticker}에 추가할 새로운 뉴스가 없습니다.")
        else:
            doc = {
                "code": ticker,
                "article": articles
            }
            item_collection.insert_one(doc)
            print(f"{ticker}에 대한 문서가 생성되었습니다.")
    else:
        print(f"{ticker}에 대한 뉴스 데이터를 가져오지 못했습니다.")

if __name__ == "__main__":
    tickers = get_nasdaq_tickers()
    print(f"총 {len(tickers)}개의 NASDAQ 티커를 처리합니다.")

    for ticker in tickers:
        try:
            get_news_sentiment(ticker)
        except Exception as e:
            print(f"{ticker} 처리 중 에러 발생: {e}")
