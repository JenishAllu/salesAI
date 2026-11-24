import React from 'react';
import { UserCheck, ShieldAlert, Award, Star, Globe, CheckCircle, Clock } from 'lucide-react';

export default function RoutingCard({ data }) {
  if (!data) return null;

  const {
    required_agent_level,
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
              Multi-factor policy matrix + eligibility matching
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
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
    </div>
  );
}

