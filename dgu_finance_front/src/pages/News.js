import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import './News.css';

function News() {
  const location = useLocation();
  const { code } = location.state || {}; // Item 페이지에서 전달된 종목 코드
  const [newsData, setNewsData] = useState([]); // 뉴스 데이터를 저장
  const [userName, setUserName] = useState(''); // 사용자 이름 저장

  useEffect(() => {
    // 사용자 이름 가져오기
    const storedName = localStorage.getItem('user_name') || 'Guest';
    setUserName(storedName);

    // 종목 뉴스 데이터 가져오기
    const fetchNewsData = async () => {
      try {
        console.log('Fetching news for code:', code); // 디버깅: 종목 코드 확인
        const response = await axios.post(
          'http://127.0.0.1:5000/api/v1/article/', // API 엔드포인트
          { code }, // 종목 코드 전송
          { headers: { 'Content-Type': 'application/json' } }
        );
        console.log('Response from server:', response.data); // 디버깅: 서버 응답 확인

        if (response.data.error) {
          alert(response.data.message);
          return;
        }

        setNewsData(response.data.data || []); // MongoDB의 article 배열 저장
      } catch (error) {
        console.error('Failed to fetch news data:', error);
        alert('뉴스 데이터를 가져오는 데 실패했습니다.');
      }
    };

    if (code) {
      fetchNewsData();
    }
  }, [code]);

  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'bullish':
      case 'somewhat-bullish':
        return 'green';
      case 'neutral':
        return 'gray';
      case 'bearish':
      case 'somewhat-bearish':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <div className="news-container">
      {/* 헤더 */}
      <header className="news-header">
        <h1 className="news-logo">DGU FINANCE</h1>
        <h2 className="news-title">NEWS</h2>
        <div className="header-right">
          <span className="user-name">{userName}님</span>
        </div>
      </header>

      {/* 콘텐츠 영역 */}
      <main className="news-content">
        {newsData.length > 0 ? (
          <ul className="news-list">
            {newsData.map((article, index) => (
              <li key={index} className="news-item">
                <h3>{article.title}</h3>
                <p>{article.summary}</p>
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  본문 읽기
                </a>
                <p
                  className="news-sentiment"
                  style={{ color: getSentimentColor(article.sentiment), marginTop: '10px' }}
                >
                  {article.sentiment}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p>뉴스 데이터가 없습니다.</p>
        )}
      </main>
    </div>
  );
}

export default News;
