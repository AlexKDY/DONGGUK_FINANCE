import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 페이지 이동을 위한 useNavigate 추가
import axios from 'axios';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate(); // useNavigate 훅 초기화

  const handleLogin = async () => {
    try {
      // 요청 데이터
      const loginData = {
        username,
        password,
      };

      // POST 요청
      const response = await axios.post('http://127.0.0.1:5000/api/v1/login/', loginData, {
        headers: {
          'Content-Type': 'application/json', // JSON 형식으로 지정
        },
      });
      
      console.log('Response from server:', response.data);
      const { user_id, name } = response.data.user;
      localStorage.setItem('user_id', user_id);
      localStorage.setItem('user_name', name);
      alert(`로그인 성공! 환영합니다, ${name}!`);
    
      // main 페이지로 이동
      navigate('/main'); // '/main' 경로로 이동
    } catch (error) {
      // 오류 처리
      if (error.response) {
        console.error('Error response:', error.response.data);
        alert(`로그인 실패: ${error.response.data.message}`);
      } else {
        console.error('Error:', error.message);
        alert('로그인 실패: 네트워크 오류가 발생했습니다.');
      }

      // 페이지 새로고침
      window.location.reload();
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-title">로그인하세요</h2>
      <form className="login-form">
        <input
          type="text"
          placeholder="아이디"
          className="login-input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="비밀번호"
          className="login-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="button" className="login-button" onClick={handleLogin}>
          로그인 시도
        </button>
      </form>
    </div>
  );
}

export default Login;
