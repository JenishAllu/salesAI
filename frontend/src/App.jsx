import React, { useState, useEffect, useRef, useCallback } from 'react';
import Navbar from './components/Navbar';
import ScenarioBar from './components/ScenarioBar';
import SensitivityPanel from './components/SensitivityPanel';
import CustomerForm from './components/CustomerForm';
import DomainCard from './components/cards/DomainCard';
import EngagementCard from './components/cards/EngagementCard';
import WillingnessCard from './components/cards/WillingnessCard';
import ComplexityCard from './components/cards/ComplexityCard';
import RoutingCard from './components/cards/RoutingCard';
import ModelConfidenceCard from './components/cards/ModelConfidenceCard';
import AgentRosterModal from './components/AgentRosterModal';
import MetricsModal from './components/MetricsModal';

import { DEFAULT_CUSTOMER, SCENARIO_LIST } from './data/scenarios';
import {
  predictCustomer,
  fetchModelMetrics,
  fetchDatasetSummary,
  fetchAgents
} from './api/client';

export default function App() {
  const [customer, setCustomer] = useState(DEFAULT_CUSTOMER);
  const [activeScenarioId, setActiveScenarioId] = useState(null);

  // Prediction outputs state
  const [predictionData, setPredictionData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Modals state
  const [isAgentsOpen, setIsAgentsOpen] = useState(false);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

  // Aux data
  const [agents, setAgents] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [datasetSummary, setDatasetSummary] = useState({});

  // History tracking for sensitivity analysis
  const previousCustomerRef = useRef(null);
  const previousPredictionRef = useRef(null);
  const debounceTimerRef = useRef(null);

  // Fetch initial aux data
  useEffect(() => {
    fetchAgents()
      .then((data) => setAgents(data))
      .catch((err) => console.warn('Could not load agents:', err));

    fetchModelMetrics()
      .then((data) => setMetrics(data))
      .catch((err) => console.warn('Could not load metrics:', err));

    fetchDatasetSummary()
      .then((data) => setDatasetSummary(data))
      .catch((err) => console.warn('Could not load dataset summary:', err));
  }, []);

  // Main calculation trigger
  const runPrediction = useCallback(async (currentCust, prevCust, prevPred) => {
    setIsLoading(true);
    setError(null);

    try {
      const res = await predictCustomer(currentCust, prevCust, prevPred);
      if (res) {
        setPredictionData(res);
        previousPredictionRef.current = res;
      }
    } catch (err) {
      console.error('Error during prediction:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial calculation on mount
  useEffect(() => {
    runPrediction(DEFAULT_CUSTOMER, null, null);
    previousCustomerRef.current = DEFAULT_CUSTOMER;
  }, [runPrediction]);

  // Handle controlled input changes with debouncing
  const handleFieldChange = (fieldName, value) => {
    setActiveScenarioId(null); // Clear preset highlight on custom edit

    setCustomer((prev) => {
      const updated = { ...prev, [fieldName]: value };

      // Cancel previous debounce timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      // Fast immediate dispatch for switches, selects, or short debounce for numbers/text
      const immediateFields = ['selected_category', 'previous_agent_failed', 'existing_policy', 'marital_status', 'language'];
      const delay = immediateFields.includes(fieldName) ? 30 : 250;

      debounceTimerRef.current = setTimeout(() => {
        runPrediction(updated, previousCustomerRef.current, previousPredictionRef.current);
        previousCustomerRef.current = updated;
      }, delay);

      return updated;
    });
  };

  // Scenario selection
  const handleSelectScenario = (scenario) => {
    setActiveScenarioId(scenario.id);
    const newCust = { ...DEFAULT_CUSTOMER, ...scenario.data };
    setCustomer(newCust);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    runPrediction(newCust, previousCustomerRef.current, previousPredictionRef.current);
    previousCustomerRef.current = newCust;
  };

  // Reset to initial default customer state
  const handleReset = () => {
    setActiveScenarioId(null);
    setCustomer(DEFAULT_CUSTOMER);
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    runPrediction(DEFAULT_CUSTOMER, customer, predictionData);
    previousCustomerRef.current = DEFAULT_CUSTOMER;
  };

  // Manual Recalculate fallback button
  const handleRecalculate = () => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    runPrediction(customer, previousCustomerRef.current, previousPredictionRef.current);
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <Navbar
        isLoading={isLoading}
        onRecalculate={handleRecalculate}
        onReset={handleReset}
        onOpenAgents={() => setIsAgentsOpen(true)}
        onOpenMetrics={() => setIsMetricsOpen(true)}
        agentCount={agents.length}
      />

      {/* 10 Quick Scenario Demo Chips */}
      <ScenarioBar
        activeScenarioId={activeScenarioId}
        onSelectScenario={handleSelectScenario}
      />

      {/* Main Grid: Left = Inputs, Right = 5 Output Cards + Model Confidence + Sensitivity */}
      <div className="dashboard-grid">
        {/* Left Column: Form Controls */}
        <div>
          <CustomerForm values={customer} onChange={handleFieldChange} />
        </div>

        {/* Right Column: Dynamic Outputs */}
        <div className="outputs-panel">
          {/* Real-Time Sensitivity Banner ("Why did assignment change?") */}
          {predictionData?.sensitivity_analysis && (
            <SensitivityPanel sensitivity={predictionData.sensitivity_analysis} />
          )}

          {error && (
            <div style={{ background: '#7f1d1d', border: '1px solid #dc2626', padding: '0.75rem 1rem', borderRadius: '8px', color: '#fecaca', fontSize: '0.82rem' }}>
              <strong>API Error:</strong> {error}
            </div>
          )}

          {/* 5 Outputs Grid */}
          <div className="cards-grid">
            {/* Card 1: Domain */}
            <DomainCard data={predictionData?.domain_prediction} />

            {/* Card 2: Engagement */}
            <EngagementCard data={predictionData?.engagement_classification} />

            {/* Card 3: Purchase Willingness */}
            <WillingnessCard data={predictionData?.purchase_willingness} />

            {/* Card 4: Customer Complexity */}
            <ComplexityCard data={predictionData?.customer_complexity} />

            {/* Card 5: Final Routing & Intelligent Agent Allocation */}
            <RoutingCard data={predictionData?.final_routing} />

            {/* Card 6: Multi-Model Confidence (LR, DT, RF, KNN, Ensemble) */}
            <ModelConfidenceCard data={predictionData} />
          </div>
        </div>
      </div>

      {/* Modals */}
      <AgentRosterModal
        isOpen={isAgentsOpen}
        onClose={() => setIsAgentsOpen(false)}
        agents={agents}
      />

      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
        metrics={metrics}
        datasetSummary={datasetSummary}
      />
    </div>
  );
}

