import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 페이지 이동을 위한 useNavigate 추가
import axios from 'axios';
import './Edit.css';

function Edit() {
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate(); // useNavigate 훅 초기화

  const handleEdit = async () => {
    try {
      const user_id = localStorage.getItem('user_id'); // 로컬 저장소에서 user_id 가져오기
      if (!user_id) {
        alert('사용자 정보가 없습니다. 다시 로그인하세요.');
        navigate('/login');
        return;
      }

      // 요청 데이터
      const editData = {
        username,
        name,
        phone,
        password,
      };

      // PATCH 요청
      const response = await axios.patch(
        `http://127.0.0.1:5000/api/v1/login/update/${user_id}`,
        editData,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      console.log('Response from server:', response.data);
      if (response.data.error) {
        alert(response.data.message);
        return;
      }

      // 업데이트된 데이터를 로컬 스토리지에 저장
      const updatedUser = response.data.user;
      localStorage.setItem('user_name', updatedUser.name || '');
      localStorage.setItem('user_id', updatedUser._id || '');
      localStorage.setItem('username', updatedUser.username || '');
      localStorage.setItem('phone', updatedUser.phone || '');

      alert('회원정보가 성공적으로 수정되었습니다.');
      navigate('/main'); // main 페이지로 이동
    } catch (error) {
      console.error('Error during profile update:', error.message);
      alert('회원정보 수정 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-title">회원 정보 수정</h2>
      <form className="login-form">
        <input
          type="text"
          placeholder="아이디 (8자리 이상의 영문)"
          className="login-input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="text"
          placeholder="이름"
          className="login-input"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="text"
          placeholder="전화번호 (예: 010-1234-5678)"
          className="login-input"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <input
          type="password"
          placeholder="비밀번호"
          className="login-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="button" className="login-button" onClick={handleEdit}>
          수정하기
        </button>
      </form>
    </div>
  );
}

export default Edit;
