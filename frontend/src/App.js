// src/App.js
import React, { useEffect } from 'react';
import { Provider, useDispatch } from 'react-redux';
import store from './store';
import AppRoutes from './routes/Routes';
import { loadUser } from './actions/authActions';

const AppContent = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    // Load user data when app starts
    dispatch(loadUser());
  }, [dispatch]);

  return <AppRoutes />;
};

const App = () => (
  <Provider store={store}>
    <AppContent />
  </Provider>
);

export default App;
