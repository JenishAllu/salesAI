import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API = '/api'

const initialCustomer = {
  age: 35,
  income_monthly: 60000,
  credit_score: 720,
  marital_status: 'married',
  dependents: 2,
  existing_policy: 'none',
  selected_category: 'none',

  health_page_views: 10,
  life_page_views: 1,
  vehicle_page_views: 0,
  general_page_views: 1,

  health_time_seconds: 500,
  life_time_seconds: 30,
  vehicle_time_seconds: 0,
  general_time_seconds: 20,

  health_comparisons: 3,
  life_comparisons: 0,
  vehicle_comparisons: 0,
  general_comparisons: 0,

  total_sessions: 4,
  return_visits: 3,
  quote_requests: 1,
  callback_requests: 0,
  chat_count: 2
}

function Field({ label, name, value, onChange, type='number', options }) {
  return (
    <label className="field">
      <span>{label}</span>
      {options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map(x => <option key={x} value={x}>{x}</option>)}
        </select>
      ) : (
        <input name={name} type={type} value={value} onChange={onChange} min={type === 'number' ? 0 : undefined} />
      )}
    </label>
  )
}

function ScoreBar({ name, value }) {
  const pct = Math.round((Number(value) || 0) * 100)
  return (
    <div className="score">
      <div className="score-top">
        <span>{name}</span><b>{pct}%</b>
      </div>
      <div className="bar"><div style={{width: `${pct}%`}} /></div>
    </div>
  )
}

function App() {
  const [customer, setCustomer] = useState(initialCustomer)
  const [message, setMessage] = useState('I want to compare health insurance for my parents.')
  const [language, setLanguage] = useState('English')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const update = (e) => {
    const { name, value, type } = e.target
    setCustomer(prev => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value
    }))
  }

  const loadScenario = (type) => {
    const base = {...initialCustomer, selected_category: 'none'}
    if (type === 'health') {
      Object.assign(base, {
        health_page_views: 15, life_page_views: 1, vehicle_page_views: 0, general_page_views: 1,
        health_time_seconds: 800, life_time_seconds: 20, vehicle_time_seconds: 0, general_time_seconds: 30,
        health_comparisons: 5, life_comparisons: 0, vehicle_comparisons: 0, general_comparisons: 0
      })
      setMessage('I want to compare health insurance for my parents.')
    }
    if (type === 'life') {
      Object.assign(base, {
        health_page_views: 1, life_page_views: 15, vehicle_page_views: 0, general_page_views: 1,
        health_time_seconds: 20, life_time_seconds: 800, vehicle_time_seconds: 0, general_time_seconds: 30,
        health_comparisons: 0, life_comparisons: 5, vehicle_comparisons: 0, general_comparisons: 0
      })
      setMessage('I want to buy life insurance.')
    }
    if (type === 'vehicle') {
      Object.assign(base, {
        health_page_views: 0, life_page_views: 1, vehicle_page_views: 15, general_page_views: 1,
        health_time_seconds: 0, life_time_seconds: 20, vehicle_time_seconds: 800, general_time_seconds: 30,
        health_comparisons: 0, life_comparisons: 0, vehicle_comparisons: 5, general_comparisons: 0
      })
      setMessage('Please show me vehicle insurance plans.')
    }
    if (type === 'general') {
      Object.assign(base, {
        health_page_views: 1, life_page_views: 1, vehicle_page_views: 1, general_page_views: 15,
        health_time_seconds: 20, life_time_seconds: 20, vehicle_time_seconds: 20, general_time_seconds: 800,
        health_comparisons: 0, life_comparisons: 0, vehicle_comparisons: 0, general_comparisons: 5
      })
      setMessage('I want information about insurance.')
    }
    if (type === 'complex') {
      Object.assign(base, {
        age: 52, income_monthly: 120000, marital_status: 'married', dependents: 4,
        existing_policy: 'multiple',
        health_page_views: 8, life_page_views: 8, vehicle_page_views: 2, general_page_views: 3,
        health_time_seconds: 500, life_time_seconds: 500, vehicle_time_seconds: 100, general_time_seconds: 150,
        health_comparisons: 5, life_comparisons: 5, vehicle_comparisons: 1, general_comparisons: 2,
        total_sessions: 12, return_visits: 11, quote_requests: 3, callback_requests: 1, chat_count: 15
      })
      setMessage('I already have multiple policies and an existing claim. I need help comparing another policy.')
    }
    setCustomer(base)
    setResult(null)
    setError('')
  }

  const analyze = async () => {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({customer, message, language})
      })
      const data = await res.json()
      if (!res.ok || !data.success) throw new Error(data.error || 'Backend request failed')
      setResult(data)
    } catch (e) {
      setError(e.message + ' — Make sure the Flask backend is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setCustomer(initialCustomer)
    setMessage('I want to compare health insurance for my parents.')
    setLanguage('English')
    setResult(null)
    setError('')
  }

  const a = result?.analysis
  const assignment = result?.assignment

  return (
    <div className="app">
      <header>
        <div>
          <div className="eyebrow">AI CUSTOMER ROUTING</div>
          <h1>Insurance Agent AI</h1>
          <p>Analyze customer behavior → predict insurance interest → assign the right agent.</p>
        </div>
        <div className="status"><span className="dot" /> Flask API :5000</div>
      </header>

      <div className="scenario-row">
        <span>Quick scenarios:</span>
        <button onClick={() => loadScenario('health')}>Health</button>
        <button onClick={() => loadScenario('life')}>Life</button>
        <button onClick={() => loadScenario('vehicle')}>Vehicle</button>
        <button onClick={() => loadScenario('general')}>General</button>
        <button onClick={() => loadScenario('complex')}>Complex → Senior</button>
      </div>

      <main>
        <section className="card input-card">
          <div className="card-title">
            <div><h2>Customer profile</h2><p>Enter the information available from the insurance platform.</p></div>
            <button className="ghost" onClick={reset}>Reset</button>
          </div>

          <div className="grid">
            <Field label="Age" name="age" value={customer.age} onChange={update}/>
            <Field label="Monthly income" name="income_monthly" value={customer.income_monthly} onChange={update}/>
            <Field label="Credit score" name="credit_score" value={customer.credit_score} onChange={update}/>
            <Field label="Marital status" name="marital_status" value={customer.marital_status} onChange={update} type="text" options={['single','married']}/>
            <Field label="Dependents" name="dependents" value={customer.dependents} onChange={update}/>
            <Field label="Existing policy" name="existing_policy" value={customer.existing_policy} onChange={update} type="text" options={['none','health','life','vehicle','multiple']}/>
            <Field label="Selected category" name="selected_category" value={customer.selected_category} onChange={update} type="text" options={['none','health','life','vehicle','general']}/>
          </div>

          <h3>Customer behavior</h3>
          <div className="grid four">
            <Field label="Health page views" name="health_page_views" value={customer.health_page_views} onChange={update}/>
            <Field label="Life page views" name="life_page_views" value={customer.life_page_views} onChange={update}/>
            <Field label="Vehicle page views" name="vehicle_page_views" value={customer.vehicle_page_views} onChange={update}/>
            <Field label="General page views" name="general_page_views" value={customer.general_page_views} onChange={update}/>
            <Field label="Health time (sec)" name="health_time_seconds" value={customer.health_time_seconds} onChange={update}/>
            <Field label="Life time (sec)" name="life_time_seconds" value={customer.life_time_seconds} onChange={update}/>
            <Field label="Vehicle time (sec)" name="vehicle_time_seconds" value={customer.vehicle_time_seconds} onChange={update}/>
            <Field label="General time (sec)" name="general_time_seconds" value={customer.general_time_seconds} onChange={update}/>
            <Field label="Health comparisons" name="health_comparisons" value={customer.health_comparisons} onChange={update}/>
            <Field label="Life comparisons" name="life_comparisons" value={customer.life_comparisons} onChange={update}/>
            <Field label="Vehicle comparisons" name="vehicle_comparisons" value={customer.vehicle_comparisons} onChange={update}/>
            <Field label="General comparisons" name="general_comparisons" value={customer.general_comparisons} onChange={update}/>
          </div>

          <h3>Engagement signals</h3>
          <div className="grid">
            <Field label="Total sessions" name="total_sessions" value={customer.total_sessions} onChange={update}/>
            <Field label="Return visits" name="return_visits" value={customer.return_visits} onChange={update}/>
            <Field label="Quote requests" name="quote_requests" value={customer.quote_requests} onChange={update}/>
            <Field label="Callback requests" name="callback_requests" value={customer.callback_requests} onChange={update}/>
            <Field label="Chat count" name="chat_count" value={customer.chat_count} onChange={update}/>
            <Field label="Language" name="language" value={language} onChange={(e)=>setLanguage(e.target.value)} type="text" options={['English','Telugu','Hindi']}/>
          </div>

          <label className="message">
            <span>Customer message / conversation</span>
            <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="What did the customer say?"></textarea>
          </label>

          <button className="analyze" onClick={analyze} disabled={loading}>
            {loading ? 'Analyzing customer...' : 'Analyze & Assign Agent'}
          </button>

          {error && <div className="error">{error}</div>}
        </section>

        <section className="right">
          {!result ? (
            <div className="empty card">
              <div className="empty-icon">AI</div>
              <h2>Waiting for customer</h2>
              <p>Choose a scenario or enter customer behavior, then click <b>Analyze & Assign Agent</b>.</p>
              <div className="flow">
                <span>Customer</span><b>→</b><span>LR + DT + RF + KNN</span><b>→</b><span>Voting</span><b>→</b><span>Agent</span>
              </div>
            </div>
          ) : (
            <>
              <div className="card verdict">
                <div className="small-label">FINAL ROUTING</div>
                <div className="domain">{a.domain.toUpperCase()}</div>
                <p>Source: {a.domain_source}</p>
                <div className="metrics">
                  <div><span>Engagement</span><strong>{a.engagement}</strong></div>
                  <div><span>Purchase intent</span><strong>{a.purchase_intent}</strong></div>
                  <div><span>Complexity</span><strong>{a.complexity}</strong></div>
                  <div><span>Conversation intent</span><strong>{a.intent || 'No message'}</strong></div>
                  <div><span>Credit score</span><strong>{a.credit_score}</strong></div>
                  <div><span>Comparisons</span><strong>{a.comparison_count}</strong></div>
                </div>
              </div>

              <div className="card">
                <div className="card-title"><div><h2>Model confidence</h2><p>Output from the voting ensemble.</p></div></div>
                <div className="model-path">LR + DT + RF + KNN <b>→</b> soft voting aggregator</div>
                <h3>Insurance domain</h3>
                {Object.entries(a.domain_scores || {}).map(([k,v]) => <ScoreBar key={k} name={k} value={v}/>)}
                <div className="confidence-grid">
                  <div><span>Domain</span><b>{Math.round(a.domain_confidence*100)}%</b></div>
                  <div><span>Engagement</span><b>{Math.round(a.engagement_confidence*100)}%</b></div>
                  <div><span>Purchase</span><b>{Math.round(a.purchase_confidence*100)}%</b></div>
                  <div><span>Complexity</span><b>{Math.round(a.complexity_confidence*100)}%</b></div>
                </div>
              </div>

              <div className="card agent">
                <div className="small-label">ASSIGNMENT RESULT</div>
                {assignment.assigned ? (
                  <>
                    <div className="required-level">Required level: <b>{assignment.required_level}</b></div>
                    <h2>{assignment.agent.name}</h2>
                    <div className="role">{assignment.agent.role}</div>
                    <p>{assignment.reason}</p>
                    <div className="agent-details">
                      <div><span>Agent ID</span><b>{assignment.agent.agent_id}</b></div>
                      <div><span>Specialization</span><b>{assignment.agent.specialization}</b></div>
                      <div><span>Experience</span><b>{assignment.agent.experience_years} years</b></div>
                      <div><span>Languages</span><b>{assignment.agent.languages}</b></div>
                      <div><span>Availability</span><b>{assignment.agent.availability ? 'Available' : 'Unavailable'}</b></div>
                      <div><span>Workload</span><b>{assignment.agent.current_workload}</b></div>
                      <div><span>Match score</span><b>{assignment.agent.match_score}</b></div>
                    </div>
                  </>
                ) : (
                  <div className="error">No suitable agent available: {assignment.reason}</div>
                )}
              </div>

              <div className="card model-note">
                <div className="small-label">MODEL TRANSPARENCY</div>
                <p>{result.model_info?.algorithms?.join(' • ')} • {result.model_info?.voting}</p>
                <p>{result.model_info?.warning}</p>
              </div>

              <details className="card raw">
                <summary>View complete API response</summary>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </details>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
