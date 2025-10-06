import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector(state => state.auth);

  const handleTeamView = () => {
    navigate('/team');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const handleRegister = () => {
    navigate('/register');
  };

  return (
    <div className="dashboard">
      <div className="dashboard-hero">
        <div className="hero-content">
          <h1 className="hero-title">FPL AI Optimizer</h1>
          <p className="hero-subtitle">
            Get AI-powered team optimization and transfer suggestions for your Fantasy Premier League team
          </p>
          
          {isAuthenticated ? (
            <div className="authenticated-actions">
              <p className="welcome-text">Welcome back, {user?.name || 'User'}!</p>
              <button className="cta-button primary" onClick={handleTeamView}>
                Manage My Team
              </button>
            </div>
          ) : (
            <div className="auth-actions">
              <button className="cta-button primary" onClick={handleLogin}>
                Login
              </button>
              <button className="cta-button secondary" onClick={handleRegister}>
                Sign Up
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2 className="features-title">Why Choose FPL AI Optimizer?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI-Powered Optimization</h3>
              <p>Get intelligent team suggestions based on machine learning models trained on FPL data</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Real-Time Data</h3>
              <p>Fresh player data updated twice daily from official FPL API and advanced statistics</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Quick Import</h3>
              <p>Import your team instantly using your FPL Entry ID - no manual player selection needed</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Smart Transfers</h3>
              <p>Get personalized transfer suggestions based on your budget, formation, and preferences</p>
            </div>
          </div>
        </div>
      </div>

      <div className="how-it-works">
        <div className="container">
          <h2 className="how-it-works-title">How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Import Your Team</h3>
                <p>Enter your FPL Entry ID to automatically import your current team</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>AI Analysis</h3>
                <p>Our AI analyzes your team and suggests optimizations based on current form and fixtures</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Get Suggestions</h3>
                <p>Receive detailed transfer suggestions, captain picks, and formation recommendations</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
