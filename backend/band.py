import numpy as np
from baselines import seasonal_naive


# Collect Historical Forecast Residuals
def collect_residuals(net, folds=4, horizon=13):
    # Store the differences between actual and predicted values
    residuals = []
    # Perform multiple backtesting folds
    for k in range(folds):
        # Determine the end of the historical data for this fold
        end = len(net) - k * horizon

        # Use data before the test period as the training history
        history = net.iloc[:end - horizon]
        # Extract the actual values for the next forecast period
        actual = net.iloc[end - horizon:end].values
        # Calculate forecast errors (actual values minus predictions)
        residuals.append(actual - seasonal_naive(history))
    return np.array(residuals)


# Generate Forecast and Uncertainty Band
def make_band(net, history, horizon=13):

    # Collect historical forecast errors and flatten them into one array
    residuals = collect_residuals(net).flatten()     
    # Generate the main forecast using the seasonal naive baseline     
    point = seasonal_naive(history, horizon)
    # Calculate the lower forecast range using the 10th percentile error
    low = point + np.percentile(residuals, 10)
    # Calculate the upper forecast range using the 90th percentile error
    high = point + np.percentile(residuals, 90)         
    return point, low, high