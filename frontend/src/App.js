// src/App.js
import React from 'react';
import { Provider } from 'react-redux';
import store from './store';
import AppRoutes from './routes/Routes';

const App = () => (
  <Provider store={store}>
    <AppRoutes />
  </Provider>
);

export default App;
