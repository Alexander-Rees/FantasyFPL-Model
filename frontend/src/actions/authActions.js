import axios from 'axios';
import { registerSuccess, registerFail, loginSuccess, loginFail, logout } from '../reducers/authReducer';

axios.defaults.baseURL = 'http://localhost:8081';

export const registerUser = (userData) => async (dispatch) => {
  try {
    const res = await axios.post('/api/v1/auth/register', userData);
    dispatch(registerSuccess(res.data));
    window.location.href = '/login'; // Redirect to login after registration
  } catch (err) {
    dispatch(registerFail(err.response ? err.response.data : "Server error"));
  }
};

export const loginUser = (userData) => async (dispatch) => {
  try {
    const res = await axios.post('/api/v1/auth/login', userData);
    localStorage.setItem('token', res.data.token); // Store token in localStorage
    
    // Set the token in axios headers for future requests
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.token}`;
    
    // The backend returns: { id, name, email, token }
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
      
      // Decode the JWT token to get user info
      // Backend JWT has: sub (email), userId (claim)
      const payload = JSON.parse(atob(token.split('.')[1]));
      
      // Check if token is expired
      const expirationTime = payload.exp * 1000; // Convert to milliseconds
      if (Date.now() > expirationTime) {
        // Token is expired, clear it
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        dispatch(logout());
        return;
      }
      
      const userData = {
        id: payload.userId,  // Backend uses 'userId' claim
        email: payload.sub,  // Backend uses 'sub' for email
        name: payload.name || 'User', // Name might not be in token, use default
        token: token
      };
      
      // Try to verify user exists by making a lightweight API call
      // If it fails, the user doesn't exist and we should clear the token
      try {
        await axios.get('/api/v1/auth'); // This will fail if user doesn't exist or token is invalid
        dispatch(loginSuccess(userData));
      } catch (verifyErr) {
        // User doesn't exist or token is invalid, clear it
        console.log('User verification failed, clearing token:', verifyErr);
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        dispatch(logout());
      }
    } catch (err) {
      // If token is invalid or can't be decoded, remove it
      console.log('Token decode failed, clearing token:', err);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      dispatch(logout());
    }
  }
};