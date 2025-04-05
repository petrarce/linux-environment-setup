#!/usr/bin/env python3

import argparse
from typing import Dict, Optional, Tuple
import ast
import unittest

def calculate_investment(
    initial_capital: float,
    top_up_map: Optional[Dict[int, float]] = None,
    interest_rate: float = 0.05,
    yearly_tax: float = 0.0,
    period: int = 1
) -> Tuple[float, float]:
    """Calculate investment growth with annual top-ups and interest tax."""
    top_up_map = top_up_map or {}
    current_balance = float(initial_capital)
    total_topped = 0.0
    total_interest = 0.0

    for year in range(1, period + 1):
        # Apply top-up at start of year
        if year in top_up_map:
            top_up = max(0.0, top_up_map[year] - current_balance)
            total_topped += top_up
            current_balance += top_up

        # Calculate and apply interest
        annual_interest = current_balance * interest_rate
        net_interest = annual_interest * (1 - yearly_tax)
        total_interest += net_interest
        current_balance += net_interest

    return (round(total_topped, 2), round(total_interest, 2))

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
            10000, {2: 15000}, 0.1, 0.0, 2
        )
        self.assertEqual(total_topped, 4000.0)
        self.assertEqual(total_interest, 2500.0)

    def test_top_up_not_needed(self):
        total_topped, total_interest = calculate_investment(
            10000, {1: 5000}, 0.1, 0.0, 1
        )
        self.assertEqual(total_topped, 0.0)
        self.assertEqual(total_interest, 1000.0)

    def test_with_tax(self):
        total_topped, total_interest = calculate_investment(
            1000, {}, 0.1, 0.2, 1
        )
        self.assertEqual(total_interest, 80.0)

    def test_zero_period(self):
        total_topped, total_interest = calculate_investment(
            1000, {}, 0.1, 0.0, 0
        )
        self.assertEqual(total_topped, 0.0)
        self.assertEqual(total_interest, 0.0)

if __name__ == '__main__':
    # Command line execution
    parser = argparse.ArgumentParser(
        description='Calculate investment growth with annual top-ups and interest tax'
    )
    parser.add_argument('--initial', type=float, required=True,
                        help='Initial investment capital')
    parser.add_argument('--top_up_map', type=str, default="{}",
                        help='Top up map as Python dict string (e.g. "{2: 5000}")')
    parser.add_argument('--rate', type=float, default=0.05,
                        help='Annual interest rate (default: 0.05)')
    parser.add_argument('--tax', type=float, default=0.0,
                        help='Yearly tax rate on interest (default: 0.0)')
    parser.add_argument('--period', type=int, required=True,
                        help='Investment period in years')

    try:
        args = parser.parse_args()
        top_up_dict = ast.literal_eval(args.top_up_map)
        if not isinstance(top_up_dict, dict):
            raise ValueError("Invalid top_up_map format")
            
        total_topped, total_interest = calculate_investment(
            args.initial,
            top_up_dict,
            args.rate,
            args.tax,
            args.period
        )

        print(f"Total topped up: ${total_topped:.2f}")
        print(f"Interest accumulated: ${total_interest:.2f}")
        print(f"Final balance: ${(args.initial + total_topped + total_interest):.2f}")
        
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing input: {str(e)}")
    except Exception as e:
        print(f"Calculation error: {str(e)}")
