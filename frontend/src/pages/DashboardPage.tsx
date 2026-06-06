import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import AgentList from '../components/AgentList';
import DeployAgentModal from '../components/DeployAgentModal';
import '../styles/dashboard.css';

interface Agent {
  id: number; name: string; description: string;
  docker_image: string; status: string; container_id: string;
  cpu_limit: number; memory_limit_mb: number; created_at: string;
}

function DashboardPage() {
  const navigate = useNavigate();
  const { user, setIsAuthenticated } = useContext(AuthContext);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await api.get('/api/agents');
      setAgents(response.data);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  const running = agents.filter(a => a.status === 'running').length;
  const stopped = agents.filter(a => a.status === 'stopped').length;
  const crashed = agents.filter(a => a.status === 'crashed').length;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-logo">
          <div className="header-logo-icon">🪺</div>
          <div className="header-logo-text">Agent<span>Nest</span></div>
        </div>
        <div className="header-right">
          <div className="user-chip">
            <span className="user-email">{user?.email}</span>
            <span className="user-balance">${Number(user?.balance || 0).toFixed(2)}</span>
          </div>
          <button onClick={handleLogout} className="btn btn-secondary">Logout</button>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-label">Total Agents</div>
            <div className="stat-value">{agents.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Running</div>
            <div className={`stat-value ${running > 0 ? 'green' : ''}`}>{running}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Stopped</div>
            <div className={`stat-value ${stopped > 0 ? 'yellow' : ''}`}>{stopped}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Crashed</div>
            <div className={`stat-value ${crashed > 0 ? 'red' : ''}`}>{crashed}</div>
          </div>
        </div>

        <div className="section-header">
          <div className="section-title">Your Agents</div>
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            + Deploy Agent
          </button>
        </div>

        {loading ? (
          <div style={{ color: 'var(--text2)', padding: '40px', textAlign: 'center', fontSize: '13px' }}>
            Loading agents...
          </div>
        ) : agents.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🤖</div>
            <p>No agents deployed yet</p>
            <p>Deploy your first AI agent to get started</p>
            <button onClick={() => setShowModal(true)} className="btn btn-primary">
              + Deploy First Agent
            </button>
          </div>
        ) : (
          <AgentList agents={agents} onRefresh={fetchAgents} />
        )}
      </main>

      {showModal && (
        <DeployAgentModal
          onClose={() => setShowModal(false)}
          onSuccess={() => { setShowModal(false); fetchAgents(); }}
        />
      )}
    </div>
  );
}

export default DashboardPage;