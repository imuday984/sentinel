import numpy as np

def calculate_rolling_stats(history_data):
    """
    Takes a list of raw click dictionaries (last 20 clicks).
    Returns a dictionary of aggregate features.
    """
    if not history_data:
        return None

    # 1. Extract lists of numbers
    reaction_times = [d['reaction_time_ms'] for d in history_data]
    distances = [d['distance_from_center'] for d in history_data]

    # 2. Calculate Stats using NumPy
    # Variance is the most important feature for Anti-Cheat!
    # Humans have High Variance (inconsistent). Bots have Low Variance (perfect).
    rt_variance = np.var(reaction_times)
    rt_mean = np.mean(reaction_times)
    
    avg_dist = np.mean(distances)

    # 3. Return the "Feature Vector"
    return {
        "reaction_time_variance": float(rt_variance),
        "reaction_time_mean": float(rt_mean),
        "accuracy_mean": float(avg_dist),
        "clicks_analyzed": len(history_data)
    }