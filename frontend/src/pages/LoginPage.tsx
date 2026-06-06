import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import '../styles/auth.css';

function LoginPage() {
  const navigate = useNavigate();
  const { setIsAuthenticated, setUser } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/api/auth/login', { email, password });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      const userResponse = await api.get('/api/auth/me');
      setUser(userResponse.data);
      setIsAuthenticated(true);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">🪺</div>
          <div className="auth-logo-text">Agent<span>Nest</span></div>
        </div>
        <h2>Welcome back</h2>
        <p className="auth-subtitle">Sign in to your agent control center</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email" type="email" value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com" required disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password" type="password" value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••" required disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Authenticating...' : '→ Sign In'}
          </button>
        </form>

        <p className="auth-link">
          No account? <Link to="/signup">Create one</Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;