import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser } from '../actions/authActions';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const dispatch = useDispatch();
  const { email, password } = formData;

  const error = useSelector(state => state.auth.error); // Get the error from the state

  const onChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(loginUser({ email, password }));
  };

  return (
    <form onSubmit={onSubmit}>
      <input type="email" name="email" value={email} onChange={onChange} required />
      <input type="password" name="password" value={password} onChange={onChange} required />
      <button type="submit">Login</button>
      {error && <p style={{ color: 'red' }}>{error}</p>} {/* Display error message */}
    </form>
  );
};

export default Login;
