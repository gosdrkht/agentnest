import nodemailer from 'nodemailer';
import { render } from '@react-email/render';

// Email templates
const templates = {
  welcome: (userName: string) => `
    <h1>Welcome to AgentNest, ${userName}! 🚀</h1>
    <p>Your account is ready to deploy AI agents.</p>
    <p>Get started:</p>
    <ol>
      <li>Login to your dashboard</li>
      <li>Click "Deploy New Agent"</li>
      <li>Choose your Docker image</li>
      <li>Set resource limits</li>
      <li>Start monitoring!</li>
    </ol>
    <p><a href="https://agentnest.io/dashboard">Go to Dashboard →</a></p>
  `,

  agentDeployed: (agentName: string) => `
    <h2>🎉 Agent Deployed: ${agentName}</h2>
    <p>Your agent is now running and monitoring.</p>
    <p>Resource Allocation:</p>
    <ul>
      <li>CPU: 1.0 core</li>
      <li>Memory: 512 MB</li>
      <li>Status: Running ✅</li>
    </ul>
    <p><a href="https://agentnest.io/dashboard">View Agent Stats →</a></p>
  `,

  agentCrashed: (agentName: string) => `
    <h2>⚠️ Agent Crashed: ${agentName}</h2>
    <p>Your agent stopped unexpectedly. Here's what we're doing:</p>
    <ul>
      <li>✓ Attempting automatic restart...</li>
      <li>✓ Checking system resources</li>
      <li>✓ Reviewing error logs</li>
    </ul>
    <p><a href="https://agentnest.io/dashboard">View Logs →</a></p>
  `,

  billingAlert: (balance: number, monthlyUsage: number) => `
    <h2>💳 Billing Alert</h2>
    <p>Your account balance is running low.</p>
    <table style="border-collapse: collapse; width: 100%;">
      <tr>
        <td>Current Balance:</td>
        <td><strong>$${balance.toFixed(2)}</strong></td>
      </tr>
      <tr>
        <td>Monthly Usage:</td>
        <td><strong>$${monthlyUsage.toFixed(2)}</strong></td>
      </tr>
    </table>
    <p><a href="https://agentnest.io/billing">Add Payment Method →</a></p>
  `,

  monthlyInvoice: (totalCost: number, agentsRun: number, uptime: string) => `
    <h2>📋 Monthly Invoice</h2>
    <p>Here's a summary of your AgentNest usage for this month:</p>
    <table style="border-collapse: collapse; width: 100%;">
      <tr>
        <td>Total Cost:</td>
        <td><strong>$${totalCost.toFixed(2)}</strong></td>
      </tr>
      <tr>
        <td>Agents Deployed:</td>
        <td><strong>${agentsRun}</strong></td>
      </tr>
      <tr>
        <td>Total Uptime:</td>
        <td><strong>${uptime}</strong></td>
      </tr>
    </table>
    <p><a href="https://agentnest.io/billing">View Invoice →</a></p>
  `,
};

// Transporter
const transporter = nodemailer.createTransport({
  service: process.env.EMAIL_SERVICE || 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASSWORD,
  },
});

export const emailService = {
  async sendWelcome(email: string, name: string) {
    return transporter.sendMail({
      from: process.env.EMAIL_FROM || 'noreply@agentnest.io',
      to: email,
      subject: '🚀 Welcome to AgentNest!',
      html: templates.welcome(name),
    });
  },

  async sendAgentDeployed(email: string, agentName: string) {
    return transporter.sendMail({
      from: process.env.EMAIL_FROM || 'noreply@agentnest.io',
      to: email,
      subject: `✅ Agent Deployed: ${agentName}`,
      html: templates.agentDeployed(agentName),
    });
  },

  async sendAgentCrashed(email: string, agentName: string) {
    return transporter.sendMail({
      from: process.env.EMAIL_FROM || 'noreply@agentnest.io',
      to: email,
      subject: `⚠️ Alert: Agent Crashed - ${agentName}`,
      html: templates.agentCrashed(agentName),
    });
  },

  async sendBillingAlert(email: string, balance: number, monthlyUsage: number) {
    return transporter.sendMail({
      from: process.env.EMAIL_FROM || 'noreply@agentnest.io',
      to: email,
      subject: '💳 Billing Alert - Low Balance',
      html: templates.billingAlert(balance, monthlyUsage),
    });
  },

  async sendMonthlyInvoice(email: string, totalCost: number, agentsRun: number, uptime: string) {
    return transporter.sendMail({
      from: process.env.EMAIL_FROM || 'noreply@agentnest.io',
      to: email,
      subject: '📋 Your AgentNest Monthly Invoice',
      html: templates.monthlyInvoice(totalCost, agentsRun, uptime),
    });
  },
};
