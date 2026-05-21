import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/agent-card.css';

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

interface Stats {
  cpu_percent: number;
  memory_usage_mb: number;
  memory_limit_mb: number;
  memory_percent: number;
  uptime_seconds: number;
}

interface Props {
  agent: Agent;
  onRefresh: () => void;
}

function AgentCard({ agent, onRefresh }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    if (agent.status === 'running') {
      fetchStats();
      const interval = setInterval(fetchStats, 5000);
      return () => clearInterval(interval);
    }
  }, [agent.status]);

  const fetchStats = async () => {
    try {
      const response = await api.get(`/api/agents/${agent.id}/stats`);
      setStats(response.data.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await api.get(`/api/agents/${agent.id}/logs`);
      setLogs(response.data.logs);
      setShowLogs(true);
    } catch (error) {
      setError('Failed to fetch logs');
    }
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await api.post(`/api/agents/${agent.id}/start`);
      onRefresh();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to start agent');
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await api.post(`/api/agents/${agent.id}/stop`);
      onRefresh();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to stop agent');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      setLoading(true);
      try {
        await api.delete(`/api/agents/${agent.id}`);
        onRefresh();
      } catch (error: any) {
        setError(error.response?.data?.detail || 'Failed to delete agent');
      } finally {
        setLoading(false);
      }
    }
  };

  const getStatusBadge = () => {
    const statusColors: { [key: string]: string } = {
      running: 'success',
      stopped: 'warning',
      deploying: 'info',
      crashed: 'danger',
    };
    return <span className={`badge badge-${statusColors[agent.status] || 'secondary'}`}>{agent.status}</span>;
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="agent-card">
      <div className="card-header">
        <div>
          <h3>{agent.name}</h3>
          <p>{agent.description}</p>
        </div>
        {getStatusBadge()}
      </div>

      <div className="card-details">
        <div className="detail-item">
          <span className="label">Image:</span>
          <span className="value">{agent.docker_image}</span>
        </div>
        <div className="detail-item">
          <span className="label">Resources:</span>
          <span className="value">{agent.cpu_limit} CPU / {agent.memory_limit_mb}MB</span>
        </div>
        {stats && agent.status === 'running' && (
          <>
            <div className="detail-item">
              <span className="label">CPU:</span>
              <span className="value">{stats.cpu_percent}%</span>
            </div>
            <div className="detail-item">
              <span className="label">Memory:</span>
              <span className="value">{stats.memory_usage_mb}MB / {stats.memory_limit_mb}MB ({stats.memory_percent}%)</span>
            </div>
            <div className="detail-item">
              <span className="label">Uptime:</span>
              <span className="value">{formatUptime(stats.uptime_seconds)}</span>
            </div>
          </>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="card-actions">
        {agent.status === 'running' ? (
          <button onClick={handleStop} disabled={loading} className="btn btn-warning">
            ⏹️ Stop
          </button>
        ) : (
          <button onClick={handleStart} disabled={loading} className="btn btn-success">
            ▶️ Start
          </button>
        )}
        <button onClick={fetchLogs} disabled={loading} className="btn btn-info">
          📋 Logs
        </button>
        <button onClick={handleDelete} disabled={loading} className="btn btn-danger">
          🗑️ Delete
        </button>
      </div>

      {showLogs && (
        <div className="logs-modal">
          <div className="logs-content">
            <div className="logs-header">
              <h4>Agent Logs</h4>
              <button onClick={() => setShowLogs(false)}>✕</button>
            </div>
            <div className="logs-body">
              {logs.length === 0 ? (
                <p>No logs available</p>
              ) : (
                logs.map((log, index) => <div key={index} className="log-line">{log}</div>)
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentCard;
