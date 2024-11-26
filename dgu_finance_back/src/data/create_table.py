import os
from pymongo import MongoClient, errors
from datetime import datetime, timezone
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri)
db = client.get_database(os.environ.get("MONGO_DATABASE"))

# 컬렉션 참조
item_collection = db["Item"]
ohlcv_collection = db["OHLCV"]
fundamental_collection = db["Fundamental"]

def convert_unix_to_datetime(unix_timestamp):
    if unix_timestamp:
        return datetime.fromtimestamp(unix_timestamp, timezone.utc).strftime('%Y-%m-%d')
    return None

# 나스닥 종목 리스트 가져오기
def get_nasdaq_tickers():
    nasdaq_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    try:
        # 나스닥 데이터 크롤링
        nasdaq_data = pd.read_csv(nasdaq_url, sep='|')
        tickers = nasdaq_data['Symbol'].dropna().tolist()
        tickers = [ticker for ticker in tickers if ticker != 'Symbol']  # 헤더 제외
        return tickers
    except Exception as e:
        print(f"Error fetching NASDAQ tickers: {e}")
        return []

# 티커 데이터를 MongoDB에 저장
def insert_ticker_data(ticker_symbol):
    try:
        # yfinance에서 데이터 가져오기
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        ohlcv_data = ticker.history(period="1mo", interval="1d")  # 지난 한 달간의 일봉 데이터

        # Step 1: Item 컬렉션에 데이터 삽입
        item_data = {
            "code": info.get("symbol"),
            "name": info.get("shortName"),
            "country": info.get("country"),
            "market": info.get("exchange"),
            "sector_name": info.get("sector"),
            "sector_code": info.get("sectorKey"),
            "type": "EQUITY" if info.get("quoteType") == "EQUITY" else None
        }
        item_data = {k: v for k, v in item_data.items() if v is not None}

        if not item_collection.find_one({"code": ticker_symbol}):
            item_collection.insert_one(item_data)
            print(f"Inserted Item data for {ticker_symbol}")
        else:
            print(f"Item data for {ticker_symbol} already exists, skipping.")

        # Step 2: OHLCV 컬렉션 데이터 삽입
        for timestamp, row in ohlcv_data.iterrows():
            ohlcv_data_row = {
                "code": ticker_symbol,
                "timestamp": timestamp.strftime("%Y-%m-%d"),  # UNIX timestamp
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
                "trading_val": row["Volume"] * row["Close"] if row["Volume"] and row["Close"] else None
            }
            ohlcv_data_row = {k: v for k, v in ohlcv_data_row.items() if v is not None}
            try:
                ohlcv_collection.update_one(
                    {"code": ticker_symbol, "timestamp": ohlcv_data_row["timestamp"]},
                    {"$set": ohlcv_data_row},
                    upsert=True
                )
            except errors.DuplicateKeyError:
                continue

        # Step 3: Fundamental 컬렉션 데이터 삽입
        fundamental_data = {
            "code": info.get("symbol"),
            "timestamp": convert_unix_to_datetime(info.get("mostRecentQuarter")),
            "close": info.get("currentPrice"),
            "volume": info.get("regularMarketVolume"),
            "issued_share": info.get("sharesOutstanding"),
            "cap": info.get("marketCap"),
            "sector_per": info.get("trailingPE"),
            "dividend": info.get("dividendRate"),
            "total_revenue": info.get("totalRevenue"),
            "operating_income": info.get("operatingCashflow"),
            "net_income": info.get("netIncomeToCommon"),
            "total_assets": info.get("totalAssets"),
            "total_liabilities": info.get("totalDebt"),
            "total_equity": info.get("bookValue")
        }
        fundamental_data = {k: v for k, v in fundamental_data.items() if v is not None}
        try:
            fundamental_collection.update_one(
                {"code": ticker_symbol, "timestamp": fundamental_data["timestamp"]},
                {"$set": fundamental_data},
                upsert=True
            )
            print(f"Inserted Fundamental data for {ticker_symbol}")
        except errors.DuplicateKeyError:
            print(f"Fundamental data for {ticker_symbol} already exists, skipping.")

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")

# 모든 나스닥 티커의 데이터를 가져오고 저장
def fetch_and_store_all_tickers():
    tickers = get_nasdaq_tickers()
    print(f"Total NASDAQ tickers: {len(tickers)}")

    for ticker_symbol in tickers:
        try:
            print(f"Fetching data for {ticker_symbol}...")
            insert_ticker_data(ticker_symbol)
        except Exception as e:
            print(f"Error processing {ticker_symbol}: {e}")

if __name__ == '__main__':
    fetch_and_store_all_tickers()