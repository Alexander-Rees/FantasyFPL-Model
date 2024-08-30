import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Team = () => {
  const [team, setTeam] = useState(null);
  const [players, setPlayers] = useState([]);
  const [playerId, setPlayerId] = useState('');
  const navigate = useNavigate(); // useNavigate hook from react-router-dom

  useEffect(() => {
    // Fetch user's current team
    axios.get('/api/team?userId=1')  // Replace with dynamic userId as needed
      .then(response => {
        setTeam(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the team!', error);
      });

    // Fetch all available players (for adding to the team)
    axios.get('/api/players') // Assuming you have an endpoint for this
      .then(response => {
        setPlayers(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the players!', error);
      });
  }, []);

  const handleAddPlayer = () => {
    axios.post('/api/team?userId=1', { id: playerId })  // Corrected request
      .then(response => {
        setTeam(response.data);  // Update the team state with the new team data
      })
      .catch(error => {
        console.error('There was an error adding the player to the team!', error);
      });
  };

  const handleReturn = () => {
    navigate('/dashboard'); // Corrected to use the navigate function
  };

  return (
    <div>
      <h2>Your Team</h2>
      {team ? (
        <div>
          <h3>{team.name}</h3>
          <p>Budget Remaining: ${team.budget}</p>
          <ul>
            {team.players.map(player => (
              <li key={player.id}>
                <strong>{player.name}</strong> - Position: {player.position}, Team: {player.team}, Points: {player.points}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>You don't have a team yet.</p>
      )}

      <div>
        <h3>Add Player to Team</h3>
        <select value={playerId} onChange={e => setPlayerId(e.target.value)}>
          <option value="" disabled>Select a player</option>
          {players.map(player => (
            <option key={player.id} value={player.id}>
              {player.name} - ${player.price} (Points: {player.points})
            </option>
          ))}
        </select>
        <button onClick={handleAddPlayer}>Add Player</button>
      </div>

      <button
        onClick={handleReturn}  // Move onClick inside the button element
        style={{ 
          marginTop: '20px', 
          padding: '10px 20px', 
          fontSize: '16px', 
          cursor: 'pointer' 
        }}
      >
        Return to Dashboard
      </button>
    </div>
  );
};

export default Team;
