import React from 'react';
import { PlayCircle, Zap } from 'lucide-react';
import { SCENARIO_LIST } from '../data/scenarios';

export default function ScenarioBar({ activeScenarioId, onSelectScenario }) {
  return (
    <div className="scenarios-container">
      <div className="scenarios-header">
        <div className="scenarios-title">
          <Zap size={15} color="#f59e0b" />
          <span>Quick Demonstration Scenarios (Click to Live-Populate & Simulate)</span>
        </div>
        <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
          Outputs update automatically via real ML inference
        </span>
      </div>

      <div className="scenario-chips">
        {SCENARIO_LIST.map((sc) => {
          const isActive = activeScenarioId === sc.id;
          return (
            <button
              key={sc.id}
              className={`scenario-chip ${isActive ? 'active' : ''}`}
              onClick={() => onSelectScenario(sc)}
              title={sc.description}
            >
              <PlayCircle size={13} color={isActive ? '#3b82f6' : '#9ca3af'} />
              <span>{sc.title}</span>
              <span className={`chip-tag ${sc.badgeColor || 'badge-blue'}`}>
                {sc.badge}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

