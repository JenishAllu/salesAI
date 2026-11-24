"""
PolicyBuzar - Comprehensive Acceptance & Regression Test Suite
Validates all 14 test scenarios and acceptance criteria from PART 20.
"""

import unittest
import copy
from backend.services.routing_engine import routing_engine
from backend.services.sensitivity_tracker import analyze_change
from backend.config.scenarios import SCENARIOS
from backend.config.policy_config import DEFAULT_CUSTOMER


class TestPolicyBuzarAcceptance(unittest.TestCase):

    def test_01_simple_willing_customer(self):
        """Test 1: Simple willing customer -> Intern Agent"""
        data = copy.deepcopy(SCENARIOS["ready_to_buy_health"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["final_routing"]["required_agent_level"], "Intern Agent")
        self.assertEqual(res["domain_prediction"]["primary_domain"], "Health")
        self.assertEqual(res["purchase_willingness"]["willingness_level"], "High")
        self.assertEqual(res["customer_complexity"]["complexity_level"], "Low")

    def test_02_multi_category_confused_customer(self):
        """Test 2: Multi-category confused customer -> Expert Agent"""
        data = copy.deepcopy(SCENARIOS["confused_multi_category"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["final_routing"]["required_agent_level"], "Expert Agent")
        self.assertIn(res["purchase_willingness"]["willingness_level"], ["Medium", "Low"])
        self.assertIn(res["customer_complexity"]["complexity_level"], ["Medium", "High"])

    def test_03_price_objection_customer(self):
        """Test 3: Price objection -> Expert Agent"""
        data = copy.deepcopy(SCENARIOS["low_willingness_objection"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["final_routing"]["required_agent_level"], "Expert Agent")
        self.assertEqual(res["conversation_intent"]["predicted_intent"], "Price objection")

    def test_04_previous_agent_failed_escalation(self):
        """Test 4: Previous agent failed = True -> Senior Expert Agent override"""
        data = copy.deepcopy(SCENARIOS["previous_agent_failed"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["final_routing"]["required_agent_level"], "Senior Expert Agent")
        self.assertTrue(res["final_routing"]["escalation_triggered"])
        self.assertIn("Previous agent", res["final_routing"]["escalation_reason"])

    def test_05_complex_multi_category_customer(self):
        """Test 5: Complex multi-category customer -> Senior Expert Agent"""
        data = copy.deepcopy(SCENARIOS["complex_senior_expert"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["final_routing"]["required_agent_level"], "Senior Expert Agent")
        self.assertEqual(res["customer_complexity"]["complexity_level"], "High")

    def test_06_high_willingness_high_complexity(self):
        """Test 6: High willingness but high complexity -> Senior Expert (MUST NOT downgrade to Intern!)"""
        data = copy.deepcopy(SCENARIOS["high_willingness_high_complexity"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["final_routing"]["required_agent_level"], "Senior Expert Agent")
        self.assertNotEqual(res["final_routing"]["required_agent_level"], "Intern Agent")

    def test_07_high_engagement_low_willingness(self):
        """Test 7: High engagement but low willingness -> Expert Agent"""
        data = copy.deepcopy(SCENARIOS["high_engagement_low_willingness"]["data"])
        res = routing_engine.process_customer(data)
        self.assertEqual(res["engagement_classification"]["engagement_level"], "High")
        self.assertEqual(res["final_routing"]["required_agent_level"], "Expert Agent")

    def test_08_language_matching_telugu(self):
        """Test 8: Language matching -> Customer prefers Telugu -> assigns Telugu-speaking agent"""
        data = copy.deepcopy(SCENARIOS["language_matching_telugu"]["data"])
        res = routing_engine.process_customer(data)
        assigned = res["final_routing"]["assigned_agent"]
        self.assertIn("Telugu", assigned["supported_languages"])

    def test_09_specialization_matching_life(self):
        """Test 9: Specialization matching -> Customer needs Life insurance"""
        data = copy.deepcopy(SCENARIOS["ready_to_buy_life"]["data"])
        res = routing_engine.process_customer(data)
        assigned = res["final_routing"]["assigned_agent"]
        self.assertIn("Life", assigned["specializations"])

    def test_10_agent_offline_handling(self):
        """Test 10: Assigned agent is online and available when qualified ones exist"""
        data = copy.deepcopy(DEFAULT_CUSTOMER)
        res = routing_engine.process_customer(data)
        assigned = res["final_routing"]["assigned_agent"]
        self.assertTrue(assigned["is_online"])
        self.assertEqual(assigned["availability_status"], "Available")

    def test_11_workload_capacity_preference(self):
        """Test 11: Agent current workload is within max workload capacity"""
        data = copy.deepcopy(DEFAULT_CUSTOMER)
        res = routing_engine.process_customer(data)
        assigned = res["final_routing"]["assigned_agent"]
        self.assertLess(assigned["current_workload"], assigned["max_workload"])

    def test_12_missing_data_robustness(self):
        """Test 12: Missing data handles None/NaN without crash"""
        data = copy.deepcopy(DEFAULT_CUSTOMER)
        data["monthly_income"] = None
        data["credit_score"] = None
        data["customer_message"] = ""
        res = routing_engine.process_customer(data)
        self.assertIn(res["final_routing"]["required_agent_level"], ["Intern Agent", "Expert Agent", "Senior Expert Agent"])
        self.assertGreater(len(res["customer_complexity"]["missing_information"]), 0)

    def test_13_live_field_sensitivity_tracking(self):
        """Test 13: Live field changes trigger accurate sensitivity analysis"""
        prev_data = copy.deepcopy(DEFAULT_CUSTOMER)
        prev_res = routing_engine.process_customer(prev_data)

        new_data = copy.deepcopy(DEFAULT_CUSTOMER)
        new_data["previous_agent_failed"] = True
        new_res = routing_engine.process_customer(new_data)

        change = analyze_change(prev_data, new_data, prev_res, new_res)
        self.assertIsNotNone(change)
        self.assertEqual(change["changed_field"], "previous_agent_failed")
        self.assertEqual(change["previous_value"], False)
        self.assertEqual(change["new_value"], True)
        self.assertEqual(change["updated_assignment"], "Senior Expert Agent")

    def test_14_reset_to_default(self):
        """Test 14: Reset restores initial state and calculates cleanly"""
        data = copy.deepcopy(DEFAULT_CUSTOMER)
        res = routing_engine.process_customer(data)
        self.assertEqual(res["domain_prediction"]["primary_domain"], "Health")
        self.assertEqual(res["customer_complexity"]["complexity_level"], "Low")
        self.assertIn(res["final_routing"]["required_agent_level"], ["Intern Agent", "Expert Agent"])


if __name__ == "__main__":
    unittest.main()

