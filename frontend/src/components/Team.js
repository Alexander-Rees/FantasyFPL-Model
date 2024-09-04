import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Team = () => {
  const [team, setTeam] = useState(null);
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [playerId, setPlayerId] = useState("");
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
        console.log("Players fetched:", response.data);
        setPlayers(response.data);
      })
      .catch((error) =>
        console.error(
          "Error fetching players:",
          error.response ? error.response.data : error.message
        )
      );
    const gameweek = 1;
    axios
      .get(`/api/players/weekly/${gameweek}`)
      .then((response) => {
        console.log("Weekly players fetched:", response.data);
        setPlayers(response.data);
      })
      .catch((error) =>
        console.error(
          "Error fetching weekly players:",
          error.response ? error.response.data : error.message
        )
      );

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
      .filter(
        (player) =>
          selectedPosition === "" ||
          player.position === parseInt(selectedPosition)
      )
      .sort((a, b) => (b[sortCriteria] || 0) - (a[sortCriteria] || 0));
    setFilteredPlayers(result);
  };

  const handleAddPlayer = () => {
    axios
      .post("/api/team?userId=1", { id: playerId })
      .then((response) => {
        setTeam(response.data);
        setMessage("Player added successfully!");
      })
      .catch((error) => setMessage("Error adding player to the team."));
  };

  const handleReturn = () => {
    navigate("/dashboard");
  };

  return (
    <div>
      <h2>Your Team</h2>
      {team ? (
        <div>
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

      <div>
        <h3>Sort and Filter Players</h3>
        <label>Filter by Position: </label>
        <select
          value={selectedPosition}
          onChange={(e) => {
            console.log("Position selected:", e.target.value);
            setSelectedPosition(e.target.value);
          }}
        >
          <option value="">All Positions</option>
          <option value="1">Goalkeeper</option>
          <option value="2">Defender</option>
          <option value="3">Midfielder</option>
          <option value="4">Forward</option>
        </select>

        <select
          value={sortCriteria}
          onChange={(e) => {
            console.log("Sort criteria selected:", e.target.value);
            setSortCriteria(e.target.value);
          }}
        >
          <option value="total_points">Total Points</option>
          <option value="value">Value</option>
          <option value="goals_scored">Goals Scored</option>
          <option value="assists">Assists</option>
        </select>

        {/* Button to trigger search */}
        <button onClick={handleSearch}>Search</button>

        <ul>
          {filteredPlayers.length > 0 ? (
            filteredPlayers.map((player) => (
              <li key={player.id}>
                {player.name} - ${player.value}M (Points: {player.total_points},
                Position: {player.position})
              </li>
            ))
          ) : (
            <p>No players found. Adjust the filters or click search again.</p>
          )}
        </ul>
      </div>

      <div>
        <h3>Optimal Team (From Flask API)</h3>
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

      <div>
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

      <button
        onClick={handleReturn}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        Return to Dashboard
      </button>
    </div>
  );
};

export default Team;
