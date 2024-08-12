import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from '../components/Home';
import Login from '../components/Login';
import Register from '../components/Register';
import Dashboard from '../components/Dashboard'; // Create a Dashboard component if not already done
import PrivateRoute from '../components/PrivateRoutes'; // Update the path if necessary

const AppRoutes = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<PrivateRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  </Router>
);

export default AppRoutes;
