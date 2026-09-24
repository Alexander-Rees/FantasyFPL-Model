import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import Login from './Login';
import rootReducer from '../reducers';

function renderLogin() {
  const store = configureStore({ reducer: rootReducer });
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    </Provider>
  );
}

test('shows validation errors for empty login submit', () => {
  renderLogin();

  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  expect(screen.getByText(/password is required/i)).toBeInTheDocument();
});

test('shows validation error for invalid email', () => {
  renderLogin();

  fireEvent.change(screen.getByLabelText(/email address/i), {
    target: { name: 'email', value: 'not-an-email' },
  });
  fireEvent.change(screen.getByLabelText(/^password$/i), {
    target: { name: 'password', value: 'secret' },
  });
  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

  expect(screen.getByText(/valid email address/i)).toBeInTheDocument();
});
