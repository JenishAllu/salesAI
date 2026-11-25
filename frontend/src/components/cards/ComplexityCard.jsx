import React from 'react';
import { Layers, AlertTriangle, AlertOctagon, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function ComplexityCard({ data }) {
  if (!data) return null;

  const {
    complexity_score,
    complexity_level,
    service_risk,
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

  const riskScore = service_risk ? service_risk.risk_score : 20;
  const riskTier = service_risk ? service_risk.risk_tier : 'Standard Low Risk';
  const verificationReq = service_risk ? service_risk.verification_requirement : 'Standard KYC Verification';
  const isHighRisk = riskScore >= 75;

  const riskColor = riskScore >= 75 ? '#ef4444' : riskScore >= 45 ? '#f59e0b' : '#10b981';
  const riskBg = riskScore >= 75 ? 'rgba(239, 68, 68, 0.15)' : riskScore >= 45 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)';

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

      {/* Service & Underwriting Risk Meter */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.55)',
          border: `1px solid ${riskColor}40`,
          borderRadius: '8px',
          padding: '0.55rem 0.75rem',
          marginBottom: '0.65rem'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.72rem', fontWeight: 600, color: '#e2e8f0' }}>
            {isHighRisk ? <ShieldAlert size={14} color="#ef4444" /> : <ShieldCheck size={14} color={riskColor} />}
            <span>Underwriting / Case Risk</span>
          </div>
          <span
            style={{
              fontSize: '0.68rem',
              fontWeight: 700,
              padding: '0.15rem 0.45rem',
              borderRadius: '9999px',
              background: riskBg,
              color: riskColor,
              border: `1px solid ${riskColor}60`
            }}
          >
            {riskScore}/100 • {riskTier}
          </span>
        </div>

        <div className="score-bar-bg" style={{ height: '4px', margin: '0.25rem 0 0.35rem' }}>
          <div
            className="score-bar-fill"
            style={{ width: `${riskScore}%`, backgroundColor: riskColor }}
          ></div>
        </div>

        <div style={{ fontSize: '0.68rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
          <span>Protocol:</span>
          <span style={{ color: '#cbd5e1', fontWeight: 500 }}>{verificationReq}</span>
        </div>
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

