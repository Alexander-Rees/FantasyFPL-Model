import React from 'react';
import { useNavigate } from 'react-router-dom';

import backgroundImage from '../PLTrophy.jpg';

const HomePage = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate('/login');
  };

  const handleRegister = () => {
    navigate('/register');
  };

  return (
    <div 
      style={{ 
        textAlign: 'center', 
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'center center',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'black',
        padding: '20px',
      }}
    >
      <h1>Welcome to the Fantasy Premier League App with Fine-tuned Predictor Model</h1>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        <button 
          onClick={handleLogin} 
          style={{ 
            padding: '10px 20px', 
            fontSize: '16px', 
            cursor: 'pointer',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            width: '200px'
          }}
        >
          Login
        </button>
        <button 
          onClick={handleRegister} 
          style={{ 
            padding: '10px 20px', 
            fontSize: '16px', 
            cursor: 'pointer',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            width: '200px'
          }}
        >
          Register
        </button>
      </div>
    </div>
  );
};

export default HomePage;
