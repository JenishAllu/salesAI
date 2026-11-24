import React from 'react';
import { Cpu } from 'lucide-react';

export default function ModelConfidenceCard({ data }) {
  if (!data) return null;

  const {
    domain_prediction,
    engagement_classification,
    purchase_willingness,
    customer_complexity,
    conversation_intent
  } = data;

  const tasks = [
    {
      name: 'Insurance Domain',
      models: domain_prediction?.model_predictions || {}
    },
    {
      name: 'Customer Engagement',
      models: engagement_classification?.model_predictions || {}
    },
    {
      name: 'Purchase Willingness',
      models: purchase_willingness?.model_predictions || {}
    },
    {
      name: 'Customer Complexity',
      models: customer_complexity?.model_predictions || {}
    },
    {
      name: 'Conversation Intent (NLP)',
      models: conversation_intent?.model_predictions || {}
    }
  ];

  return (
    <div className="output-card full-width">
      <div className="card-header">
        <div className="card-title-group">
          <span className="card-icon">🧠</span>
          <div>
            <h2 className="card-title">6. Multi-Model Confidence & Algorithm Breakdown</h2>
            <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
              Individual algorithm outputs compared against Soft-Voting Ensemble
            </span>
          </div>
        </div>
        <span className="card-badge badge-blue">
          4 ML Algorithms + Ensemble
        </span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="models-table">
          <thead>
            <tr>
              <th style={{ width: '22%' }}>Prediction Target</th>
              <th style={{ width: '15%' }}>Logistic Reg. (LR)</th>
              <th style={{ width: '15%' }}>Decision Tree (DT)</th>
              <th style={{ width: '16%' }}>Random Forest (RF)</th>
              <th style={{ width: '16%' }}>KNN Classifier</th>
              <th style={{ width: '16%', color: '#60a5fa' }}>Soft-Voting Ensemble</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 600, color: '#f3f4f6' }}>{task.name}</td>
                <td style={{ color: '#cbd5e1' }}>{task.models.lr || '—'}</td>
                <td style={{ color: '#cbd5e1' }}>{task.models.dt || '—'}</td>
                <td style={{ color: '#cbd5e1' }}>{task.models.rf || '—'}</td>
                <td style={{ color: '#cbd5e1' }}>{task.models.knn || '—'}</td>
                <td style={{ fontWeight: 700, color: '#93c5fd', background: 'rgba(59, 130, 246, 0.08)' }}>
                  {task.models.ensemble || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card-explanation" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>
          Ensemble uses soft probability voting to synthesize decisions while mitigating individual model bias.
        </span>
        <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
          Calibrated on Scikit-Learn Pipelines
        </span>
      </div>
    </div>
  );
}

