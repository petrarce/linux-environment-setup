
#!/usr/bin/env python3
import sys
import argparse

def calculate_credit(interest_rate, total_loan, loan_period, partial_repayments):
    """
    Calculate the monthly rate for each year of a loan.

    Args:
        interest_rate (float): The annual interest rate as a float between 0 and 1.
        total_loan (float): The total amount of the loan as a float greater than 0.
        loan_period (int): The period of the loan in years, must be an integer greater than 0.
        partial_repayments (float): The partial repayments as a float between 0 and 1.

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

    yearly_repaiment_amount = total_loan / loan_period
    remaining_loan = total_loan
    yearly_rates = {}
    total_paid = 0.0

    for year in range(1, loan_period + 1):
        monthly_payment = (remaining_loan * interest_rate + yearly_repaiment_amount) / 12
        yearly_rates[year] = monthly_payment
        
        annual_payment = monthly_payment * 12
        partial_payment = total_loan * partial_repayments
        total_paid += annual_payment + partial_payment

        remaining_loan = max(0, remaining_loan - (yearly_repaiment_amount + partial_payment))
        if remaining_loan == 0:
            break

    return yearly_rates, round(total_paid, 2)

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

    args = parser.parse_args()

    try:
        yearly_rates, total_paid = calculate_credit(args.interest_rate, args.total_loan, args.loan_period, args.partial_repayments)
        for year, rate in yearly_rates.items():
            print(f"Year {year}: Monthly Rate = {rate:.2f}")
        print(f"Total Paid Over Loan Period: {total_paid:.2f}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    _main()
