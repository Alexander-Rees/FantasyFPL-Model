import React from 'react';
import { useDispatch } from 'react-redux';
import { logoutUser } from '../actions/authActions';

const Dashboard = () => {
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(logoutUser());
  };

  return (
    <div>
      <h2>Welcome to your Dashboard!</h2>
      {/* Add dashboard content here */}
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default Dashboard;
