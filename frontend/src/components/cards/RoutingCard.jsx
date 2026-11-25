import React from 'react';
import { UserCheck, ShieldAlert, Award, Star, Globe, CheckCircle, Clock } from 'lucide-react';

export default function RoutingCard({ data }) {
  if (!data) return null;

  const {
    required_agent_level,
    routing_strategy,
    escalation_triggered,
    escalation_reason,
    assigned_agent = {},
    assignment_summary
  } = data;

  const tierBadgeClass = {
    'Intern Agent': 'badge-green',
    'Expert Agent': 'badge-blue',
    'Senior Expert Agent': 'badge-purple'
  }[required_agent_level] || 'badge-blue';

  const strategyColor = {
    'Intern Agent': { bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399', border: '#059669' },
    'Expert Agent': { bg: 'rgba(59, 130, 246, 0.15)', text: '#60a5fa', border: '#2563eb' },
    'Senior Expert Agent': { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: '#9333ea' }
  }[required_agent_level] || { bg: 'rgba(59, 130, 246, 0.15)', text: '#60a5fa', border: '#2563eb' };

  const isOnline = Boolean(assigned_agent.is_online);
  const status = assigned_agent.availability_status || 'Offline';
  const currWl = assigned_agent.current_workload || 0;
  const maxWl = assigned_agent.max_workload || 5;
  const wlPercent = Math.min(Math.round((currWl / maxWl) * 100), 100);

  return (
    <div className="output-card full-width" style={{ border: '1px solid rgba(59, 130, 246, 0.4)' }}>
      <div className="card-header">
        <div className="card-title-group">
          <span className="card-icon">🚀</span>
          <div>
            <h2 className="card-title">5. Final Routing & Intelligent Agent Allocation</h2>
            <span style={{ fontSize: '0.74rem', color: '#9ca3af' }}>
              Real-world operational tier: Intern (Direct Buyers) • Expert (High Interest) • Senior (Complex & Escalations)
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          {routing_strategy && (
            <span
              style={{
                fontSize: '0.74rem',
                fontWeight: 600,
                padding: '0.25rem 0.65rem',
                borderRadius: '6px',
                background: strategyColor.bg,
                color: strategyColor.text,
                border: `1px solid ${strategyColor.border}`
              }}
            >
              {routing_strategy}
            </span>
          )}
          {escalation_triggered && (
            <span className="card-badge badge-red" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
              <ShieldAlert size={12} />
              <span>Escalated</span>
            </span>
          )}
          <span className={`card-badge ${tierBadgeClass}`} style={{ fontSize: '0.85rem', padding: '0.35rem 0.85rem' }}>
            {required_agent_level}
          </span>
        </div>
      </div>

      {/* Assigned Agent Box */}
      <div className="assigned-agent-box">
        <div className="agent-profile-header">
          <div className="agent-name-id">
            <span className="agent-name">{assigned_agent.agent_name || 'Agent Assigning...'}</span>
            <span className="agent-id">
              ID: {assigned_agent.agent_id} • Level: {assigned_agent.agent_level}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              style={{
                fontSize: '0.72rem',
                padding: '0.2rem 0.55rem',
                borderRadius: '9999px',
                fontWeight: 600,
                background: isOnline ? 'rgba(16, 185, 129, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                color: isOnline ? '#34d399' : '#9ca3af',
                border: `1px solid ${isOnline ? '#059669' : '#4b5563'}`
              }}
            >
              {isOnline ? 'Online' : 'Offline'} ({status})
            </span>
          </div>
        </div>

        {/* Tags */}
        <div className="agent-tags">
          <span className="agent-tag-pill" style={{ color: '#93c5fd', borderColor: '#2563eb' }}>
            Domain: {Array.isArray(assigned_agent.specializations) ? assigned_agent.specializations.join(', ') : assigned_agent.specializations}
          </span>
          <span className="agent-tag-pill" style={{ color: '#a78bfa', borderColor: '#7c3aed' }}>
            Languages: {Array.isArray(assigned_agent.supported_languages) ? assigned_agent.supported_languages.join(', ') : assigned_agent.supported_languages}
          </span>
          <span className="agent-tag-pill">
            Rating: ★ {assigned_agent.performance_rating || '4.8'}
          </span>
        </div>

        {/* Agent Stats Grid */}
        <div className="agent-stats-grid">
          <div className="agent-stat-item">
            <span className="stat-label">Experience</span>
            <span className="stat-value">{assigned_agent.experience_years} Years</span>
          </div>
          <div className="agent-stat-item">
            <span className="stat-label">Current Workload</span>
            <span className="stat-value">{currWl} / {maxWl} Cases</span>
          </div>
          <div className="agent-stat-item">
            <span className="stat-label">Assigned Total</span>
            <span className="stat-value">{assigned_agent.assigned_customer_count || 45}</span>
          </div>
          <div className="agent-stat-item">
            <span className="stat-label">Match Score</span>
            <span className="stat-value" style={{ color: '#38bdf8' }}>{assigned_agent.match_score || 1200} pts</span>
          </div>
        </div>

        {/* Workload Bar */}
        <div style={{ marginTop: '0.65rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#9ca3af', marginBottom: '2px' }}>
            <span>Workload Capacity Utilization</span>
            <span>{wlPercent}%</span>
          </div>
          <div className="score-bar-bg" style={{ height: '5px', margin: 0 }}>
            <div
              className="score-bar-fill"
              style={{
                width: `${wlPercent}%`,
                backgroundColor: wlPercent > 80 ? '#ef4444' : wlPercent > 50 ? '#f59e0b' : '#10b981'
              }}
            ></div>
          </div>
        </div>
      </div>

      <div className="card-explanation">
        <p style={{ marginBottom: '0.35rem' }}>
          <strong>Policy Reasoning:</strong> {assignment_summary}
        </p>
        {assigned_agent.reason && (
          <p style={{ color: '#cbd5e1', fontSize: '0.78rem' }}>
            <strong>Match Notes:</strong> {assigned_agent.reason}
          </p>
        )}
      </div>

      {/* 3-Tier Real-World Allocation Architecture Explainer */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '0.5rem',
          marginTop: '0.65rem',
          padding: '0.6rem 0.8rem',
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid rgba(51, 65, 85, 0.5)',
          borderRadius: '8px',
          fontSize: '0.72rem'
        }}
      >
        <div style={{ opacity: required_agent_level === 'Intern Agent' ? 1 : 0.55, borderLeft: '3px solid #10b981', paddingLeft: '0.45rem' }}>
          <strong style={{ color: '#34d399' }}>✓ Intern Agent (Direct Buyer):</strong>
          <div style={{ color: '#94a3b8', fontSize: '0.68rem', marginTop: '2px' }}>
            Fully willing to buy + up to 2 domains (e.g. Health & Life bundle). Fast transactional fulfillment.
          </div>
        </div>

        <div style={{ opacity: required_agent_level === 'Expert Agent' ? 1 : 0.55, borderLeft: '3px solid #3b82f6', paddingLeft: '0.45rem' }}>
          <strong style={{ color: '#60a5fa' }}>⚡ Expert Agent (High Interest):</strong>
          <div style={{ color: '#94a3b8', fontSize: '0.68rem', marginTop: '2px' }}>
            Broad multi-domain interest (3+ domains or hesitation), comparisons, inquiries, or objections.
          </div>
        </div>

        <div style={{ opacity: required_agent_level === 'Senior Expert Agent' ? 1 : 0.55, borderLeft: '3px solid #a855f7', paddingLeft: '0.45rem' }}>
          <strong style={{ color: '#c084fc' }}>★ Senior Expert (Hard Complex):</strong>
          <div style={{ color: '#94a3b8', fontSize: '0.68rem', marginTop: '2px' }}>
            High complexity, previous failure recovery, or complex multi-line underwriting.
          </div>
        </div>
      </div>
    </div>
  );
}

