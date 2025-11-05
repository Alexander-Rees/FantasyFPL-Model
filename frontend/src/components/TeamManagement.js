import React, { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { logoutUser } from '../actions/authActions';
import './TeamManagement.css';

const TeamManagement = () => {
  const [fplEntryId, setFplEntryId] = useState('');
  const [isImporting, setIsImporting] = useState(false);
  const [importMessage, setImportMessage] = useState('');
  const [teamData, setTeamData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Optimization states
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [optimizationError, setOptimizationError] = useState('');
  const [optimizationSettings, setOptimizationSettings] = useState({
    budget: 100.0,
    freeTransfers: 1,
    formation: '3-4-3',
    lockedPlayers: [],
    avoidPlayers: []
  });
  
  const { user, isAuthenticated } = useSelector(state => state.auth);
  const dispatch = useDispatch();

  const fetchTeamData = useCallback(async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      console.log('Fetching team data for user ID:', user.id);
      const response = await fetch(`http://localhost:8081/api/team/players?userId=${user.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Team data response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Team data received:', data);
        setTeamData(data);
      } else {
        console.error('Failed to fetch team data:', response.status);
      }
    } catch (error) {
      console.error('Error fetching team data:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchTeamData();
    }
  }, [isAuthenticated, user, fetchTeamData]);

  const handleImportTeam = async (e) => {
    e.preventDefault();
    if (!fplEntryId.trim()) {
      setImportMessage('Please enter a valid FPL Entry ID');
      return;
    }

    setIsImporting(true);
    setImportMessage('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8081/api/team/import/fpl-entry?userId=${user.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ entryId: parseInt(fplEntryId) })
      });

      if (response.ok) {
        const data = await response.json();
        setImportMessage(`✅ Team imported successfully! Team: ${data.name}`);
        setFplEntryId('');
        // Refresh team data
        fetchTeamData();
      } else {
        const errorData = await response.json();
        setImportMessage(`❌ Import failed: ${errorData.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Import error:', error);
      setImportMessage(`❌ Import failed: ${error.message}`);
    } finally {
      setIsImporting(false);
    }
  };

  const handleOptimizeTeam = async () => {
    if (!teamData || teamData.length === 0) {
      setOptimizationError('Please import your team first before optimizing');
      return;
    }

    setIsOptimizing(true);
    setOptimizationError('');
    setOptimizationResult(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8081/api/team/optimize?userId=${user.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(optimizationSettings)
      });

      if (response.ok) {
        const data = await response.json();
        setOptimizationResult(data);
        console.log('Optimization result:', data);
      } else {
        const errorData = await response.json();
        setOptimizationError(`Optimization failed: ${errorData.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Optimization error:', error);
      setOptimizationError(`Optimization failed: ${error.message}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleLogout = () => {
    dispatch(logoutUser());
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="team-management">
        <div className="auth-required">
          <h2>Authentication Required</h2>
          <p>Please log in to manage your team.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="team-management">
      <div className="team-header">
        <div className="user-info">
          <h2>Welcome, {user.name || 'User'}!</h2>
          <p className="user-email">{user.email || ''}</p>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="team-content">
        <div className="import-section">
          <h3>Import Your FPL Team</h3>
          <p className="import-description">
            Enter your Fantasy Premier League Entry ID to import your current team.
            You can find this in your FPL profile URL or team page.
          </p>
          
          <form onSubmit={handleImportTeam} className="import-form">
            <div className="input-group">
              <label htmlFor="fplEntryId">FPL Entry ID:</label>
              <input
                type="number"
                id="fplEntryId"
                value={fplEntryId}
                onChange={(e) => setFplEntryId(e.target.value)}
                placeholder="e.g., 4084655"
                disabled={isImporting}
                required
              />
            </div>
            <button 
              type="submit" 
              className="import-btn"
              disabled={isImporting || !fplEntryId.trim()}
            >
              {isImporting ? 'Importing...' : 'Import Team'}
            </button>
          </form>

          {importMessage && (
            <div className={`import-message ${importMessage.includes('✅') ? 'success' : 'error'}`}>
              {importMessage}
            </div>
          )}
        </div>

        <div className="team-section">
          <div className="team-header-section">
            <h3>My Team</h3>
            {teamData && teamData.length > 0 && (
              <button 
                className="optimize-btn"
                onClick={handleOptimizeTeam}
                disabled={isOptimizing}
              >
                {isOptimizing ? 'Optimizing...' : '🤖 Optimize Team'}
              </button>
            )}
          </div>
          
          {loading ? (
            <div className="loading">Loading team data...</div>
          ) : teamData && teamData.length > 0 ? (
            <div className="team-players">
              <h4>Players ({teamData.length})</h4>
              <div className="players-grid">
                {teamData.map((player, index) => (
                  <div key={player.id || index} className="player-card">
                    <div className="player-name">{player.name}</div>
                    <div className="player-details">
                      <span className="player-position">{player.position}</span>
                      <span className="player-team">{player.team}</span>
                    </div>
                    <div className="player-stats">
                      <span className="player-value">£{player.value}m</span>
                      <span className="player-points">{player.totalPoints} pts</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-team">
              <p>No team imported yet. Use the form above to import your FPL team.</p>
            </div>
          )}
        </div>

        {/* Optimization Settings */}
        {teamData && teamData.length > 0 && (
          <div className="optimization-settings">
            <h3>Optimization Settings</h3>
            <div className="settings-grid">
              <div className="setting-group">
                <label htmlFor="budget">Budget (M):</label>
                <input
                  type="number"
                  id="budget"
                  value={optimizationSettings.budget}
                  onChange={(e) => setOptimizationSettings({
                    ...optimizationSettings,
                    budget: parseFloat(e.target.value) || 100.0
                  })}
                  min="50"
                  max="200"
                  step="0.1"
                />
              </div>
              <div className="setting-group">
                <label htmlFor="freeTransfers">Free Transfers:</label>
                <input
                  type="number"
                  id="freeTransfers"
                  value={optimizationSettings.freeTransfers}
                  onChange={(e) => setOptimizationSettings({
                    ...optimizationSettings,
                    freeTransfers: parseInt(e.target.value) || 1
                  })}
                  min="0"
                  max="15"
                />
              </div>
              <div className="setting-group">
                <label htmlFor="formation">Formation:</label>
                <select
                  id="formation"
                  value={optimizationSettings.formation}
                  onChange={(e) => setOptimizationSettings({
                    ...optimizationSettings,
                    formation: e.target.value
                  })}
                >
                  <option value="3-4-3">3-4-3</option>
                  <option value="3-5-2">3-5-2</option>
                  <option value="4-4-2">4-4-2</option>
                  <option value="4-3-3">4-3-3</option>
                  <option value="5-4-1">5-4-1</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Optimization Results */}
        {optimizationError && (
          <div className="optimization-error">
            <h4>❌ Optimization Error</h4>
            <p>{optimizationError}</p>
          </div>
        )}

        {optimizationResult && (
          <div className="optimization-results">
            <h3>🎯 AI Optimization Results</h3>
            
            <div className="results-summary">
              <div className="summary-item">
                <span className="summary-label">Total Value:</span>
                <span className="summary-value">£{optimizationResult.totalValue?.toFixed(1)}M</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Expected Points:</span>
                <span className="summary-value">{optimizationResult.totalPoints?.toFixed(0)} pts</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Formation:</span>
                <span className="summary-value">{optimizationResult.formation}</span>
              </div>
            </div>

            {optimizationResult.captain && (
              <div className="captain-section">
                <h4>👑 Captain: {optimizationResult.captain.name}</h4>
                <p>{optimizationResult.captain.position} • {optimizationResult.captain.team} • £{optimizationResult.captain.value}M • {optimizationResult.captain.totalPoints} pts</p>
              </div>
            )}

            {optimizationResult.viceCaptain && optimizationResult.viceCaptain.id !== optimizationResult.captain?.id && (
              <div className="vice-captain-section">
                <h4>🔄 Vice-Captain: {optimizationResult.viceCaptain.name}</h4>
                <p>{optimizationResult.viceCaptain.position} • {optimizationResult.viceCaptain.team} • £{optimizationResult.viceCaptain.value}M • {optimizationResult.viceCaptain.totalPoints} pts</p>
              </div>
            )}

            {optimizationResult.transfers && optimizationResult.transfers.length > 0 && (
              <div className="transfers-section">
                <h4>🔄 Transfer Suggestions</h4>
                <div className="transfers-list">
                  {optimizationResult.transfers.map((transfer, index) => (
                    <div key={index} className="transfer-item">
                      <div className="transfer-out">
                        <span className="transfer-label">OUT:</span>
                        <span className="transfer-player">{transfer.playerOut?.name}</span>
                        <span className="transfer-details">({transfer.playerOut?.position}, £{transfer.playerOut?.value}M)</span>
                      </div>
                      <div className="transfer-arrow">→</div>
                      <div className="transfer-in">
                        <span className="transfer-label">IN:</span>
                        <span className="transfer-player">{transfer.playerIn?.name}</span>
                        <span className="transfer-details">({transfer.playerIn?.position}, £{transfer.playerIn?.value}M)</span>
                      </div>
                      <div className="transfer-cost">
                        <span className="cost-label">Cost:</span>
                        <span className="cost-value">£{transfer.cost?.toFixed(1)}M</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {optimizationResult.optimalTeam && optimizationResult.optimalTeam.length > 0 && (
              <div className="optimal-team-section">
                <h4>⭐ Optimal Team</h4>
                <div className="optimal-players-grid">
                  {optimizationResult.optimalTeam.map((player, index) => (
                    <div key={player.id || index} className="optimal-player-card">
                      <div className="player-name">{player.name}</div>
                      <div className="player-details">
                        <span className="player-position">{player.position}</span>
                        <span className="player-team">{player.team}</span>
                      </div>
                      <div className="player-stats">
                        <span className="player-value">£{player.value}m</span>
                        <span className="player-points">{player.totalPoints} pts</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamManagement;
