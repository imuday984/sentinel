import pandas as pd
import numpy as np

SAMPLES = 5000
data = []

for _ in range(SAMPLES):
    # Humans
    rt = np.random.normal(250, 40, 20)
    acc = np.random.normal(15, 5, 20)
    data.append({
        "reaction_time_variance": np.var(rt),
        "reaction_time_mean": np.mean(rt),
        "accuracy_mean": np.mean(acc),
        "is_cheater": 0
    })
    # Bots
    rt = np.random.normal(150, 2, 20)
    acc = np.random.normal(1, 0.5, 20)
    data.append({
        "reaction_time_variance": np.var(rt),
        "reaction_time_mean": np.mean(rt),
        "accuracy_mean": np.mean(acc),
        "is_cheater": 1
    })

df = pd.DataFrame(data)
df.to_csv("training_data.csv", index=False)
print("✅ Saved training_data.csv")