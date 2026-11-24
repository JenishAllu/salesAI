import React from 'react';
import { ArrowRight, HelpCircle, Activity } from 'lucide-react';

export default function SensitivityPanel({ sensitivity }) {
  if (!sensitivity) return null;

  const {
    changed_field,
    previous_value,
    new_value,
    predictions_affected,
    previous_assignment,
    updated_assignment,
    impact_summary,
    explanation
  } = sensitivity;

  return (
    <div className="sensitivity-banner">
      <Activity size={22} color="#60a5fa" style={{ marginTop: '2px' }} />
      <div className="sensitivity-content">
        <div className="sensitivity-title">
          Sensitivity Analysis: Why did the state change?
        </div>
        <div className="sensitivity-desc">
          <strong>Field Modified:</strong> <span style={{ fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>{changed_field}</span>{' '}
          (<span>{String(previous_value)}</span> <ArrowRight size={12} style={{ display: 'inline', verticalAlign: 'middle' }} /> <span>{String(new_value)}</span>)
        </div>
        <div style={{ fontSize: '0.8rem', color: '#e2e8f0', marginTop: '0.2rem' }}>
          <strong>Impact:</strong> {impact_summary}
        </div>
        <div style={{ fontSize: '0.76rem', color: '#94a3b8', marginTop: '0.2rem' }}>
          <strong>Reasoning:</strong> {explanation}
        </div>
        {predictions_affected && (
          <div className="sensitivity-tags">
            {predictions_affected.map((t, idx) => (
              <span key={idx} className="sensitivity-tag">
                Target: {t}
              </span>
            ))}
            {previous_assignment && updated_assignment && (
              <span className="sensitivity-tag" style={{ color: '#38bdf8', borderColor: '#0284c7' }}>
                Routing: {previous_assignment} → {updated_assignment}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

