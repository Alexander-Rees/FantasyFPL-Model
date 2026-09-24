import authReducer, {
  loginSuccess,
  loginFail,
  logout,
  registerSuccess,
} from '../reducers/authReducer';

describe('authReducer', () => {
  const baseState = {
    isAuthenticated: false,
    user: null,
    error: null,
  };

  beforeEach(() => {
    localStorage.clear();
  });

  test('loginSuccess sets authenticated user and stores token', () => {
    const payload = { id: 1, email: 'a@b.com', token: 'jwt-token' };
    const next = authReducer(baseState, loginSuccess(payload));
    expect(next.isAuthenticated).toBe(true);
    expect(next.user).toEqual(payload);
    expect(next.error).toBeNull();
    expect(localStorage.getItem('token')).toBe('jwt-token');
  });

  test('registerSuccess mirrors login success', () => {
    const payload = { id: 2, email: 'b@c.com', token: 'reg-token' };
    const next = authReducer(baseState, registerSuccess(payload));
    expect(next.isAuthenticated).toBe(true);
    expect(localStorage.getItem('token')).toBe('reg-token');
  });

  test('loginFail stores error without authenticating', () => {
    const next = authReducer(baseState, loginFail('bad credentials'));
    expect(next.isAuthenticated).toBe(false);
    expect(next.error).toBe('bad credentials');
  });

  test('logout clears auth state and token', () => {
    localStorage.setItem('token', 'jwt-token');
    const authed = {
      isAuthenticated: true,
      user: { id: 1 },
      error: null,
    };
    const next = authReducer(authed, logout());
    expect(next.isAuthenticated).toBe(false);
    expect(next.user).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});
