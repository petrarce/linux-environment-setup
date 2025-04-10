
#!/usr/bin/env python3
import sys
import argparse
import json
from collections import defaultdict
from typing import Dict

def calculate_credit(interest_rate, total_loan, loan_period, repayment_map: Dict[int, float] | None = None):
    """
    Calculate the monthly rate for each year of a loan.

    Args:
        interest_rate (float): Annual interest rate (0-1)
        total_loan (float): Total loan amount (>0)
        loan_period (int): Loan period in years (>0)
        repayment_map (dict): Optional year-to-repayment mapping {year: amount}

    Returns:
        tuple: (
            dict: {year: (monthly_rate, remaining_loan)},
            float: Total paid,
            float: Unused repayments
        )
    """
    if not (0 <= interest_rate <= 1):
        raise ValueError("Interest rate must be between 0 and 1")
    if total_loan <= 0:
        raise ValueError("Total loan amount must be greater than 0")
    if loan_period <= 0:
        raise ValueError("Loan period must be greater than 0")
    if not isinstance(repayment_map, dict):
        raise ValueError("repayment_map must be a dictionary")
    for amount in repayment_map.values():
        if amount < 0:
            raise ValueError("Repayment amounts must be ≥0")

    yearly_repaiment_amount = total_loan / loan_period
    remaining_loan = total_loan
    yearly_rates = {}
    total_paid = 0.0
    total_unused = 0.0
    last_year = loan_period  # Default if full period completes

    for year in range(1, loan_period + 1):
        # Calculate base payments
        monthly_payment = (remaining_loan * interest_rate + min(remaining_loan, yearly_repaiment_amount)) / 12
        annual_payment = monthly_payment * 12
        remaining_at_start = remaining_loan
        remaining_loan = max(0, remaining_loan - yearly_repaiment_amount)
        total_paid += annual_payment

        # Process scheduled repayment if exists
        if repayment_map is not None and year in repayment_map:
            scheduled = repayment_map[year]
            actual = min(scheduled, remaining_loan)
            remaining_loan -= actual
            total_paid += actual
            total_unused += scheduled - actual

        yearly_rates[year] = (monthly_payment, remaining_at_start)
        
        if remaining_loan == 0:
            last_year = year
            break

    # Add unused repayments from future years
    for y in repayment_map:
        if y > last_year:
            total_unused += repayment_map[y]

    return yearly_rates, round(total_paid, 2), round(total_unused, 2)

def calculate_multiple_credits(config_file):
    """
    Calculate combined monthly payments across multiple credits from a JSON config.
    
    Args:
        config_file (str): Path to JSON file containing credit configurations
        
    Returns:
        tuple: (
            dict: Aggregated monthly payments by calendar year,
            dict: Aggregated remaining to pay by calendar year
            float: Total paid across all credits
        )
    """
    with open(config_file) as f:
        credits = json.load(f)

    aggregated_payments = defaultdict(float)
    aggregated_remaining = defaultdict(float)
    total_paid_all = 0.0

    for credit in credits:
        # Calculate individual credit
        loan_amount = credit['loan_amount']
        yearly_rates, total_paid, _ = calculate_credit(
            interest_rate=credit['interest_rate'],
            total_loan=loan_amount,
            loan_period=credit['period'],
            repayment_map={int(k): v for k, v in credit.get('repayment_map', {}).items()}
        )

        # Offset payments by start year
        start_year = credit['start_year']
        for credit_year, monthly_data in yearly_rates.items():
            calendar_year = start_year + credit_year - 1
            aggregated_payments[calendar_year] += monthly_data[0]  # Access first element
            aggregated_remaining[calendar_year] += monthly_data[1]

        # Handle redirected credits by subtracting their loan amount
        if credit.get('redirected', False):
            total_paid_all -= loan_amount
        total_paid_all += total_paid

    # Convert defaultdict to regular dict and sort
    ordered_payments = dict(sorted(aggregated_payments.items()))
    ordered_left_total = dict(sorted(aggregated_remaining.items()))
    return ordered_payments, ordered_left_total, round(total_paid_all, 2)

def _main():
    """
		Command-line interface to calculate the monthly rate for each year of a loan.

		Parses command-line arguments and calls the `calculate_credit` function with provided parameters.
		Prints the result or error messages if inputs are invalid.
		"""
    parser = argparse.ArgumentParser(description="Calculate the monthly rate for each year of a loan.")

    # Add subparsers for different credit types
    subparsers = parser.add_subparsers(description="valid subcommands: single, multi")
    multi = subparsers.add_parser('multi')
    single = subparsers.add_parser('single')

    # Configure multi subparser arguments
    multi.add_argument("--config", type=str,
                       help="Path to JSON config file for multiple credits", required=True)

    # Configure single subparser arguments
    single.add_argument("--interest-rate", type=float, required=True, help="Interest rate as float (0-1)")
    single.add_argument("--total-loan", type=float, required=True, help="Total loan amount as float (>0)")
    single.add_argument("--loan-period", type=int, required=True, help="Loan period in years (>0)")
    single.add_argument("--repayment-map", type=str, default="{}",
                        help='JSON string of repayment schedule (e.g. \'{"2": 20000, "5": 10000}\')')

    args = parser.parse_args()

    if hasattr(args, "config"):
        try:
            yearly_payments, left_total, total = calculate_multiple_credits(args.config)
            for year, rate in yearly_payments.items():
                print(f"Year {year}: Remaining Loan: {left_total[year]}, Combined Monthly Rate = {rate:.2f}")
            print(f"Total Paid Across All Credits: {total:.2f}")
        except Exception as e:
            print(f"Config error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            # Parse repayment map from JSON string
            repayment_map = json.loads(args.repayment_map.replace("'", "\""))
            repayment_map = {int(k): v for k, v in repayment_map.items()}

            yearly_rates, total_paid, unused = calculate_credit(
                interest_rate=args.interest_rate,
                total_loan=args.total_loan,
                loan_period=args.loan_period,
                repayment_map=repayment_map
            )

            for year, rate_data in yearly_rates.items():
                print(f"Year {year}: Remaining Loan = {rate_data[1]:.2f}, Monthly Rate = {rate_data[0]:.2f}")
            print(f"Total Paid Over Loan Period: {total_paid:.2f}")
            print(f"Unused Repayment Capacity: {unused:.2f}")

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    _main()
