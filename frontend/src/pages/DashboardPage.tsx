import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import AgentList from '../components/AgentList';
import DeployAgentModal from '../components/DeployAgentModal';
import '../styles/dashboard.css';

interface Agent {
  id: number;
  name: string;
  description: string;
  docker_image: string;
  status: string;
  container_id: string;
  cpu_limit: number;
  memory_limit_mb: number;
  created_at: string;
}

function DashboardPage() {
  const navigate = useNavigate();
  const { user, setIsAuthenticated } = useContext(AuthContext);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchAgents();
    // Refresh agents every 10 seconds
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

  const handleAgentDeployed = () => {
    setShowModal(false);
    fetchAgents();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🚀 AgentNest Dashboard</h1>
        </div>
        <div className="header-right">
          <div className="user-info">
            <span>{user?.email}</span>
            <span className="balance">💰 ${user?.balance.toFixed(2)}</span>
          </div>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-controls">
          <h2>Your Agents</h2>
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            ➕ Deploy New Agent
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading agents...</div>
        ) : agents.length === 0 ? (
          <div className="empty-state">
            <p>No agents deployed yet</p>
            <p>Click "Deploy New Agent" to get started</p>
          </div>
        ) : (
          <AgentList agents={agents} onRefresh={fetchAgents} />
        )}
      </main>

      {showModal && (
        <DeployAgentModal onClose={() => setShowModal(false)} onSuccess={handleAgentDeployed} />
      )}
    </div>
  );
}

export default DashboardPage;
