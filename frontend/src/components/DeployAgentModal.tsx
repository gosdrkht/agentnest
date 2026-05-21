import React, { useState } from 'react';
import api from '../services/api';
import '../styles/modal.css';

interface Props {
  onClose: () => void;
  onSuccess: () => void;
}

function DeployAgentModal({ onClose, onSuccess }: Props) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [dockerImage, setDockerImage] = useState('');
  const [cpuLimit, setCpuLimit] = useState('1.0');
  const [memoryLimit, setMemoryLimit] = useState('512');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.post('/api/agents', {
        name,
        description,
        docker_image: dockerImage,
        cpu_limit: parseFloat(cpuLimit),
        memory_limit_mb: parseInt(memoryLimit),
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to deploy agent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Deploy New Agent</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name">Agent Name *</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., My AI Bot"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Agent description"
              disabled={loading}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="dockerImage">Docker Image *</label>
            <input
              id="dockerImage"
              type="text"
              value={dockerImage}
              onChange={(e) => setDockerImage(e.target.value)}
              placeholder="e.g., ubuntu:latest"
              required
              disabled={loading}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cpuLimit">CPU Cores</label>
              <input
                id="cpuLimit"
                type="number"
                value={cpuLimit}
                onChange={(e) => setCpuLimit(e.target.value)}
                min="0.1"
                max="4"
                step="0.1"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="memoryLimit">Memory (MB)</label>
              <input
                id="memoryLimit"
                type="number"
                value={memoryLimit}
                onChange={(e) => setMemoryLimit(e.target.value)}
                min="128"
                max="4096"
                step="128"
                disabled={loading}
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={loading} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Deploying...' : 'Deploy Agent'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DeployAgentModal;
