import React from 'react';
import { Shield, RefreshCw, RotateCcw, Users, BarChart3, Database } from 'lucide-react';

export default function Navbar({
  isLoading,
  onRecalculate,
  onReset,
  onOpenAgents,
  onOpenMetrics,
  agentCount = 40
}) {
  return (
    <header className="navbar">
      <div className="brand-section">
        <div className="brand-logo">🛡️</div>
        <div>
          <h1 className="brand-title">salesIntelAi</h1>
          <p className="brand-subtitle">Dynamic 5-Stage Customer Classification & Intelligent Agent Routing</p>
        </div>
      </div>

      <div className="nav-actions">
        <div className="status-pill">
          <span className="pulse-dot"></span>
          <span>LIVE AI SIMULATOR</span>
        </div>

        <button
          className="btn btn-secondary"
          onClick={onOpenAgents}
          title="View all synthetic agents in database"
        >
          <Users size={15} />
          <span>Agents ({agentCount})</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={onOpenMetrics}
          title="View ML evaluation metrics and dataset statistics"
        >
          <BarChart3 size={15} />
          <span>ML Metrics & Data</span>
        </button>

        <button
          className="btn btn-reset"
          onClick={onReset}
          title="Reset to default initial customer state"
        >
          <RotateCcw size={15} />
          <span>Reset</span>
        </button>

        <button
          className="btn btn-primary"
          onClick={onRecalculate}
          disabled={isLoading}
          title="Manual recalculation fallback"
        >
          {isLoading ? (
            <div className="spinner"></div>
          ) : (
            <RefreshCw size={15} />
          )}
          <span>{isLoading ? 'Calculating...' : 'Recalculate'}</span>
        </button>
      </div>
    </header>
  );
}

