import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  const handleTeamView = () => {
    navigate('/team'); // Navigate to the login page
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '20%' }}>
      <h1>Welcome to the Fantasy Premier League</h1>
      <button 
        onClick={handleTeamView} 
        style={{ 
          marginTop: '20px', 
          padding: '10px 20px', 
          fontSize: '16px', 
          cursor: 'pointer' 
        }}
      >
        View Team
      </button>
    </div>
  );
};

export default HomePage;
