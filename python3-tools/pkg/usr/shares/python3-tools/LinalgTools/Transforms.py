import numpy as np


# function to convert column of matrix to 1D vector:
def vectorfy(mtrx, clmn):
    return np.array(mtrx[:, clmn]).reshape(-1)
