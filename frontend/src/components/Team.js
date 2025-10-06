import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Team.css";

const Team = () => {
  const [team, setTeam] = useState(null);
  const [players, setPlayers] = useState([]);
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
      .get("/api/players")
      .then((response) => {
        console.log("Player data:", response.data); // Log the data to verify the IDs and structure
        setPlayers(response.data);
      })
      .catch((error) => console.error("Error fetching players:", error));

    axios
      .get("/api/team/optimal_team")
      .then((response) => setOptimalTeam(response.data))
      .catch((error) => console.error("Error fetching optimal team:", error));

    axios
      .get("/api/team/top_players")
      .then((response) => setTopPlayers(response.data))
      .catch((error) => console.error("Error fetching top players:", error));
  }, []);

  const handleSearch = () => {
    const result = players
      .filter((player) => {
        if (selectedPosition !== "") {
          return player.position === selectedPosition;
        }
        return true;
      })
      .sort((a, b) => (b[sortCriteria] || 0) - (a[sortCriteria] || 0));

    setFilteredPlayers(result);
  };

  const handleAddPlayer = (playerId, playerValue) => {
    console.log("Adding Player ID:", playerId, "with Value:", playerValue); // Log the player ID and value

    if (team.budget < playerValue) {
      setMessage("Not enough budget to add this player.");
      return;
    }

    axios
      .post("/api/team", null, { params: { userId: 1, playerId } }) // Replace '1' with the actual user ID
      .then((response) => {
        setTeam(response.data); // Update team state with the updated team after adding the player
        setMessage("Player added successfully!");
        console.log("Updated team:", response.data); // Log the updated team data
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
          <option value="event_points">Weekly Points</option>
        </select>

        <button onClick={handleSearch}>Search</button>

        <div className="scrollable-container">
          <ul>
            {filteredPlayers.length > 0 ? (
              filteredPlayers.map((player) => (
                <li key={player.id}>
                  {player.name} - Position: {player.position}, Team:{" "}
                  {player.team}, Value: ${player.value}M, Total Points:{" "}
                  {player.total_points}, Weekly Points: {player.event_points}
                  <button
                    onClick={() => handleAddPlayer(player.id, player.value)}
                  >
                    Add to Team
                  </button>
                </li>
              ))
            ) : (
              <p>No players found. Adjust filters or search again.</p>
            )}
          </ul>
        </div>
      </div>

      <div className="highest-predicted-section">
        <h3>Highest Predicted Points Next Gameweek</h3>
        {topPlayers ? (
          <div className="scrollable-container">
            <ul>
              <p>Top Goalkeepers: </p>
              {topPlayers.GK &&
                topPlayers.GK.slice(0, 10).map((player, index) => (
                  <li key={index}>
                    {player.name} - {player.team_x} (Predicted Points:{" "}
                    {player.predicted_points})
                  </li>
                ))}
              <p>Top Defenders: </p>
              {topPlayers.DEF &&
                topPlayers.DEF.slice(0, 10).map((player, index) => (
                  <li key={index}>
                    {player.name} - {player.team_x} (Predicted Points:{" "}
                    {player.predicted_points})
                  </li>
                ))}
              <p>Top Midfielders: </p>
              {topPlayers.MID &&
                topPlayers.MID.slice(0, 10).map((player, index) => (
                  <li key={index}>
                    {player.name} - {player.team_x} (Predicted Points:{" "}
                    {player.predicted_points})
                  </li>
                ))}
              <p>Top Forwards: </p>
              {topPlayers.FWD &&
                topPlayers.FWD.slice(0, 10).map((player, index) => (
                  <li key={index}>
                    {player.name} - {player.team_x} (Predicted Points:{" "}
                    {player.predicted_points})
                  </li>
                ))}
            </ul>
          </div>
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
