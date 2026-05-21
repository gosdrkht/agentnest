import React, { useState } from 'react';
import AgentCard from './AgentCard';
import '../styles/agent-list.css';

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

interface Props {
  agents: Agent[];
  onRefresh: () => void;
}

function AgentList({ agents, onRefresh }: Props) {
  return (
    <div className="agent-list">
      {agents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} onRefresh={onRefresh} />
      ))}
    </div>
  );
}

export default AgentList;
