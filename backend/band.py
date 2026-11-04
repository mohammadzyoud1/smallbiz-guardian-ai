import numpy as np

from baselines import seasonal_naive


def collect_residuals(net, folds=4, horizon=13):
    residuals = []
    for k in range(folds):
        end = len(net) - k * horizon
        history = net.iloc[:end - horizon]
        actual = net.iloc[end - horizon:end].values
        residuals.append(actual - seasonal_naive(history))
    return np.array(residuals)



def make_band(net, history, horizon=13):
    residuals = collect_residuals(net).flatten()          
    point = seasonal_naive(history, horizon)
    low = point + np.percentile(residuals, 10)
    high = point + np.percentile(residuals, 90)         
    return point, low, high