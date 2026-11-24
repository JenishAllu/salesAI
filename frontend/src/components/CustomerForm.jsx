import React from 'react';
import { User, Activity, MessageSquare, AlertCircle, Sparkles } from 'lucide-react';

export default function CustomerForm({ values, onChange }) {
  const handleTextOrNumber = (e) => {
    const { name, value, type } = e.target;
    let parsedVal = value;
    if (type === 'number') {
      parsedVal = value === '' ? 0 : parseFloat(value);
    }
    onChange(name, parsedVal);
  };

  const handleCheckbox = (e) => {
    const { name, checked } = e.target;
    onChange(name, checked);
  };

  return (
    <div className="form-panel">
      {/* SECTION A: CUSTOMER PROFILE */}
      <div className="form-section">
        <div className="section-title">
          <User size={15} />
          <span>A. Customer Profile</span>
        </div>

        <div className="field-grid">
          {/* Age */}
          <div className="field-group">
            <label className="field-label">
              <span>Age (Years)</span>
              <span className="field-val-hint">{values.age}</span>
            </label>
            <input
              type="number"
              name="age"
              min="18"
              max="90"
              value={values.age}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Monthly Income */}
          <div className="field-group">
            <label className="field-label">
              <span>Monthly Income (₹)</span>
              <span className="field-val-hint">₹{Number(values.monthly_income).toLocaleString('en-IN')}</span>
            </label>
            <input
              type="number"
              name="monthly_income"
              step="5000"
              min="10000"
              max="1000000"
              value={values.monthly_income}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Credit Score */}
          <div className="field-group">
            <label className="field-label">
              <span>Credit Score (300-850)</span>
              <span className="field-val-hint">{values.credit_score}</span>
            </label>
            <input
              type="number"
              name="credit_score"
              min="300"
              max="850"
              value={values.credit_score}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Marital Status */}
          <div className="field-group">
            <label className="field-label">Marital Status</label>
            <select
              name="marital_status"
              value={values.marital_status}
              onChange={handleTextOrNumber}
              className="input-control"
            >
              <option value="Single">Single</option>
              <option value="Married">Married</option>
              <option value="Divorced">Divorced</option>
              <option value="Widowed">Widowed</option>
            </select>
          </div>

          {/* Dependents */}
          <div className="field-group">
            <label className="field-label">
              <span>Dependents</span>
              <span className="field-val-hint">{values.dependents}</span>
            </label>
            <input
              type="number"
              name="dependents"
              min="0"
              max="8"
              value={values.dependents}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Selected Category */}
          <div className="field-group">
            <label className="field-label">Selected Category</label>
            <select
              name="selected_category"
              value={values.selected_category}
              onChange={handleTextOrNumber}
              className="input-control"
            >
              <option value="None">None (Unspecified)</option>
              <option value="Health">Health</option>
              <option value="Life">Life</option>
              <option value="Vehicle">Vehicle</option>
              <option value="General">General</option>
            </select>
          </div>

          {/* Existing Policy */}
          <div className="field-group full-width">
            <div className="toggle-wrapper">
              <span style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>Existing Policy Holder?</span>
              <label className="switch">
                <input
                  type="checkbox"
                  name="existing_policy"
                  checked={Boolean(values.existing_policy)}
                  onChange={handleCheckbox}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION B: CUSTOMER BEHAVIOUR */}
      <div className="form-section">
        <div className="section-title">
          <Activity size={15} />
          <span>B. Customer Browsing Behaviour</span>
        </div>

        <div className="field-grid">
          {/* Health Views & Time */}
          <div className="field-group">
            <label className="field-label">
              <span>Health Views</span>
              <span className="field-val-hint">{values.health_page_views}</span>
            </label>
            <input
              type="number"
              name="health_page_views"
              min="0"
              max="50"
              value={values.health_page_views}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>
          <div className="field-group">
            <label className="field-label">
              <span>Health Dwell Time</span>
              <span className="field-val-hint">{values.health_time}s</span>
            </label>
            <input
              type="number"
              name="health_time"
              min="0"
              step="30"
              value={values.health_time}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Life Views & Time */}
          <div className="field-group">
            <label className="field-label">
              <span>Life Views</span>
              <span className="field-val-hint">{values.life_page_views}</span>
            </label>
            <input
              type="number"
              name="life_page_views"
              min="0"
              max="50"
              value={values.life_page_views}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>
          <div className="field-group">
            <label className="field-label">
              <span>Life Dwell Time</span>
              <span className="field-val-hint">{values.life_time}s</span>
            </label>
            <input
              type="number"
              name="life_time"
              min="0"
              step="30"
              value={values.life_time}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Vehicle Views & Time */}
          <div className="field-group">
            <label className="field-label">
              <span>Vehicle Views</span>
              <span className="field-val-hint">{values.vehicle_page_views}</span>
            </label>
            <input
              type="number"
              name="vehicle_page_views"
              min="0"
              max="50"
              value={values.vehicle_page_views}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>
          <div className="field-group">
            <label className="field-label">
              <span>Vehicle Dwell Time</span>
              <span className="field-val-hint">{values.vehicle_time}s</span>
            </label>
            <input
              type="number"
              name="vehicle_time"
              min="0"
              step="30"
              value={values.vehicle_time}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* General Views & Time */}
          <div className="field-group">
            <label className="field-label">
              <span>General Views</span>
              <span className="field-val-hint">{values.general_page_views}</span>
            </label>
            <input
              type="number"
              name="general_page_views"
              min="0"
              max="50"
              value={values.general_page_views}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>
          <div className="field-group">
            <label className="field-label">
              <span>General Dwell Time</span>
              <span className="field-val-hint">{values.general_time}s</span>
            </label>
            <input
              type="number"
              name="general_time"
              min="0"
              step="30"
              value={values.general_time}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>
        </div>
      </div>

      {/* SECTION C: ENGAGEMENT SIGNALS */}
      <div className="form-section">
        <div className="section-title">
          <MessageSquare size={15} />
          <span>C. Engagement & Intent Signals</span>
        </div>

        <div className="field-grid">
          {/* Total Sessions */}
          <div className="field-group">
            <label className="field-label">
              <span>Total Sessions</span>
              <span className="field-val-hint">{values.total_sessions}</span>
            </label>
            <input
              type="number"
              name="total_sessions"
              min="1"
              max="30"
              value={values.total_sessions}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Return Visits */}
          <div className="field-group">
            <label className="field-label">
              <span>Return Visits</span>
              <span className="field-val-hint">{values.return_visits}</span>
            </label>
            <input
              type="number"
              name="return_visits"
              min="0"
              max="30"
              value={values.return_visits}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Quote Requests */}
          <div className="field-group">
            <label className="field-label">
              <span>Quote Requests</span>
              <span className="field-val-hint">{values.quote_requests}</span>
            </label>
            <input
              type="number"
              name="quote_requests"
              min="0"
              max="10"
              value={values.quote_requests}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Callback Requests */}
          <div className="field-group">
            <label className="field-label">
              <span>Callback Requests</span>
              <span className="field-val-hint">{values.callback_requests}</span>
            </label>
            <input
              type="number"
              name="callback_requests"
              min="0"
              max="5"
              value={values.callback_requests}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Chat Count */}
          <div className="field-group">
            <label className="field-label">
              <span>Chat Count</span>
              <span className="field-val-hint">{values.chat_count}</span>
            </label>
            <input
              type="number"
              name="chat_count"
              min="0"
              max="20"
              value={values.chat_count}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Risk Score */}
          <div className="field-group">
            <label className="field-label">
              <span>Risk Score (0-100)</span>
              <span className="field-val-hint">{values.risk_score}</span>
            </label>
            <input
              type="number"
              name="risk_score"
              min="0"
              max="100"
              value={values.risk_score}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Doubts */}
          <div className="field-group">
            <label className="field-label">
              <span>Recorded Doubts</span>
              <span className="field-val-hint">{values.doubts}</span>
            </label>
            <input
              type="number"
              name="doubts"
              min="0"
              max="15"
              value={values.doubts}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Questions */}
          <div className="field-group">
            <label className="field-label">
              <span>Questions Asked</span>
              <span className="field-val-hint">{values.questions}</span>
            </label>
            <input
              type="number"
              name="questions"
              min="0"
              max="20"
              value={values.questions}
              onChange={handleTextOrNumber}
              className="input-control"
            />
          </div>

          {/* Customer Language */}
          <div className="field-group full-width">
            <label className="field-label">Customer Preferred Language</label>
            <select
              name="language"
              value={values.language}
              onChange={handleTextOrNumber}
              className="input-control"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="Telugu">Telugu (తెలుగు)</option>
              <option value="Tamil">Tamil (தமிழ்)</option>
              <option value="Kannada">Kannada (ಕನ್ನಡ)</option>
              <option value="Marathi">Marathi (मराठी)</option>
              <option value="Bengali">Bengali (বাংলা)</option>
              <option value="Gujarati">Gujarati (ગુજરાતી)</option>
            </select>
          </div>

          {/* Previous Agent Failed Escalation Toggle */}
          <div className="field-group full-width">
            <div className="toggle-wrapper" style={{ borderColor: values.previous_agent_failed ? '#ef4444' : 'var(--border-color)' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: values.previous_agent_failed ? '#f87171' : '#cbd5e1', fontWeight: 600 }}>
                  Previous Agent Failed?
                </span>
                <p style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                  Activates immediate Senior Expert escalation override
                </p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  name="previous_agent_failed"
                  checked={Boolean(values.previous_agent_failed)}
                  onChange={handleCheckbox}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          {/* Customer Message / Conversation */}
          <div className="field-group full-width">
            <label className="field-label">
              <span>Customer Message / Inbound Conversation</span>
              <span style={{ fontSize: '0.68rem', color: '#a78bfa' }}>Analyzed by TF-IDF + NLP Model</span>
            </label>
            <textarea
              name="customer_message"
              rows="3"
              value={values.customer_message}
              onChange={handleTextOrNumber}
              placeholder="e.g. I want to purchase health insurance today."
              className="input-control"
            ></textarea>
          </div>
        </div>
      </div>
    </div>
  );
}

