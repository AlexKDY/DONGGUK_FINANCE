import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Main from './pages/Main'; 
import Item from './pages/Item';
import News from './pages/News';

function App() {
  const navigate = useNavigate(); // useNavigate 훅 사용

  return (
    <div className="App">
      <main className="main">
        <div className="content">
          <div className="logo">
            <h1>DGU FINANCE</h1>
          </div>
          <div className="buttons">
            <button className="button signup" onClick={() => navigate('/signup')}>
              Sign Up
            </button>
            <button className="button login" onClick={() => navigate('/login')}>
              Log In
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

function AppWrapper() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/main" element={<Main />} />
        <Route path="/item" element={<Item />} />
        <Route path="/news" element={<News />} />
      </Routes>
    </Router>
  );
}

export default AppWrapper;
