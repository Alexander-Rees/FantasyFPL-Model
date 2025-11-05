import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from '../components/Login';
import Register from '../components/Register';
import Dashboard from '../components/Dashboard';
import TeamManagement from '../components/TeamManagement'; // Import the TeamManagement component
import PrivateRoute from '../components/PrivateRoutes';

const AppRoutes = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected Routes */}
      <Route element={<PrivateRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/team" element={<TeamManagement />} />
      </Route>

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  </Router>
);

export default AppRoutes;
