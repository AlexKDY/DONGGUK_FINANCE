import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri)
db = client.get_database(os.environ.get("MONGO_DATABASE"))
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
item_collection = db["article"]

def get_news_sentiment(ticker):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if 'feed' in data:
        articles = []  # 뉴스 정보를 저장할 리스트
        for article in data['feed']:
            articles.append({
                "title": article.get('title', 'No title'),
                "url": article.get('url', 'No URL'),
                "summary": article.get('summary', 'No summary'),
                "sentiment": article.get('overall_sentiment_label', 'No sentiment')
            })

        # MongoDB에 저장
        doc = {
            "code": ticker,
            "article": articles
        }
        item_collection.insert_one(doc)  # MongoDB에 문서 삽입

        print(f"{ticker} 뉴스가 MongoDB에 성공적으로 저장되었습니다.")
    else:
        print("뉴스 데이터를 가져오지 못했습니다.")

# 사용 예시
if __name__ == "__main__":
    ticker = 'AAPL'  # 조회할 주식 티커
    get_news_sentiment(ticker)
