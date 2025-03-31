import unittest
import tempfile
import os
import json
from ..CreditCalculator import calculate_credit, calculate_multiple_credits

class TestCreditCalculator(unittest.TestCase):
    def test_normal_case(self):
        """Test normal case with valid inputs"""
        yearly_rates, total_paid = calculate_credit(0.05, 100000, 10, 0.1)
        self.assertEqual(len(yearly_rates), 5)
        self.assertAlmostEqual(yearly_rates[1], 1250.0, places=2)
        self.assertAlmostEqual(yearly_rates[5], 916.67, places=2)
        self.assertAlmostEqual(total_paid, 115000.00, places=2)

    def test_zero_interest(self):
        """Test with zero interest rate"""
        yearly_rates, total_paid = calculate_credit(0.0, 100000, 5, 0.0)
        self.assertEqual(len(yearly_rates), 5)
        self.assertAlmostEqual(yearly_rates[1], 1666.67, places=2)
        self.assertAlmostEqual(yearly_rates[5], 1666.67, places=2)
        self.assertAlmostEqual(total_paid, 100000.00, places=2)

    def test_full_early_repayment(self):
        """Test when partial repayments pay off loan early"""
        yearly_rates, total_paid = calculate_credit(0.1, 100000, 10, 1.0)
        self.assertEqual(len(yearly_rates), 1)
        self.assertAlmostEqual(yearly_rates[1], 1666.67, places=2)
        self.assertAlmostEqual(total_paid, 120000.00, places=2)

    def test_invalid_interest_rate(self):
        """Test invalid interest rate (negative)"""
        with self.assertRaises(ValueError):
            calculate_credit(-0.1, 100000, 10, 0.1)

    def test_invalid_interest_rate_high(self):
        """Test invalid interest rate (>1)"""
        with self.assertRaises(ValueError):
            calculate_credit(1.1, 100000, 10, 0.1)

    def test_invalid_loan_amount(self):
        """Test invalid loan amount (negative)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, -100000, 10, 0.1)

    def test_invalid_loan_period(self):
        """Test invalid loan period (zero)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 0, 0.1)

    def test_invalid_partial_repayment(self):
        """Test invalid partial repayment (negative)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 10, -0.1)

    def test_invalid_partial_repayment_high(self):
        """Test invalid partial repayment (>1)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 10, 1.1)

    def test_multiple_credits(self):
        """Test aggregation of multiple credits"""
        config = [
            {
                "loan_amount": 100000,
                "period": 2,
                "partial_repayments": 0.0,
                "interest_rate": 0.1,
                "start_year": 2024
            },
            {
                "loan_amount": 50000,
                "period": 2,
                "partial_repayments": 0.0,
                "interest_rate": 0.0,
                "start_year": 2025
            }
        ]
        
        # Save temp config
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            payments, total = calculate_multiple_credits(temp_path)
            
            # Test aggregated payments
            self.assertAlmostEqual(payments[2024], 5000, places=1)  # 100000 @10%
            self.assertAlmostEqual(payments[2025], 4583.33 + 2083.33, places=1)  # Both credits
            self.assertAlmostEqual(payments[2026], 2083.33, places=1)  # Second credit only
            self.assertAlmostEqual(total, 115000.00 + 50000.00, places=1)
        finally:
            os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
