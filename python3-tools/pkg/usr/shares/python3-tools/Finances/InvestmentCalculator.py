#!/usr/bin/env python3

import argparse
from typing import Dict, Optional, Tuple
import json



def calculate_investment(
    initial_capital: float,
    top_up_map: Optional[Dict[int | str, float | Tuple[int, float]]] = None,
    interest_rate: float = 0.05,
    yearly_tax: float = 0.0,
    length: int = 1
) -> Tuple[float, float]:
    """Calculate investment growth with annual top-ups and interest tax."""
    top_up_map = top_up_map or {}
    current_balance = float(initial_capital)
    total_topped = 0.0
    total_interest = 0.0

    # Validate input parameters
    if initial_capital < 0:
        raise ValueError("Initial capital cannot be negative")
    if interest_rate < 0:
        raise ValueError("Interest rate less then 0")
    if yearly_tax < 0 or yearly_tax > 1:
        raise ValueError("Yearly tax rate must be between 0 and 1")
    if length < 1:
        raise ValueError("Investment period must be at least 1 year")

    repeated_topups = {} #repeated topups
    # Validate top-up map contents
    for first, second in top_up_map.items():
        if type(first) is int:
            year, amount = (first, second)
            if year < 0 or year >= length:
                raise ValueError(f"Top-up year {year} must be within investment period (0 - {period}-1)")
            if amount < 0:
                raise ValueError(f"Top-up amount for year {year} cannot be negative")
        elif first == 'repeat':
            period, amount =  second
            if period < 1:
                raise ValueError(f"period should be >1")
            if amount < 0:
                raise ValueError(f"amount should be >0")

            if repeated_topups.get(period) is None:
                repeated_topups[period] = 0
            repeated_topups[period] += amount
        else:
            raise ValueError("Top up is either year:amount pair or 'repeat': { period : amount }")

    for year in range(0, length):
        # Apply top-up at start of year
        if year in top_up_map:
            top_up = top_up_map[year]
            total_topped += top_up
            current_balance += top_up

        for period, top_up in repeated_topups.items():
            if ((year + 1) % period) == 0:
                total_topped += top_up
                current_balance += top_up

        # Calculate and apply interest
        annual_interest = current_balance * interest_rate
        net_interest = annual_interest * (1 - yearly_tax)
        total_interest += net_interest
        current_balance += net_interest

    return round(total_topped, 2), round(total_interest, 2)

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
        top_up_dict_non_converted = json.loads(args.top_up_map.replace("'", "\""))
        top_up_dict: Dict[int | str, float | Tuple[int, float]] = {}
        for key, value in top_up_dict_non_converted.items():
            if key != 'repeat':
                top_up_dict[int(key)] = float(value)
            else:
                period, top_up = value['period'], value['amount']
                top_up_dict[str(key)] = period, top_up

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
