import React, { useState, useEffect } from 'react';
import './Main.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Main() {
  const [name, setName] = useState('');
  const [userId, setUserId] = useState(''); // 사용자 ID 저장
  const [myStocks, setMyStocks] = useState([]);
  const [searchTerm, setSearchTerm] = useState(''); // 검색어 상태 추가
  const [searchResults, setSearchResults] = useState([]); // 검색 결과 상태 추가
  const navigate = useNavigate(); // React Router navigate 함수

  useEffect(() => {
    // 로컬 저장소에서 사용자 이름 및 ID 가져오기
    const storedName = localStorage.getItem('user_name') || 'Guest';
    const storedUserId = localStorage.getItem('user_id') || '';
    setName(storedName);
    setUserId(storedUserId);

    // 관심 종목 데이터 가져오기
    const fetchMyStocks = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/api/v1/mystock/list/${storedUserId}`
        );
        setMyStocks(response.data.mystock || []);
      } catch (error) {
        console.error('Failed to fetch my stocks:', error);
        alert('관심 종목 정보를 가져오는 데 실패했습니다.');
      }
    };

    if (storedUserId) {
      fetchMyStocks();
    }
  }, []);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      alert('검색어를 입력하세요.');
      return;
    }

    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/v1/item/search',
        { item: searchTerm },
        { headers: { 'Content-Type': 'application/json' } }
      );

      if (response.data.error) {
        alert(response.data.message);
      } else {
        setSearchResults(response.data.data); // 검색 결과 저장
      }
    } catch (error) {
      console.error('Failed to search item:', error);
      alert('검색 중 오류가 발생했습니다.');
    }
  };

  const handleAddFavorite = async (code) => {
    if (!userId) {
      alert('사용자 ID를 찾을 수 없습니다. 다시 로그인 해주세요.');
      return;
    }

    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/v1/mystock/',
        { code, user_id: userId },
        { headers: { 'Content-Type': 'application/json' } }
      );

      if (response.data.error) {
        alert(response.data.message);
      } else {
        alert('관심 종목에 등록되었습니다!');
        setMyStocks((prev) => [...prev, code]); // 관심 종목 목록에 추가
      }
    } catch (error) {
      console.error('Failed to add favorite stock:', error);
      alert('관심 종목 등록 중 오류가 발생했습니다.');
    }
  };

  const handleRemoveFavorite = async (code) => {
    if (!userId) {
      alert('사용자 ID를 찾을 수 없습니다. 다시 로그인 해주세요.');
      return;
    }

    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/v1/mystock/delete',
        { code, user_id: userId },
        { headers: { 'Content-Type': 'application/json' } }
      );

      if (response.data.error) {
        alert(response.data.message);
      } else {
        alert('관심 종목에서 삭제되었습니다!');
        setMyStocks((prev) => prev.filter((stock) => stock !== code)); // 관심 종목 목록에서 제거
      }
    } catch (error) {
      console.error('Failed to remove favorite stock:', error);
      alert('관심 종목 삭제 중 오류가 발생했습니다.');
    }
  };

  const handleRowClick = (item) => {
    navigate('/item', { state: { item } }); // 데이터와 함께 item으로 이동
  };

  const handleMyStockClick = (stock) => {
    // 관심 종목 클릭 시 해당 종목 페이지로 이동
    navigate('/item', { state: { item: { code: stock } } });
  };

  const handleUserClick = () => {
    navigate('/user'); // User 페이지로 이동
  };

  return (
    <div className="main-container">
      {/* 헤더 */}
      <header className="main-header">
        <h1 className="main-logo">DGU FINANCE</h1>
        <div className="header-right">
          <span className="user-name" onClick={handleUserClick} style={{ cursor: 'pointer' }}>
            {name}님
            </span>
        </div>
      </header>

      {/* 콘텐츠 영역 */}
      <main className="main-content">
        {/* 검색창 */}
        <div className="search-bar-container">
          <input
            type="text"
            className="search-bar"
            placeholder="종목을 검색하세요"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button className="search-button" onClick={handleSearch}>
            검색
          </button>
        </div>

        {/* 관심 종목 컨테이너 */}
        <div className="stock-container">
          <h2>내 관심 종목</h2>
          {myStocks.length === 0 ? (
            <p>관심 종목 정보가 없습니다.</p>
          ) : (
            <ul className="stock-list">
              {myStocks.map((stock, index) => (
                <li key={index} className="stock-item">
                  <span onClick={() => handleMyStockClick(stock)}>{stock}</span>
                  <button
                    className="remove-favorite-button"
                    onClick={() => handleRemoveFavorite(stock)}
                  >
                    관심등록해제
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* 검색 결과 컨테이너 */}
        <div className="result-container">
          <h2>검색결과</h2>
          {searchResults.length === 0 ? (
            <p>검색 결과가 없습니다.</p>
          ) : (
            <table className="result-table">
              <thead>
                <tr>
                  <th>종목코드</th>
                  <th>종목명</th>
                  <th>본사위치</th>
                  <th>거래소</th>
                  <th>산업분야</th>
                  <th>타입</th>
                </tr>
              </thead>
              <tbody>
                {searchResults.map((result, index) => (
                  <tr key={index}>
                    <td>
                      <div className="favorite-container">
                        <span onClick={() => handleRowClick(result)}>{result.code}</span>
                        <button
                          className="add-favorite-button"
                          onClick={() => handleAddFavorite(result.code)}
                        >
                          찜하기
                        </button>
                      </div>
                    </td>
                    <td onClick={() => handleRowClick(result)}>{result.name}</td>
                    <td onClick={() => handleRowClick(result)}>{result.country}</td>
                    <td onClick={() => handleRowClick(result)}>{result.market}</td>
                    <td onClick={() => handleRowClick(result)}>{result.sector_name}</td>
                    <td onClick={() => handleRowClick(result)}>{result.type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
}

export default Main;
