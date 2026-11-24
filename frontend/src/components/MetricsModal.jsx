import React, { useState } from 'react';
import { X, CheckCircle, Database, BarChart } from 'lucide-react';

export default function MetricsModal({ isOpen, onClose, metrics = {}, datasetSummary = {} }) {
  const [activeTab, setActiveTab] = useState('metrics');

  if (!isOpen) return null;

  const targetNames = {
    insurance_domain: '1. Insurance Domain Classification',
    customer_engagement: '2. Customer Engagement Classification',
    purchase_willingness: '3. Purchase Willingness Classification',
    customer_complexity: '4. Customer Complexity Classification',
    conversation_intent: '5. Conversation Intent NLP Classification'
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f3f4f6' }}>
              ML Evaluation Metrics & Synthetic Dataset Report
            </h3>
            <p style={{ fontSize: '0.74rem', color: '#9ca3af' }}>
              Rigorous Scikit-Learn evaluation of LR, DT, RF, KNN, and Ensemble on 100,000 synthetic records
            </p>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', padding: '0.75rem 1.5rem', borderBottom: '1px solid var(--border-color)', background: 'rgba(15, 23, 42, 0.4)' }}>
          <button
            className={`btn ${activeTab === 'metrics' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('metrics')}
          >
            <BarChart size={14} />
            <span>Model Evaluation Metrics</span>
          </button>
          <button
            className={`btn ${activeTab === 'dataset' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('dataset')}
          >
            <Database size={14} />
            <span>Dataset Statistics (100,000 Records)</span>
          </button>
        </div>

        <div className="modal-body">
          {activeTab === 'metrics' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {Object.keys(metrics).map((targetKey) => {
                const targetData = metrics[targetKey];
                return (
                  <div key={targetKey} style={{ background: 'var(--bg-card-subtle)', borderRadius: '8px', padding: '1rem', border: '1px solid var(--border-color)' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#60a5fa', marginBottom: '0.5rem' }}>
                      {targetNames[targetKey] || targetKey}
                    </div>

                    <table className="models-table">
                      <thead>
                        <tr>
                          <th>Algorithm</th>
                          <th>Accuracy</th>
                          <th>F1-Score (Weighted)</th>
                          <th>Precision</th>
                          <th>Recall</th>
                        </tr>
                      </thead>
                      <tbody>
                        {['lr', 'dt', 'rf', 'knn', 'ensemble'].map((algo) => {
                          const item = targetData[algo] || {};
                          const isEnsemble = algo === 'ensemble';
                          const algoName = {
                            lr: 'Logistic Regression',
                            dt: 'Decision Tree',
                            rf: 'Random Forest',
                            knn: 'K-Nearest Neighbors',
                            ensemble: '★ Soft-Voting Ensemble'
                          }[algo];

                          return (
                            <tr key={algo} className={isEnsemble ? 'ensemble-row' : ''}>
                              <td style={{ fontWeight: isEnsemble ? 700 : 500 }}>{algoName}</td>
                              <td>{item.accuracy ? `${(item.accuracy * 100).toFixed(1)}%` : '—'}</td>
                              <td>{item.f1_weighted ? `${(item.f1_weighted * 100).toFixed(1)}%` : '—'}</td>
                              <td>{item.precision_weighted ? `${(item.precision_weighted * 100).toFixed(1)}%` : '—'}</td>
                              <td>{item.recall_weighted ? `${(item.recall_weighted * 100).toFixed(1)}%` : '—'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
                <div style={{ background: 'var(--bg-card-subtle)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Total Customers</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                    {datasetSummary.total_rows?.toLocaleString() || '100,000'}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-card-subtle)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Features & Columns</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#a78bfa', fontFamily: 'var(--font-mono)' }}>
                    {datasetSummary.num_columns || '36'}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-card-subtle)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Duplicate Records</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                    0
                  </div>
                </div>
                <div style={{ background: 'var(--bg-card-subtle)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Synthetic Agents</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>
                    40 Roster
                  </div>
                </div>
              </div>

              {/* Class Distributions */}
              {datasetSummary.class_distributions && (
                <div style={{ background: 'var(--bg-card-subtle)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#60a5fa', marginBottom: '0.75rem' }}>
                    Target Class Distributions Across 100,000 Records
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', fontSize: '0.78rem' }}>
                    <div>
                      <div style={{ fontWeight: 600, color: '#cbd5e1', marginBottom: '0.25rem' }}>Insurance Domain:</div>
                      {Object.entries(datasetSummary.class_distributions.insurance_domain || {}).map(([k, v]) => (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', color: '#9ca3af' }}>
                          <span>{k}</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: '#f3f4f6' }}>{Number(v).toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: '#cbd5e1', marginBottom: '0.25rem' }}>Required Agent Level:</div>
                      {Object.entries(datasetSummary.class_distributions.required_agent_level || {}).map(([k, v]) => (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', color: '#9ca3af' }}>
                          <span>{k}</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: '#f3f4f6' }}>{Number(v).toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

