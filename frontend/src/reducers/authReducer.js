// Define action types
const REGISTER_SUCCESS = 'REGISTER_SUCCESS';
const REGISTER_FAIL = 'REGISTER_FAIL';
const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
const LOGIN_FAIL = 'LOGIN_FAIL';
const LOGOUT = 'LOGOUT';

// Initial state
const initialState = {
  isAuthenticated: !!localStorage.getItem('token'), // Check if token exists in localStorage
  user: null,
  error: null,
};

// Reducer function
const authReducer = (state = initialState, action) => {
  switch (action.type) {
    case REGISTER_SUCCESS:
    case LOGIN_SUCCESS:
      localStorage.setItem('token', action.payload.token); // Store token in localStorage
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload,
        error: null,
      };
    case REGISTER_FAIL:
    case LOGIN_FAIL:
      return {
        ...state,
        error: action.payload,
      };
    case LOGOUT:
      localStorage.removeItem('token'); // Remove token from localStorage
      return {
        ...state,
        isAuthenticated: false,
        user: null,
      };
    default:
      return state;
  }
};

// Action creators
export const registerSuccess = (data) => ({
  type: REGISTER_SUCCESS,
  payload: data,
});

export const registerFail = (error) => ({
  type: REGISTER_FAIL,
  payload: error,
});

export const loginSuccess = (data) => ({
  type: LOGIN_SUCCESS,
  payload: data,
});

export const loginFail = (error) => ({
  type: LOGIN_FAIL,
  payload: error,
});

export const logout = () => ({
  type: LOGOUT,
});

export default authReducer;
