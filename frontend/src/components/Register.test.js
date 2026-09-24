import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import Register from './Register';
import rootReducer from '../reducers';

function renderRegister() {
  const store = configureStore({ reducer: rootReducer });
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    </Provider>
  );
}

test('shows validation errors for empty register submit', () => {
  renderRegister();

  fireEvent.click(screen.getByRole('button', { name: /create account/i }));

  expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
});

test('rejects mismatched passwords', () => {
  renderRegister();

  fireEvent.change(screen.getByLabelText(/full name/i), {
    target: { name: 'name', value: 'Alex Manager' },
  });
  fireEvent.change(screen.getByLabelText(/email address/i), {
    target: { name: 'email', value: 'alex@example.com' },
  });
  fireEvent.change(screen.getByLabelText(/^password$/i), {
    target: { name: 'password', value: 'Password1' },
  });
  fireEvent.change(screen.getByLabelText(/confirm password/i), {
    target: { name: 'confirmPassword', value: 'Password2' },
  });
  fireEvent.click(screen.getByRole('button', { name: /create account/i }));

  expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
});
