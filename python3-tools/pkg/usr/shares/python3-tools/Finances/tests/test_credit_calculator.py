import unittest
from ..CreditCalculator import calculate_credit

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

if __name__ == '__main__':
    unittest.main()
