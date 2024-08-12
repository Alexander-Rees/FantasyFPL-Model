import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { registerUser } from '../actions/authActions';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const dispatch = useDispatch();
  const { name, email, password } = formData;

  const error = useSelector(state => state.auth.error); // Get the error from the state

  const onChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(registerUser({ name, email, password }));
  };

  return (
    <form onSubmit={onSubmit}>
      <input type="text" name="name" value={name} onChange={onChange} required />
      <input type="email" name="email" value={email} onChange={onChange} required />
      <input type="password" name="password" value={password} onChange={onChange} required />
      <button type="submit">Register</button>
      {error && <p style={{ color: 'red' }}>{error}</p>} {/* Display error message */}
    </form>
  );
};

export default Register;
