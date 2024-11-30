import React from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './User.css';

function User() {
  const name = localStorage.getItem('user_name') || 'Guest'; // 사용자 이름 가져오기
  const user_id = localStorage.getItem('user_id');
  const navigate = useNavigate(); // 페이지 이동을 위한 useNavigate

  // 로그아웃 기능
  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  // 회원정보 수정 기능
  const handleEditInfo = () => {
    // 회원정보 수정 페이지로 이동
    navigate('/edit', { state: { user_id } });
  };

  // 회원 탈퇴 기능
  const handleDeleteAccount = async () => {
    if (!user_id) {
      alert('사용자 정보가 없습니다. 다시 로그인하세요.');
      navigate('/login');
      return;
    }

    const confirmDelete = window.confirm(
      '정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.'
    );

    if (confirmDelete) {
      try {
        const response = await axios.delete(`http://127.0.0.1:5000/api/v1/signup/delete/${user_id}`);
        console.log('Response from server:', response.data);

        if (response.data.error) {
          alert(response.data.message);
          return;
        }

        alert('계정이 성공적으로 삭제되었습니다.');
        localStorage.clear(); // 로컬 스토리지 비우기
        navigate('/login'); // 로그인 페이지로 이동
      } catch (error) {
        console.error('Error during account deletion:', error.message);
        alert('계정을 삭제하는 중 오류가 발생했습니다.');
      }
    }
  };

  return (
    <div className="user-container">
      {/* 헤더 */}
      <header className="main-header">
        <h1 className="main-logo">DGU FINANCE</h1>
        <div className="header-right">
          <span className="user-name">{name}님</span>
        </div>
      </header>

      {/* 콘텐츠 영역 */}
      <main className="user-content">
        <button className="user-button" onClick={handleLogout}>
          로그아웃
        </button>
        <button className="user-button" onClick={handleEditInfo}>
          회원정보 수정
        </button>
        <button className="user-button" onClick={handleDeleteAccount}>
          회원탈퇴
        </button>
      </main>
    </div>
  );
}

export default User;
