import unittest
import tempfile
import os
import json
from ..CreditCalculator import calculate_credit, calculate_multiple_credits

class TestCreditCalculator(unittest.TestCase):
    def test_normal_case(self):
        """Test normal case with valid inputs"""
        repayment_map = {y: 10000 for y in range(1, 11)}
        yearly_rates, total_paid, unused = calculate_credit(0.05, 100000, 10, repayment_map)
        self.assertEqual(len(yearly_rates), 5)
        self.assertAlmostEqual(yearly_rates[1][0], 1250.0, places=2)
        self.assertAlmostEqual(total_paid, 115000.00, places=2)
        self.assertAlmostEqual(unused, 50000.00, places=2)  # Years 6-10 repayments unused

    def test_zero_interest(self):
        """Test with zero interest rate"""
        yearly_rates, total_paid, _ = calculate_credit(0.0, 100000, 5, {})
        self.assertEqual(len(yearly_rates), 5)
        self.assertAlmostEqual(yearly_rates[1][0], 1666.67, places=2)
        self.assertAlmostEqual(yearly_rates[5][0], 1666.67, places=2)
        self.assertAlmostEqual(total_paid, 100000.00, places=2)

    def test_full_early_repayment(self):
        """Test when repayments pay off loan early"""
        yearly_rates, total_paid, unused = calculate_credit(
            0.1,
            100000,
            10,
            {1: 100000})
        self.assertEqual(len(yearly_rates), 1)
        self.assertAlmostEqual(total_paid, 110000.00, places=2)
        self.assertAlmostEqual(unused, 10000, places=2)  # Full repayment used

    def test_invalid_interest_rate(self):
        """Test invalid interest rate (negative)"""
        with self.assertRaises(ValueError):
            calculate_credit(
                -0.1,
                100000,
                10,
                {1: 10000, 2: 10000, 3: 10000, 4: 10000, 5: 10000, 6: 10000, 7: 10000, 8: 10000, 9: 10000, 10: 10000})

    def test_invalid_interest_rate_high(self):
        """Test invalid interest rate (>1)"""
        with self.assertRaises(ValueError):
            calculate_credit(1.1, 100000, 10, {1: 10000, 2: 10000, 3: 10000, 4: 10000, 5: 10000, 6: 10000, 7: 10000, 8: 10000, 9: 10000, 10: 10000})

    def test_invalid_loan_amount(self):
        """Test invalid loan amount (negative)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, -100000, 10, {1: 10000, 2: 10000, 3: 10000, 4: 10000, 5: 10000, 6: 10000, 7: 10000, 8: 10000, 9: 10000, 10: 10000})

    def test_invalid_loan_period(self):
        """Test invalid loan period (zero)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 0, {1: 10000, 2: 10000, 3: 10000, 4: 10000, 5: 10000, 6: 10000, 7: 10000, 8: 10000, 9: 10000, 10: 10000})

    def test_invalid_partial_repayment(self):
        """Test invalid partial repayment (negative)"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 10, {1: -10000, 2: -10000, 3: 10000, 4: -10000, 5: 10000, 6: 10000, 7: 10000, 8: 10000, 9: 10000, 10: 10000})

    def test_invalid_partial_repayment_high(self):
        """Test invalid partial repayment (>1)"""
        yearly_rates, total, unused = calculate_credit(0.05, 100000, 10, {1: 110000})
        self.assertAlmostEqual(unused, 20000, 2)
        self.assertAlmostEqual(total, 105000, 2)


    def test_partial_repayment_period(self):
        """Test partial repayment every 2 years"""
        yearly_rates, total_paid, _ = calculate_credit(
            interest_rate=0.05,
            total_loan=100000,
            loan_period=10,
            repayment_map={2: 10000, 4: 10000, 6: 10000, 8: 10000, 10: 10000}
        )
        
        self.assertEqual(len(yearly_rates), 7)  # Should finish in 7 years
        self.assertAlmostEqual(yearly_rates[1][0], 1250.00, places=2)
        self.assertAlmostEqual(yearly_rates[3][0], 1125.00, places=2)  # Year 3 payment
        self.assertAlmostEqual(yearly_rates[3][1], 60000.00, places=2)
        self.assertAlmostEqual(yearly_rates[7][1], 0.00, places=2)
        self.assertAlmostEqual(total_paid, 120000, places=2)

    def test_multiple_credits(self):
        """Test aggregation of multiple credits"""
        config = [
            {
                "loan_amount": 100000,
                "period": 2,
                "interest_rate": 0.1,
                "start_year": 2024
            },
            {
                "loan_amount": 50000,
                "period": 2,
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

    def test_redirected_credit(self):
        """Test that redirected credits subtract their loan amount from total"""
        config_json = '[                        \
            {                                   \
                "loan_amount": 100000,          \
                "period": 2,                    \
                "interest_rate": 0.1,           \
                "start_year": 2024,             \
                "repayment_map": { "1" : 50000 }\
            },                                  \
            {                                   \
                "loan_amount": 50000,           \
                "period": 2,                    \
                "interest_rate": 0.0,           \
                "start_year": 2025,             \
                "redirected": true              \
            }                                   \
        ]'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(config_json)
            temp_path = f.name
        
        try:
            payments, total = calculate_multiple_credits(temp_path)
            
            # First credit: 100000 @10% over first year with partial repayments after 1-st year: { 1: 50000 }.
            # Second credit: 50000 redirected (subtracted from total)
            # Second credit payments: 50000 @0% over 2 years (total paid = 50000)
            # Final total should be 110000 - 50000 + 50000 = 110000
            self.assertAlmostEqual(total, 110000.00, places=2)
        finally:
            os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
    def test_invalid_repayment_map(self):
        """Test invalid repayment map types"""
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 10, repayment_map=["invalid"])
        with self.assertRaises(ValueError):
            calculate_credit(0.05, 100000, 10, repayment_map={1: -100})
