import React from 'react';
import { ShoppingCart, MessageSquare, Check, X } from 'lucide-react';

export default function WillingnessCard({ data }) {
  if (!data) return null;

  const {
    willingness_score,
    willingness_level,
    conversation_intent,
    positive_signals = [],
    negative_signals = [],
    explanation
  } = data;

  const levelColor = {
    Low: '#ef4444',
    Medium: '#f59e0b',
    High: '#10b981'
  }[willingness_level] || '#10b981';

  const badgeClass = {
    Low: 'badge-red',
    Medium: 'badge-amber',
    High: 'badge-green'
  }[willingness_level] || 'badge-green';

  return (
    <div className="output-card">
      <div className="card-header">
        <div className="card-title-group">
          <span className="card-icon">🛒</span>
          <h2 className="card-title">3. Purchase Willingness</h2>
        </div>
        <span className={`card-badge ${badgeClass}`}>
          {willingness_level} Willingness
        </span>
      </div>

      <div className="score-container">
        <span className="score-number" style={{ color: levelColor }}>
          {willingness_score}
        </span>
        <span className="score-max">/ 100</span>
      </div>

      <div className="score-bar-bg">
        <div
          className="score-bar-fill"
          style={{ width: `${willingness_score}%`, backgroundColor: levelColor }}
        ></div>
      </div>

      {/* Detected Intent Pill */}
      <div style={{ marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <span style={{ fontSize: '0.74rem', color: '#9ca3af' }}>NLP Intent:</span>
        <span
          style={{
            fontSize: '0.74rem',
            fontWeight: 600,
            padding: '0.2rem 0.55rem',
            borderRadius: '4px',
            background: 'rgba(139, 92, 246, 0.2)',
            color: '#c084fc',
            border: '1px solid rgba(139, 92, 246, 0.4)'
          }}
        >
          {conversation_intent}
        </span>
      </div>

      {/* Signals List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginBottom: '0.6rem' }}>
        {positive_signals.slice(0, 2).map((sig, i) => (
          <div key={i} style={{ fontSize: '0.74rem', color: '#a7f3d0', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Check size={13} color="#10b981" />
            <span>{sig}</span>
          </div>
        ))}
        {negative_signals.slice(0, 2).map((sig, i) => (
          <div key={i} style={{ fontSize: '0.74rem', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <X size={13} color="#ef4444" />
            <span>{sig}</span>
          </div>
        ))}
      </div>

      <div className="card-explanation">
        {explanation}
      </div>
    </div>
  );
}

