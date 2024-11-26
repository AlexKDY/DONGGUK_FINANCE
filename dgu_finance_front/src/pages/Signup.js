import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // useNavigate 가져오기
import axios from 'axios';
import './Signup.css'; // CSS 파일 포함

function Signup() {
  const [formData, setFormData] = useState({
    username: '',
    name: '',
    phone: '',
    password: '',
  });

  const navigate = useNavigate(); // useNavigate 훅 초기화

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSignup = async () => {
    try {
      // Flask API로 POST 요청
      const response = await axios.post('http://127.0.0.1:5000/api/v1/signup/', formData);
      console.log('Response from server:', response.data);
      alert('회원가입 성공!');
      
      // 로그인 페이지로 이동
      navigate('/login'); // '/login' 경로로 이동
    } catch (error) {
      // 서버에서 반환한 오류 메시지 처리
      if (error.response) {
        console.error('Error response:', error.response.data);
        alert(`회원가입 실패: ${error.response.data.message}`);
      } else {
        // 네트워크 오류 처리
        console.error('Error:', error.message);
        alert('회원가입 실패: 네트워크 오류가 발생했습니다.');
      }

      // 페이지 새로고침 (선택사항)
      window.location.reload();
    }
  };

  return (
    <div className="signup-container">
      <h2 className="signup-title">회원가입하세요</h2>
      <form className="signup-form">
        <input
          type="text"
          name="username"
          placeholder="아이디 (8자리 이상의 영문)"
          className="signup-input"
          value={formData.username}
          onChange={handleChange}
        />
        <input
          type="text"
          name="name"
          placeholder="이름"
          className="signup-input"
          value={formData.name}
          onChange={handleChange}
        />
        <input
          type="text"
          name="phone"
          placeholder="전화번호 (XXX-XXXX-XXXX)"
          className="signup-input"
          value={formData.phone}
          onChange={handleChange}
        />
        <input
          type="password"
          name="password"
          placeholder="비밀번호 (8자리 이상의 영문)"
          className="signup-input"
          value={formData.password}
          onChange={handleChange}
        />
        <button type="button" className="signup-button" onClick={handleSignup}>
          회원가입
        </button>
      </form>
    </div>
  );
}

export default Signup;
