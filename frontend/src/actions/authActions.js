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
    
    // Set the token in axios headers for future requests
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.token}`;
    
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

export const loadUser = () => async (dispatch) => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      // Set the token in axios headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // For now, we'll decode the token to get user info
      // In a real app, you'd make an API call to /api/users/me
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userData = {
        id: payload.userId,
        email: payload.sub,
        name: 'User', // We'll get this from the token or make an API call
        token: token
      };
      
      dispatch(loginSuccess(userData));
    } catch (err) {
      // If token is invalid, remove it
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      dispatch(logout());
    }
  }
};