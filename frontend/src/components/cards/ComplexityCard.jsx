import React from 'react';
import { Layers, AlertTriangle, AlertOctagon } from 'lucide-react';

export default function ComplexityCard({ data }) {
  if (!data) return null;

  const {
    complexity_score,
    complexity_level,
    main_complexity_factors = [],
    missing_information = [],
    explanation
  } = data;

  const levelColor = {
    Low: '#10b981',
    Medium: '#f59e0b',
    High: '#ef4444'
  }[complexity_level] || '#10b981';

  const badgeClass = {
    Low: 'badge-green',
    Medium: 'badge-amber',
    High: 'badge-red'
  }[complexity_level] || 'badge-green';

  return (
    <div className="output-card">
      <div className="card-header">
        <div className="card-title-group">
          <span className="card-icon">🧩</span>
          <h2 className="card-title">4. Customer Complexity</h2>
        </div>
        <span className={`card-badge ${badgeClass}`}>
          {complexity_level} Complexity
        </span>
      </div>

      <div className="score-container">
        <span className="score-number" style={{ color: levelColor }}>
          {complexity_score}
        </span>
        <span className="score-max">/ 100</span>
      </div>

      <div className="score-bar-bg">
        <div
          className="score-bar-fill"
          style={{ width: `${complexity_score}%`, backgroundColor: levelColor }}
        ></div>
      </div>

      {/* Complexity Factors */}
      <div style={{ marginBottom: '0.65rem' }}>
        <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.25rem' }}>
          Key Factors
        </div>
        {main_complexity_factors.length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {main_complexity_factors.slice(0, 3).map((fac, i) => (
              <li key={i} style={{ fontSize: '0.74rem', color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
                <AlertTriangle size={12} color="#f59e0b" />
                <span>{fac}</span>
              </li>
            ))}
          </ul>
        ) : (
          <span style={{ fontSize: '0.75rem', color: '#6ee7b7' }}>
            ✓ Standard single-domain requirements with no recorded friction.
          </span>
        )}
      </div>

      {/* Missing Information Notice if any */}
      {missing_information.length > 0 && (
        <div style={{ fontSize: '0.72rem', color: '#94a3b8', background: 'rgba(30, 41, 59, 0.5)', padding: '0.35rem 0.5rem', borderRadius: '4px', marginBottom: '0.5rem' }}>
          <strong>Notice:</strong> {missing_information.join(', ')}
        </div>
      )}

      <div className="card-explanation">
        {explanation}
      </div>
    </div>
  );
}

