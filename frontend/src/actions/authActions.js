import axios from 'axios';
import { registerSuccess, registerFail, loginSuccess, loginFail, logout } from '../reducers/authReducer';

axios.defaults.baseURL = 'http://localhost:8081';

export const registerUser = (userData) => async (dispatch) => {
  try {
    const res = await axios.post('/api/users/register', userData);
    dispatch(registerSuccess(res.data));
    window.location.href = '/login'; // Redirect to login after registration
  } catch (err) {
    dispatch(registerFail(err.response ? err.response.data : "Server error"));
  }
};

export const loginUser = (userData) => async (dispatch) => {
  try {
    const res = await axios.post('/api/users/login', userData);
    localStorage.setItem('token', res.data.token); // Store token in localStorage
    dispatch(loginSuccess(res.data));
    window.location.href = '/dashboard'; // Redirect to dashboard after login
  } catch (err) {
    dispatch(loginFail(err.response ? err.response.data : "Server error"));
  }
};

export const logoutUser = () => (dispatch) => {
  dispatch(logout());
  window.location.href = '/login';
};
