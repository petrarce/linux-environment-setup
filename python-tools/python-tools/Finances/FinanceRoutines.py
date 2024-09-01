import math
import numpy

def computeComplexPercentIncome(initialSum, yearlyFee, expectedIncome, years):

    totalSum = (initialSum + yearlyFee) * math.pow(1 + expectedIncome, years)
    for i in range(2, years+1):
        totalSum += yearlyFee * math.pow(1 + expectedIncome, i)
    return totalSum
