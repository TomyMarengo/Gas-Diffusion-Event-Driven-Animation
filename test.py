import numpy as np
from scipy.optimize import minimize

def y(alpha, x):
    y = np.empty(len(x), float)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = x[i-1]*alpha + y[i-1]*(1-alpha)
    return y

def mape(alpha, x):
    diff = y(alpha, x) - x
    return np.mean(diff/x)

x = np.array([ 3, 4, 5, 6])
guess = .5
result = minimize(mape, guess, (x,), bounds=[(0,1)], method='SLSQP')
print(result)
[alpha_opt] = result.x