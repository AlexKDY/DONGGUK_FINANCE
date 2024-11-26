import React, { useState, useEffect } from 'react';
import './ItemList.css'; 

const ItemList = () => {
  const [items, setItems] = useState([]); // Item 리스트 상태 저장
  const [loading, setLoading] = useState(true); // 로딩 상태 저장

  useEffect(() => {
    // API 호출 함수
    const fetchItems = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/v1/item/list'); // Flask API 호출
        const data = await response.json();
        setItems(data); // API에서 받아온 데이터를 상태에 저장
        setLoading(false); // 로딩 상태 변경
      } catch (error) {
        console.error('Failed to fetch items:', error);
        setLoading(false); // 로딩 상태 변경
      }
    };

    fetchItems(); // API 호출
  }, []);

  if (loading) {
    return <div>Loading...</div>; // 로딩 중 표시
  }

  return (
    <div style={{ height: '400px', overflowY: 'scroll', border: '1px solid #ddd', padding: '10px' }}>
      {items.map((item) => (
        <div key={item._id} style={{ marginBottom: '10px' }}>
          <h3>{item.name}</h3>
          <p>
            <strong>Code:</strong> {item.code} <br />
            <strong>Country:</strong> {item.country} <br />
            <strong>Market:</strong> {item.market}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ItemList;
