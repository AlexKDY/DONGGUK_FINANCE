import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import './Item.css';

function Item() {
  const location = useLocation();
  const navigate = useNavigate();
  const { item } = location.state || {}; // Main에서 전달된 데이터
  const [chartData, setChartData] = useState([]); // 주가 데이터를 저장
  const [fundamentalData, setFundamentalData] = useState(null); // Fundamental 데이터를 저장
  const [userName, setUserName] = useState(''); // 사용자 이름 저장
  const [visibleMetrics, setVisibleMetrics] = useState({
    close: true,
    high: false,
    low: false,
    open: false,
  }); // 선택한 데이터 상태 관리
  const [activeTab, setActiveTab] = useState('graph'); // 현재 활성화된 탭 ('graph' 또는 'fundamental')

  useEffect(() => {
    // 사용자 이름 가져오기
    const storedName = localStorage.getItem('user_name') || 'Guest';
    setUserName(storedName);

    // 종목 데이터 가져오기
    const fetchOhlcvData = async () => {
      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/api/v1/ohlcv/',
          { code: item.code },
          { headers: { 'Content-Type': 'application/json' } }
        );
        setChartData(response.data.data);
      } catch (error) {
        console.error('Failed to fetch OHLCV data:', error);
        alert('데이터를 가져오는 데 실패했습니다.');
      }
    };

    if (item) {
      fetchOhlcvData();
    }
  }, [item]);

  // Fundamental 데이터 가져오기
  const fetchFundamentalData = async () => {
    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/v1/fundamental/',
        { code: item.code },
        { headers: { 'Content-Type': 'application/json' } }
      );
      if (response.data.error) {
        alert(response.data.message);
        return;
      }
      setFundamentalData(response.data.data); // 데이터 저장
    } catch (error) {
      console.error('Failed to fetch Fundamental data:', error);
      alert('Fundamental 데이터를 가져오는 데 실패했습니다.');
    }
  };

  if (!item) {
    return <div>종목 데이터를 찾을 수 없습니다.</div>;
  }

  // 체크박스 상태 변경 핸들러
  const handleCheckboxChange = (metric) => {
    setVisibleMetrics((prev) => ({
      ...prev,
      [metric]: !prev[metric],
    }));
  };

  // 탭 변경 핸들러
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'fundamental') {
      fetchFundamentalData();
    }
  };
  const handleNewsPage = () => {
    navigate('/news', { state: { code: item.code } }); // 뉴스 페이지로 이동
  };
  const handleUserClick = () => {
    navigate('/user'); // User 페이지로 이동
  };
  return (
    <div className="item-container">
      {/* 헤더 */}
      <header className="item-header">
        <h1 className="item-logo">DGU FINANCE</h1>
        <div className="header-right">
        <span className="user-name" onClick={handleUserClick} style={{ cursor: 'pointer' }}>
            {userName}님
          </span>
        </div>
      </header>

      {/* 콘텐츠 영역 */}
      <main className="item-content">
        {/* 종목 이름 */}
        <h2 className="stock-title">{item.code}</h2>

        {/* 버튼 영역 */}
        <div className="button-container">
          <button
            className={`item-button ${activeTab === 'graph' ? 'active' : ''}`}
            onClick={() => handleTabChange('graph')}
          >
            주가 그래프
          </button>
          <button
            className={`item-button ${activeTab === 'fundamental' ? 'active' : ''}`}
            onClick={() => handleTabChange('fundamental')}
          >
            재무정보
          </button>
          <button
            className="item-button"
            onClick={handleNewsPage} // 뉴스 페이지로 이동
          >
            종목뉴스
          </button>
        </div>

        {/* 주가 그래프 */}
        {activeTab === 'graph' && (
          <>
            {/* 체크박스 영역 */}
            <div className="checkbox-container">
              <label>
                <input
                  type="checkbox"
                  checked={visibleMetrics.close}
                  onChange={() => handleCheckboxChange('close')}
                />
                종가
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={visibleMetrics.high}
                  onChange={() => handleCheckboxChange('high')}
                />
                최고가
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={visibleMetrics.low}
                  onChange={() => handleCheckboxChange('low')}
                />
                최저가
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={visibleMetrics.open}
                  onChange={() => handleCheckboxChange('open')}
                />
                시가
              </label>
            </div>

            {/* 차트 영역 */}
            <div className="chart-container">
              <h2>주가 그래프</h2>
              <ResponsiveContainer width="95%" height={400}>
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  {/* 막대 그래프 (종가) */}
                  {visibleMetrics.close && (
                    <Bar dataKey="close" fill="#8884d8" name="종가" />
                  )}
                  {visibleMetrics.high && (
                    <Bar dataKey="high" fill="#82ca9d" name="최고가" />
                  )}
                  {visibleMetrics.low && (
                    <Bar dataKey="low" fill="#ff7300" name="최저가" />
                  )}
                  {visibleMetrics.open && (
                    <Bar dataKey="open" fill="#ffa500" name="시가" />
                  )}
                </ComposedChart>
              </ResponsiveContainer>

              {/* 거래금액과 거래량 */}
              <div className="volume-chart">
                <h3>거래금액 및 거래량</h3>
                <ResponsiveContainer width="95%" height={200}>
                  <ComposedChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis yAxisId="left" orientation="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Bar yAxisId="left" dataKey="volume" fill="#8884d8" name="거래량" />
                    <Bar yAxisId="right" dataKey="trading_val" fill="#82ca9d" name="거래금액" />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}

        {/* 재무정보 */}
        {activeTab === 'fundamental' && fundamentalData && (
          <div className="fundamental-container">
            <h3>재무 정보</h3>
            <table className="fundamental-table">
              <thead>
                <tr>
                  <th colSpan="2"></th>
                </tr>
              </thead>
              <tbody>
                {[
                  { key: 'cap', label: '시가총액', isDollar: true },
                  { key: 'close', label: '현재가', isDollar: true },
                  { key: 'dividend', label: '배당금', isDollar: true },
                  { key: 'issued_share', label: '발행 주식량', isDollar: false },
                  { key: 'net_income', label: '순이익', isDollar: true },
                  { key: 'operating_income', label: '영업이익', isDollar: true },
                  { key: 'sector_per', label: '주당 순이익', isDollar: true },
                  { key: 'total_equity', label: '자기자본', isDollar: true },
                  { key: 'total_liabilities', label: '총 부채', isDollar: true },
                  { key: 'total_revenue', label: '매출', isDollar: true },
                  { key: 'volume', label: '거래량', isDollar: false },
                ].map(({ key, label, isDollar }) => (
                  <tr key={key}>
                    <td>{label}</td>
                    <td>
                      {isDollar ? `$${fundamentalData[key]}` : fundamentalData[key]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default Item;
