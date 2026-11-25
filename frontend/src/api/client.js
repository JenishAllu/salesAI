/**
 * PolicyBuzar API Client
 * Manages debounced live prediction requests with sequence ID checking
 * and AbortController to prevent stale responses from overwriting newer predictions.
 */

const API_BASE = '/api';

let currentRequestId = 0;
let abortController = null;

export async function predictCustomer(customer, previousCustomer = null, previousPrediction = null) {
  currentRequestId += 1;
  const requestId = currentRequestId;

  if (abortController) {
    abortController.abort();
  }
  abortController = new AbortController();

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        customer,
        previous_customer: previousCustomer,
        previous_prediction: previousPrediction
      }),
      signal: abortController.signal
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const json = await res.json();
    if (requestId === currentRequestId) {
      return json.data;
    }
    return null; // Stale response discarded
  } catch (err) {
    if (err.name === 'AbortError') {
      return null; // Aborted cleanly
    }
    console.error('Prediction API error:', err);
    throw err;
  }
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error('Failed to load scenarios');
  const json = await res.json();
  return json.scenarios;
}

export async function fetchModelMetrics() {
  const res = await fetch(`${API_BASE}/model-metrics`);
  if (!res.ok) throw new Error('Failed to load model metrics');
  const json = await res.json();
  return json.metrics;
}

export async function fetchDatasetSummary() {
  const res = await fetch(`${API_BASE}/dataset/summary`);
  if (!res.ok) throw new Error('Failed to load dataset summary');
  const json = await res.json();
  return json.summary;
}

export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  if (!res.ok) throw new Error('Failed to load agents');
  const json = await res.json();
  return json.agents;
}

export async function fetchAgentHistory(agentId) {
  const res = await fetch(`${API_BASE}/agents/${agentId}/history`);
  if (!res.ok) throw new Error(`Failed to load history for agent ${agentId}`);
  return await res.json();
}

export async function submitAgentOutcome(agentId, caseId, outcome, notes = '') {
  const res = await fetch(`${API_BASE}/agents/${agentId}/outcome`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, outcome, notes })
  });
  if (!res.ok) throw new Error(`Failed to update outcome for case ${caseId}`);
  return await res.json();
}

export async function submitFeedback(feedback) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback)
  });
  if (!res.ok) throw new Error('Failed to submit feedback');
  return await res.json();
}

