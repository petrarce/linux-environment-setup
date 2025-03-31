
#!/usr/bin/env python3
import sys
import argparse
import json
from collections import defaultdict

def calculate_credit(interest_rate, total_loan, loan_period, partial_repayments, partial_repayments_period=1):
    """
    Calculate the monthly rate for each year of a loan.

    Args:
        interest_rate (float): Annual interest rate (0-1)
        total_loan (float): Total loan amount (>0)
        loan_period (int): Loan period in years (>0)
        partial_repayments (float): Partial repayment percentage (0-1)
        partial_repayments_period (int): Years between partial repayments (≥1)

    Returns:
        dict: A dictionary where keys are the years and values are the monthly rates for each year.

    Raises:
        ValueError: If any of the input parameters are invalid.
    """
    if not (0 <= interest_rate <= 1):
        raise ValueError("Interest rate must be between 0 and 1")
    if total_loan <= 0:
        raise ValueError("Total loan amount must be greater than 0")
    if loan_period <= 0:
        raise ValueError("Loan period must be greater than 0")
    if not (0 <= partial_repayments <= 1):
        raise ValueError("Partial repayments must be between 0 and 1")
    if partial_repayments_period < 1:
        raise ValueError("Partial repayment period must be ≥1")

    yearly_repaiment_amount = total_loan / loan_period
    remaining_loan = total_loan
    yearly_rates = {}
    total_paid = 0.0

    for year in range(1, loan_period + 1):
        # Calculate the payments and remaining loan not including the partial repayment
        monthly_payment = (remaining_loan * interest_rate + min(remaining_loan, yearly_repaiment_amount)) / 12
        annual_payment = monthly_payment * 12
        remaining_loan = max(0, remaining_loan - yearly_repaiment_amount)

        # Calculate the remaining loan including the partial repayment
        partial_payment = min(remaining_loan, total_loan * partial_repayments) \
            if year % partial_repayments_period == 0 \
            else 0.0

        total_paid += annual_payment + partial_payment
        remaining_loan -= partial_payment
        yearly_rates[year] = monthly_payment
        if remaining_loan == 0:
            break

    return yearly_rates, round(total_paid, 2)

def calculate_multiple_credits(config_file):
    """
    Calculate combined monthly payments across multiple credits from a JSON config.
    
    Args:
        config_file (str): Path to JSON file containing credit configurations
        
    Returns:
        tuple: (
            dict: Aggregated monthly payments by calendar year,
            float: Total paid across all credits
        )
    """
    with open(config_file) as f:
        credits = json.load(f)

    aggregated_payments = defaultdict(float)
    total_paid_all = 0.0

    for credit in credits:
        # Calculate individual credit
        loan_amount = credit['loan_amount']
        yearly_rates, total_paid = calculate_credit(
            interest_rate=credit['interest_rate'],
            total_loan=loan_amount,
            loan_period=credit['period'],
            partial_repayments=credit['partial_repayments']
        )

        # Offset payments by start year
        start_year = credit['start_year']
        for credit_year, monthly_rate in yearly_rates.items():
            calendar_year = start_year + credit_year - 1
            aggregated_payments[calendar_year] += monthly_rate

        # Handle redirected credits by subtracting their loan amount
        if credit.get('redirected', False):
            total_paid_all -= loan_amount
        total_paid_all += total_paid

    # Convert defaultdict to regular dict and sort
    ordered_payments = dict(sorted(aggregated_payments.items()))
    return ordered_payments, round(total_paid_all, 2)

def _main():
    """
    Command-line interface to calculate the monthly rate for each year of a loan.

    Parses command-line arguments and calls the `calculate_credit` function with provided parameters.
    Prints the result or error messages if inputs are invalid.
    """
    parser = argparse.ArgumentParser(description="Calculate the monthly rate for each year of a loan.")
    parser.add_argument("--interest-rate", type=float, help="Interest rate as float")
    parser.add_argument("--total-loan", type=float, help="Total loan amount as float")
    parser.add_argument("--loan-period", type=int, help="Loan period in years")
    parser.add_argument("--partial-repayments", type=float, help="Partial repayments as float")
    parser.add_argument("--partial-repayments-period", type=int, default=1,
                      help="Years between partial repayments (default: 1)")
    parser.add_argument("--config", type=str, 
                      help="Path to JSON config file for multiple credits")

    args = parser.parse_args()

    if args.config:
        try:
            yearly_payments, total = calculate_multiple_credits(args.config)
            for year, rate in yearly_payments.items():
                print(f"Year {year}: Combined Monthly Rate = {rate:.2f}")
            print(f"Total Paid Across All Credits: {total:.2f}")
        except Exception as e:
            print(f"Config error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            yearly_rates, total_paid = calculate_credit(
                args.interest_rate,
                args.total_loan,
                args.loan_period,
                args.partial_repayments,
                args.partial_repayments_period
            )
            for year, rate in yearly_rates.items():
                print(f"Year {year}: Monthly Rate = {rate:.2f}")
            print(f"Total Paid Over Loan Period: {total_paid:.2f}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    _main()
