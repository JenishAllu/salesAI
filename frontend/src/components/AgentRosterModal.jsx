import React, { useState } from 'react';
import { X, Search, Filter } from 'lucide-react';

export default function AgentRosterModal({ isOpen, onClose, agents = [] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState('ALL');

  if (!isOpen) return null;

  const filteredAgents = agents.filter((a) => {
    const matchSearch =
      a.agent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.agent_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (Array.isArray(a.specializations)
        ? a.specializations.join(' ').toLowerCase()
        : String(a.specializations).toLowerCase()
      ).includes(searchTerm.toLowerCase()) ||
      (Array.isArray(a.supported_languages)
        ? a.supported_languages.join(' ').toLowerCase()
        : String(a.supported_languages).toLowerCase()
      ).includes(searchTerm.toLowerCase());

    const matchLevel = levelFilter === 'ALL' || a.agent_level === levelFilter;
    return matchSearch && matchLevel;
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f3f4f6' }}>
              Synthetic Agent Roster ({agents.length} Qualified Agents)
            </h3>
            <p style={{ fontSize: '0.74rem', color: '#9ca3af' }}>
              Live availability, specializations, supported languages, and capacity tracking
            </p>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div style={{ padding: '0.85rem 1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.4)' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={15} style={{ position: 'absolute', left: '10px', top: '10px', color: '#9ca3af' }} />
            <input
              type="text"
              placeholder="Search by agent name, ID, domain, language..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '32px', width: '100%' }}
            />
          </div>

          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="input-control"
            style={{ width: '180px' }}
          >
            <option value="ALL">All Levels</option>
            <option value="Intern Agent">Intern Agent</option>
            <option value="Expert Agent">Expert Agent</option>
            <option value="Senior Expert Agent">Senior Expert Agent</option>
          </select>
        </div>

        <div className="modal-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '0.85rem' }}>
            {filteredAgents.map((agent) => {
              const isOnline = Boolean(agent.is_online);
              const specs = Array.isArray(agent.specializations)
                ? agent.specializations.join(', ')
                : agent.specializations;
              const langs = Array.isArray(agent.supported_languages)
                ? agent.supported_languages.join(', ')
                : agent.supported_languages;

              const tierClass = {
                'Intern Agent': 'badge-green',
                'Expert Agent': 'badge-blue',
                'Senior Expert Agent': 'badge-purple'
              }[agent.agent_level] || 'badge-blue';

              return (
                <div
                  key={agent.agent_id}
                  style={{
                    background: 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.85rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.4rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#f3f4f6' }}>
                        {agent.agent_name}
                      </div>
                      <div style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>
                        {agent.agent_id}
                      </div>
                    </div>
                    <span className={`card-badge ${tierClass}`} style={{ fontSize: '0.65rem' }}>
                      {agent.agent_level.replace(' Agent', '')}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.74rem', color: '#cbd5e1' }}>
                    <strong>Specialization:</strong> {specs}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#cbd5e1' }}>
                    <strong>Languages:</strong> {langs}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9ca3af', marginTop: 'auto', paddingTop: '0.4rem', borderTop: '1px solid #1f2937' }}>
                    <span>Exp: {agent.experience_years}y • ★ {agent.performance_rating}</span>
                    <span style={{ color: isOnline ? '#34d399' : '#9ca3af' }}>
                      {agent.availability_status} ({agent.current_workload}/{agent.max_workload})
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

