import React, { useState, useEffect } from 'react';
import {
  X,
  Search,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  RotateCw,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  UserCheck,
  Award
} from 'lucide-react';
import { fetchAgentHistory, submitAgentOutcome } from '../api/client';

export default function AgentRosterModal({
  isOpen,
  onClose,
  agents = [],
  onLoadCustomerInSimulator
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState('ALL');
  const [selectedAgent, setSelectedAgent] = useState(null);

  // History & outcome state
  const [history, setHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [actionLoadingCaseId, setActionLoadingCaseId] = useState(null);
  const [escalationResult, setEscalationResult] = useState(null);
  const [actionSuccessMsg, setActionSuccessMsg] = useState('');

  // Reset selected agent when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedAgent(null);
      setEscalationResult(null);
      setActionSuccessMsg('');
    }
  }, [isOpen]);

  // Load history when an agent is selected
  const handleSelectAgent = async (agent) => {
    setSelectedAgent(agent);
    setEscalationResult(null);
    setActionSuccessMsg('');
    setIsLoadingHistory(true);
    try {
      const data = await fetchAgentHistory(agent.agent_id);
      setHistory(data.history || []);
      if (data.agent) {
        setSelectedAgent(data.agent);
      }
    } catch (err) {
      console.error('Failed to fetch agent history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Submit outcome (Succeeded or Failed)
  const handleOutcomeChange = async (caseId, outcome) => {
    if (!selectedAgent) return;
    setActionLoadingCaseId(caseId);
    setEscalationResult(null);
    setActionSuccessMsg('');

    try {
      const defaultNote =
        outcome === 'failed'
          ? 'Customer requested senior specialist assistance; agent unable to resolve policy terms.'
          : 'Successfully assisted customer with policy issuance.';

      const res = await submitAgentOutcome(
        selectedAgent.agent_id,
        caseId,
        outcome,
        defaultNote
      );

      if (res.status === 'success') {
        if (res.history) {
          setHistory(res.history);
        }
        if (res.agent) {
          setSelectedAgent(res.agent);
        }

        if (outcome === 'failed' && res.escalation) {
          setEscalationResult(res.escalation);
        } else {
          setActionSuccessMsg(
            `Case ${caseId} marked as Succeeded! Agent performance rating updated.`
          );
        }
      }
    } catch (err) {
      console.error('Failed to update case outcome:', err);
      alert('Failed to update outcome: ' + err.message);
    } finally {
      setActionLoadingCaseId(null);
    }
  };

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
      <div
        className="modal-card"
        style={{ maxWidth: '1400px', width: '96vw', height: '90vh' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* MODAL HEADER */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {selectedAgent && (
              <button
                className="btn btn-secondary"
                style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                onClick={() => {
                  setSelectedAgent(null);
                  setEscalationResult(null);
                }}
              >
                <ArrowLeft size={14} />
                <span>All Agents</span>
              </button>
            )}
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f3f4f6' }}>
                {selectedAgent
                  ? `${selectedAgent.agent_name} (${selectedAgent.agent_id}) — Case History & Performance`
                  : `Synthetic Agent Roster (${agents.length} Qualified Agents)`}
              </h3>
              <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                {selectedAgent
                  ? 'Inspect past customer assignments, record success/failure outcomes, trigger ML retraining, and escalate failed cases to higher agents.'
                  : 'Click on any agent to inspect their full assignment history and test failure outcome escalation.'}
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* VIEW 1: AGENT LIST (When no agent is selected) */}
        {!selectedAgent ? (
          <>
            <div
              style={{
                padding: '0.85rem 1.5rem',
                borderBottom: '1px solid var(--border-color)',
                display: 'flex',
                gap: '0.75rem',
                background: 'rgba(15, 23, 42, 0.4)'
              }}
            >
              <div style={{ position: 'relative', flex: 1 }}>
                <Search
                  size={15}
                  style={{ position: 'absolute', left: '10px', top: '10px', color: '#9ca3af' }}
                />
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
                style={{ width: '190px' }}
              >
                <option value="ALL">All Levels ({agents.length})</option>
                <option value="Intern Agent">Intern Agents</option>
                <option value="Expert Agent">Expert Agents</option>
                <option value="Senior Expert Agent">Senior Expert Agents</option>
              </select>
            </div>

            <div className="modal-body" style={{ flex: 1, overflowY: 'auto' }}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))',
                  gap: '0.85rem'
                }}
              >
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
                      onClick={() => handleSelectAgent(agent)}
                      style={{
                        background: 'var(--bg-card-subtle)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '10px',
                        padding: '1rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.45rem',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = '#3b82f6';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-color)';
                        e.currentTarget.style.transform = 'none';
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start'
                        }}
                      >
                        <div>
                          <div
                            style={{ fontWeight: 700, fontSize: '0.95rem', color: '#f3f4f6' }}
                          >
                            {agent.agent_name}
                          </div>
                          <div
                            style={{
                              fontSize: '0.72rem',
                              fontFamily: 'var(--font-mono)',
                              color: '#93c5fd'
                            }}
                          >
                            {agent.agent_id}
                          </div>
                        </div>
                        <span className={`card-badge ${tierClass}`} style={{ fontSize: '0.68rem' }}>
                          {agent.agent_level.replace(' Agent', '')}
                        </span>
                      </div>

                      <div style={{ fontSize: '0.76rem', color: '#cbd5e1' }}>
                        <span style={{ color: '#9ca3af' }}>Domain:</span>{' '}
                        <strong>{specs}</strong>
                      </div>
                      <div style={{ fontSize: '0.76rem', color: '#cbd5e1' }}>
                        <span style={{ color: '#9ca3af' }}>Languages:</span> {langs}
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '0.72rem',
                          color: '#9ca3af',
                          marginTop: 'auto',
                          paddingTop: '0.5rem',
                          borderTop: '1px solid #1f2937'
                        }}
                      >
                        <span>Exp: {agent.experience_years}y • ★ {agent.performance_rating}</span>
                        <span style={{ color: isOnline ? '#34d399' : '#9ca3af', fontWeight: 600 }}>
                          {agent.availability_status} ({agent.current_workload}/{agent.max_workload})
                        </span>
                      </div>

                      <div
                        style={{
                          textAlign: 'center',
                          fontSize: '0.7rem',
                          color: '#60a5fa',
                          fontWeight: 600,
                          marginTop: '0.2rem'
                        }}
                      >
                        Click to view history & test outcomes →
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        ) : (
          /* VIEW 2: SPECIFIC AGENT DETAIL & HISTORY */
          <div className="modal-body" style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Agent Profile Overview Card */}
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.25), rgba(88, 28, 135, 0.25))',
                border: '1px solid rgba(59, 130, 246, 0.4)',
                borderRadius: '12px',
                padding: '1.2rem',
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '1rem'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                  <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#ffffff' }}>
                    {selectedAgent.agent_name}
                  </h2>
                  <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>
                    ({selectedAgent.agent_id})
                  </span>
                  <span
                    className={`card-badge ${
                      {
                        'Intern Agent': 'badge-green',
                        'Expert Agent': 'badge-blue',
                        'Senior Expert Agent': 'badge-purple'
                      }[selectedAgent.agent_level] || 'badge-blue'
                    }`}
                  >
                    {selectedAgent.agent_level}
                  </span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', fontSize: '0.76rem', color: '#cbd5e1' }}>
                  <span>
                    Specializations:{' '}
                    <strong>
                      {Array.isArray(selectedAgent.specializations)
                        ? selectedAgent.specializations.join(', ')
                        : selectedAgent.specializations}
                    </strong>
                  </span>
                  <span>•</span>
                  <span>
                    Languages:{' '}
                    <strong>
                      {Array.isArray(selectedAgent.supported_languages)
                        ? selectedAgent.supported_languages.join(', ')
                        : selectedAgent.supported_languages}
                    </strong>
                  </span>
                </div>
              </div>

              {/* Stats badges */}
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.7)',
                    padding: '0.5rem 0.85rem',
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Experience</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6' }}>
                    {selectedAgent.experience_years} Years
                  </div>
                </div>

                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.7)',
                    padding: '0.5rem 0.85rem',
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Workload</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#38bdf8' }}>
                    {selectedAgent.current_workload} / {selectedAgent.max_workload} Cases
                  </div>
                </div>

                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.7)',
                    padding: '0.5rem 0.85rem',
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Rating</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fbbf24' }}>
                    ★ {selectedAgent.performance_rating}
                  </div>
                </div>
              </div>
            </div>

            {/* ESCALATION SUCCESS BANNER (If a case was marked failed and escalated) */}
            {escalationResult && (
              <div
                style={{
                  background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.25), rgba(139, 92, 246, 0.25))',
                  border: '1px solid #ef4444',
                  borderRadius: '10px',
                  padding: '1rem 1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  animation: 'fadeIn 0.3s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f87171', fontWeight: 700, fontSize: '0.95rem' }}>
                    <AlertTriangle size={18} />
                    <span>Case Failure Recorded & Customer Escalated to Higher Tier!</span>
                  </div>
                  <span className="card-badge badge-green" style={{ fontSize: '0.72rem' }}>
                    ML Models Retrained
                  </span>
                </div>

                <div style={{ fontSize: '0.82rem', color: '#f3f4f6' }}>
                  <strong>Previous Agent:</strong> {escalationResult.previous_agent?.name} ({escalationResult.previous_agent?.level}) — <span style={{ color: '#ef4444' }}>Resolution Failed</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#a7f3d0' }}>
                  <strong>🚀 Re-assigned to Higher Agent:</strong> {escalationResult.new_agent?.agent_name} ({escalationResult.new_agent?.agent_id} - <strong style={{ color: '#60a5fa' }}>{escalationResult.new_agent?.agent_level}</strong>)
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>
                    {escalationResult.new_agent?.reason}
                  </div>
                </div>

                {onLoadCustomerInSimulator && escalationResult.customer_data && (
                  <button
                    className="btn btn-primary"
                    style={{ alignSelf: 'flex-start', marginTop: '0.4rem', padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
                    onClick={() => {
                      onLoadCustomerInSimulator(escalationResult.customer_data);
                      onClose();
                    }}
                  >
                    <ExternalLink size={14} />
                    <span>Load This Escalated Customer in Live Simulator</span>
                  </button>
                )}
              </div>
            )}

            {actionSuccessMsg && (
              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid #10b981',
                  borderRadius: '8px',
                  padding: '0.75rem 1rem',
                  color: '#34d399',
                  fontSize: '0.82rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <CheckCircle2 size={16} />
                <span>{actionSuccessMsg}</span>
              </div>
            )}

            {/* CASES HISTORY SECTION */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f3f4f6' }}>
                  Entire Customer Interaction & Assignment History ({history.length} Cases)
                </h4>
                <span style={{ fontSize: '0.74rem', color: '#9ca3af' }}>
                  Evaluate resolution outcomes or simulate escalations
                </span>
              </div>

              {isLoadingHistory ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af' }}>
                  <RotateCw size={24} className="spinner" style={{ margin: '0 auto 0.5rem' }} />
                  <div>Loading assignment history...</div>
                </div>
              ) : history.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af', background: 'var(--bg-card-subtle)', borderRadius: '8px' }}>
                  No past customer interactions recorded for this agent yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {history.map((c) => {
                    const isCaseLoading = actionLoadingCaseId === c.case_id;
                    const outcome = c.outcome || 'in_progress';

                    const outcomeBadge = {
                      succeeded: (
                        <span className="card-badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                          <CheckCircle2 size={12} />
                          <span>Succeeded</span>
                        </span>
                      ),
                      failed: (
                        <span className="card-badge badge-red" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                          <XCircle size={12} />
                          <span>Failed (Escalated)</span>
                        </span>
                      ),
                      in_progress: (
                        <span className="card-badge badge-amber" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                          <Clock size={12} />
                          <span>In Progress</span>
                        </span>
                      )
                    }[outcome] || (
                      <span className="card-badge badge-amber">Active</span>
                    );

                    return (
                      <div
                        key={c.case_id}
                        style={{
                          background: 'var(--bg-card-subtle)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '10px',
                          padding: '1rem',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.6rem'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <span style={{ fontWeight: 700, fontSize: '0.92rem', color: '#f3f4f6' }}>
                                {c.customer_name || 'Customer'}
                              </span>
                              <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: '#93c5fd' }}>
                                ({c.customer_id})
                              </span>
                              <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>• Case: {c.case_id}</span>
                            </div>
                            <div style={{ fontSize: '0.74rem', color: '#9ca3af', marginTop: '0.15rem' }}>
                              Date: {c.date_assigned || 'Recently'} • Domain: <strong style={{ color: '#60a5fa' }}>{c.domain}</strong> • Complexity: <strong style={{ color: '#fbbf24' }}>{c.complexity}</strong>
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {outcomeBadge}
                          </div>
                        </div>

                        {/* Case notes / message */}
                        <div style={{ fontSize: '0.78rem', color: '#cbd5e1', background: 'rgba(15, 23, 42, 0.4)', padding: '0.5rem 0.75rem', borderRadius: '6px' }}>
                          <div style={{ color: '#94a3b8', fontSize: '0.7rem', marginBottom: '2px' }}>
                            <strong>Interaction Summary:</strong>
                          </div>
                          <div>{c.outcome_notes || 'Customer assisted with policy inquiry.'}</div>
                          {c.customer_data?.customer_message && (
                            <div style={{ fontStyle: 'italic', color: '#93c5fd', marginTop: '0.25rem', fontSize: '0.74rem' }}>
                              "{c.customer_data.customer_message}"
                            </div>
                          )}
                        </div>

                        {/* Escalation note if failed */}
                        {c.escalated_to && (
                          <div style={{ fontSize: '0.74rem', color: '#f87171', background: 'rgba(239, 68, 68, 0.1)', padding: '0.4rem 0.6rem', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                            ⚠️ Escalated to: <strong>{c.escalated_to_name || c.escalated_to}</strong> ({c.escalated_to_level || 'Higher Agent'})
                          </div>
                        )}

                        {/* Interactive Outcome Actions */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.2rem', paddingTop: '0.5rem', borderTop: '1px solid #1f2937' }}>
                          <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
                            Update Outcome:
                          </div>

                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            {/* Button Succeeded */}
                            <button
                              className="btn"
                              style={{
                                background: outcome === 'succeeded' ? '#059669' : 'rgba(16, 185, 129, 0.15)',
                                color: outcome === 'succeeded' ? '#ffffff' : '#34d399',
                                border: '1px solid #10b981',
                                padding: '0.35rem 0.75rem',
                                fontSize: '0.74rem'
                              }}
                              disabled={isCaseLoading}
                              onClick={() => handleOutcomeChange(c.case_id, 'succeeded')}
                            >
                              <CheckCircle2 size={13} />
                              <span>Succeeded</span>
                            </button>

                            {/* Button Failed & Escalate */}
                            <button
                              className="btn"
                              style={{
                                background: outcome === 'failed' ? '#dc2626' : 'rgba(239, 68, 68, 0.15)',
                                color: outcome === 'failed' ? '#ffffff' : '#f87171',
                                border: '1px solid #ef4444',
                                padding: '0.35rem 0.75rem',
                                fontSize: '0.74rem'
                              }}
                              disabled={isCaseLoading}
                              onClick={() => handleOutcomeChange(c.case_id, 'failed')}
                            >
                              {isCaseLoading ? (
                                <RotateCw size={13} className="spinner" />
                              ) : (
                                <XCircle size={13} />
                              )}
                              <span>
                                {isCaseLoading
                                  ? 'Retraining & Escalating...'
                                  : 'Failed (Escalate & Retrain)'}
                              </span>
                            </button>

                            {/* Load in Simulator button */}
                            {c.customer_data && onLoadCustomerInSimulator && (
                              <button
                                className="btn btn-secondary"
                                style={{ padding: '0.35rem 0.65rem', fontSize: '0.74rem' }}
                                onClick={() => {
                                  onLoadCustomerInSimulator(c.customer_data);
                                  onClose();
                                }}
                                title="Load this customer's profile into the live dashboard simulator"
                              >
                                <ExternalLink size={13} />
                                <span>Simulate</span>
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
