import React from 'react';
import { Activity, Clock, Repeat } from 'lucide-react';

export default function EngagementCard({ data }) {
  if (!data) return null;

  const {
    engagement_score,
    engagement_level,
    most_engaged_category,
    relevant_visits,
    time_spent_seconds,
    reasoning,
    score_breakdown = {}
  } = data;

  const levelColor = {
    Low: '#9ca3af',
    Medium: '#3b82f6',
    High: '#10b981'
  }[engagement_level] || '#3b82f6';

  const badgeClass = {
    Low: 'badge-amber',
    Medium: 'badge-blue',
    High: 'badge-green'
  }[engagement_level] || 'badge-blue';

  return (
    <div className="output-card">
      <div className="card-header">
        <div className="card-title-group">
          <span className="card-icon">⚡</span>
          <h2 className="card-title">2. Customer Engagement</h2>
        </div>
        <span className={`card-badge ${badgeClass}`}>
          {engagement_level} Engagement
        </span>
      </div>

      <div className="score-container">
        <span className="score-number" style={{ color: levelColor }}>
          {engagement_score}
        </span>
        <span className="score-max">/ 100</span>
      </div>

      <div className="score-bar-bg">
        <div
          className="score-bar-fill"
          style={{ width: `${engagement_score}%`, backgroundColor: levelColor }}
        ></div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.75rem', fontSize: '0.76rem' }}>
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.4rem 0.6rem', borderRadius: '6px' }}>
          <span style={{ color: '#9ca3af', display: 'block', fontSize: '0.68rem' }}>Most Engaged Category</span>
          <span style={{ fontWeight: 600, color: '#f3f4f6' }}>{most_engaged_category}</span>
        </div>
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.4rem 0.6rem', borderRadius: '6px' }}>
          <span style={{ color: '#9ca3af', display: 'block', fontSize: '0.68rem' }}>Dwell Time & Visits</span>
          <span style={{ fontWeight: 600, color: '#f3f4f6' }}>{time_spent_seconds}s | {relevant_visits} visits</span>
        </div>
      </div>

      {/* Mini weights breakdown */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
        <span>Sessions: {score_breakdown.sessions}</span>
        <span>Revisits: {score_breakdown.revisits}</span>
        <span>Views: {score_breakdown.page_views}</span>
        <span>Time: {score_breakdown.time_spent}</span>
      </div>

      <div className="card-explanation">
        {reasoning}
      </div>
    </div>
  );
}

