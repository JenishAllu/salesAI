import React from 'react';
import { Compass, CheckCircle2 } from 'lucide-react';

export default function DomainCard({ data }) {
  if (!data) return null;

  const {
    primary_domain,
    secondary_domain,
    domain_probabilities = {},
    confidence,
    evidence = [],
    explanation
  } = data;

  const domainColors = {
    Health: '#10b981',
    Life: '#3b82f6',
    Vehicle: '#f59e0b',
    General: '#8b5cf6',
    Unknown: '#6b7280'
  };

  const badgeClass = {
    Health: 'badge-green',
    Life: 'badge-blue',
    Vehicle: 'badge-amber',
    General: 'badge-purple',
    Unknown: 'badge-amber'
  }[primary_domain] || 'badge-blue';

  return (
    <div className="output-card">
      <div className="card-header">
        <div className="card-title-group">
          <span className="card-icon">🎯</span>
          <h2 className="card-title">1. Insurance Domain</h2>
        </div>
        <span className={`card-badge ${badgeClass}`}>
          {primary_domain} ({Math.round(confidence * 100)}%)
        </span>
      </div>

      <div style={{ marginBottom: '0.85rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.6rem' }}>
          <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>Primary:</span>
          <span style={{ fontWeight: 700, color: domainColors[primary_domain] || '#fff', fontSize: '1rem' }}>
            {primary_domain}
          </span>
          {secondary_domain && (
            <>
              <span style={{ fontSize: '0.78rem', color: '#6b7280', margin: '0 0.2rem' }}>|</span>
              <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>Secondary:</span>
              <span style={{ fontWeight: 600, color: domainColors[secondary_domain] || '#cbd5e1', fontSize: '0.85rem' }}>
                {secondary_domain}
              </span>
            </>
          )}
        </div>

        {/* Probabilities Distribution */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {['Health', 'Life', 'Vehicle', 'General'].map((dom) => {
            const prob = domain_probabilities[dom] || 0;
            const pct = Math.round(prob * 100);
            return (
              <div key={dom} className="domain-prob-row">
                <span style={{ width: '60px', color: '#cbd5e1' }}>{dom}</span>
                <div className="domain-prob-bar">
                  <div
                    className="domain-prob-fill"
                    style={{
                      width: `${pct}%`,
                      backgroundColor: domainColors[dom]
                    }}
                  ></div>
                </div>
                <span style={{ width: '35px', textAlign: 'right', fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>
                  {pct}%
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {evidence && evidence.length > 0 && (
        <div style={{ marginBottom: '0.6rem' }}>
          <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.2rem' }}>
            Supporting Signals
          </div>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {evidence.slice(0, 3).map((ev, i) => (
              <li key={i} style={{ fontSize: '0.75rem', color: '#e2e8f0', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.2rem' }}>
                <CheckCircle2 size={12} color="#10b981" />
                <span>{ev}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card-explanation">
        {explanation}
      </div>
    </div>
  );
}

