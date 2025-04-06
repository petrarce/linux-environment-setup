import unittest
from ..InvestmentCalculator import calculate_investment

class TestCalculateInvestment(unittest.TestCase):
    """Unit tests for investment calculator."""

    def test_no_top_up_no_tax(self):
        total_topped, total_interest = calculate_investment(
            1000, {}, 0.1, 0.0, 1
        )
        self.assertEqual(total_topped, 0.0)
        self.assertEqual(total_interest, 100.0)

    def test_with_top_up(self):
        total_topped, total_interest = calculate_investment(
            10000, {1: 15000}, 0.1, 0.0, 2
        )
        self.assertEqual(total_topped, 15000.0)
        self.assertEqual(total_interest, 1000 + 1100 + 1500)

    def test_top_up_not_needed(self):
        total_topped, total_interest = calculate_investment(
            10000, {1: 5000}, 0.1, 0.0, 1
        )
        self.assertEqual(total_topped, 0.0)
        self.assertEqual(total_interest, 1000.0)

    def test_with_tax(self):
        total_topped, total_interest = calculate_investment(
            1000,
            {},
            1,
            0.5,
            3)
        self.assertEqual(total_interest, 1000 * 0.5 + 1500 * 0.5 + 2250 * 0.5)

    def test_zero_period(self):
        total_topped, total_interest = calculate_investment(
            1000, {}, 0.1, 0.0, 0
        )
        self.assertEqual(total_topped, 0.0)
        self.assertEqual(total_interest, 0.0)


if __name__ == "__main__":
    unittest.main()