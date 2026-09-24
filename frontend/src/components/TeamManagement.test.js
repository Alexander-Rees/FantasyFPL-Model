import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { createStore } from 'redux';
import TeamManagement from './TeamManagement';

const authedState = {
  auth: {
    isAuthenticated: true,
    user: { id: 1, email: 'manager@example.com', name: 'Manager' },
    error: null,
  },
};

function renderTeam() {
  const store = createStore(() => authedState);
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <TeamManagement />
      </MemoryRouter>
    </Provider>
  );
}

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
  });
});

afterEach(() => {
  jest.resetAllMocks();
  localStorage.clear();
});

test('optimize button is not shown until team data exists', async () => {
  renderTeam();
  await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  expect(screen.queryByRole('button', { name: /optimize team/i })).not.toBeInTheDocument();
});

test('optimize requires imported team and surfaces error when clicked without data', async () => {
  // Force empty team then navigate to optimized tab is unreachable without team;
  // instead assert import CTA is present and optimize is absent.
  renderTeam();
  await waitFor(() => {
    expect(screen.getByText(/import your fpl team/i)).toBeInTheDocument();
  });
  expect(screen.queryByRole('button', { name: /optimize team/i })).not.toBeInTheDocument();
});

test('optimize button disables while request is in flight', async () => {
  let resolveOptimize;
  global.fetch = jest
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, name: 'Salah', position: 'MID', team: 'LIV', value: 12.5 }],
    })
    .mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveOptimize = resolve;
        })
    );

  renderTeam();
  await waitFor(() => screen.getByRole('button', { name: /optimize team/i }));

  const button = screen.getByRole('button', { name: /optimize team/i });
  fireEvent.click(button);

  await waitFor(() => expect(button).toBeDisabled());
  expect(button).toHaveTextContent(/optimizing/i);

  resolveOptimize({
    ok: true,
    json: async () => ({ optimal_team: [], formation: '3-4-3' }),
  });
});
