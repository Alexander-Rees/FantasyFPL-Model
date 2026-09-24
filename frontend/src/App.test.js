import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app shell with dashboard brand content', () => {
  render(<App />);
  expect(
    screen.getByRole('heading', { level: 1, name: 'FPL AI Optimizer' })
  ).toBeInTheDocument();
});
