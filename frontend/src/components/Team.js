import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Team.css";

const Team = () => {
  const [team, setTeam] = useState(null);
  const [totalPlayers, setTotalPlayers] = useState([]);
  const [weeklyPlayers, setWeeklyPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [optimalTeam, setOptimalTeam] = useState([]);
  const [topPlayers, setTopPlayers] = useState(null);
  const [sortCriteria, setSortCriteria] = useState("total_points");
  const [selectedPosition, setSelectedPosition] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("/api/team?userId=1")
      .then((response) => setTeam(response.data))
      .catch((error) =>
        console.error(
          "Error fetching the team:",
          error.response ? error.response.data : error.message
        )
      );

    axios
      .get("/api/players/total")
      .then((response) => {
        setTotalPlayers(response.data);
      })
      .catch((error) => console.error("Error fetching players:", error));

    const gameweek = 1;
    axios
      .get(`/api/players/weekly/${gameweek}`)
      .then((response) => {
        setWeeklyPlayers(response.data);
      })
      .catch((error) => console.error("Error fetching weekly players:", error));

    axios
      .get("/api/team/optimal_team")
      .then((response) => setOptimalTeam(response.data))
      .catch((error) => console.error("Error fetching optimal team:", error));

    axios
      .get("/api/team/top_players")
      .then((response) => setTopPlayers(response.data))
      .catch((error) => console.error("Error fetching top players:", error));
  }, []);

  // Handle search and filtering
  const handleSearch = () => {
    const combinedPlayers = [...totalPlayers, ...weeklyPlayers];
    const result = combinedPlayers
      .filter(
        (player) =>
          selectedPosition === "" ||
          player.position === parseInt(selectedPosition)
      )
      .sort((a, b) => (b[sortCriteria] || 0) - (a[sortCriteria] || 0));
    setFilteredPlayers(result);
  };

  // Handle adding a player to the team by passing the full player object
  const handleAddPlayer = (playerId) => {
    axios
      .post("/api/team?userId=1", { playerId }) // Pass the playerId
      .then((response) => {
        setTeam(response.data);
        setMessage("Player added successfully!");
      })
      .catch((error) => {
        console.error(
          "There was an error adding the player to the team!",
          error
        );
        setMessage("Error adding player to the team.");
      });
  };

  const handleReturn = () => {
    navigate("/dashboard");
  };

  return (
    <div className="team-container">
      <div className="team-header">
        <h2>Your Team</h2>
      </div>

      {team ? (
        <div className="team-section">
          <h3>{team.name}</h3>
          <p>Budget Remaining: ${team.budget}</p>
          <ul>
            {team.players.map((player) => (
              <li key={player.id}>
                <strong>{player.name}</strong> - Position: {player.position},
                Team: {player.team}, Points: {player.points}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>Loading team...</p>
      )}

      <div className="filter-sort-section">
        <h3>Sort and Filter Players</h3>
        <label>Filter by Position: </label>
        <select
          value={selectedPosition}
          onChange={(e) => setSelectedPosition(e.target.value)}
        >
          <option value="">All Positions</option>
          <option value="1">Goalkeeper</option>
          <option value="2">Defender</option>
          <option value="3">Midfielder</option>
          <option value="4">Forward</option>
        </select>

        <select
          value={sortCriteria}
          onChange={(e) => setSortCriteria(e.target.value)}
        >
          <option value="total_points">Total Points</option>
          <option value="value">Value</option>
          <option value="goals_scored">Goals Scored</option>
          <option value="assists">Assists</option>
          <option value="weeklyPoints">Weekly Points</option>
        </select>

        <button onClick={handleSearch}>Search</button>

        <ul>
          {filteredPlayers.length > 0 ? (
            filteredPlayers.map((player) => (
              <li key={player.id} className="player-list-item">
                {player.name} - ${player.value}M (Total Points:{" "}
                {player.total_points}, Weekly Points: {player.weeklyPoints},
                Position: {player.position})
                <button
                  className="add-player-button"
                  onClick={() => handleAddPlayer(player)} // Pass full player object
                >
                  Add to Team
                </button>
              </li>
            ))
          ) : (
            <p>No players found. Adjust the filters or click search again.</p>
          )}
        </ul>
      </div>

      <div className="optimal-team-section">
        <h3>Optimal Team</h3>
        {optimalTeam.length > 0 ? (
          <ul>
            {optimalTeam.map((player, index) => (
              <li key={index}>
                {player.name} - {player.team_x} (Position: {player.position},
                Predicted Points: {player.predicted_points}, Value: $
                {player.value}M)
              </li>
            ))}
          </ul>
        ) : (
          <p>Loading optimal team...</p>
        )}
      </div>

      <div className="highest-predicted-section">
        <h3>Highest predicted points next gameweek</h3>
        {topPlayers ? (
          <ul>
            <p>Top Goalkeepers: </p>
            {topPlayers.GK &&
              topPlayers.GK.map((player, index) => (
                <li key={index}>
                  {player.name} - {player.team_x} (Predicted Points:{" "}
                  {player.predicted_points})
                </li>
              ))}
            <p>Top Defenders: </p>
            {topPlayers.DEF &&
              topPlayers.DEF.map((player, index) => (
                <li key={index}>
                  {player.name} - {player.team_x} (Predicted Points:{" "}
                  {player.predicted_points})
                </li>
              ))}
            <p>Top Midfielders: </p>
            {topPlayers.MID &&
              topPlayers.MID.map((player, index) => (
                <li key={index}>
                  {player.name} - {player.team_x} (Predicted Points:{" "}
                  {player.predicted_points})
                </li>
              ))}
            <p>Top Forwards: </p>
            {topPlayers.FWD &&
              topPlayers.FWD.map((player, index) => (
                <li key={index}>
                  {player.name} - {player.team_x} (Predicted Points:{" "}
                  {player.predicted_points})
                </li>
              ))}
          </ul>
        ) : (
          <p>Loading top players...</p>
        )}
      </div>

      {message && <p>{message}</p>}

      <button onClick={handleReturn} className="return-button">
        Return to Dashboard
      </button>
    </div>
  );
};

export default Team;
