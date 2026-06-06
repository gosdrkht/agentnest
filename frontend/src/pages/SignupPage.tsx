import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import '../styles/auth.css';

function SignupPage() {
  const navigate = useNavigate();
  const { setIsAuthenticated, setUser } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/api/auth/signup', { email, username, password });
      const loginResponse = await api.post('/api/auth/login', { email, password });
      const { access_token } = loginResponse.data;
      localStorage.setItem('token', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      const userResponse = await api.get('/api/auth/me');
      setUser(userResponse.data);
      setIsAuthenticated(true);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed.');
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
        <h2>Create account</h2>
        <p className="auth-subtitle">Start hosting your AI agents in seconds</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username" type="text" value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="agentmaster" required disabled={loading}
            />
          </div>
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
            {loading ? 'Creating account...' : '→ Get Started'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default SignupPage;