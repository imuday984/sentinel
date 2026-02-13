import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from skl2onnx import to_onnx

# 1. Load Data
df = pd.read_csv("training_data.csv")

# Use the EXACT names from the CSV
cols = ["reaction_time_variance", "reaction_time_mean", "accuracy_mean"]
X = df[cols].values.astype(np.float32)
y = df["is_cheater"]

# 2. Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
clf = RandomForestClassifier(n_estimators=10)
clf.fit(X_train, y_train)

# 3. Export with ZipMap False (Crucial for Node.js)
onx = to_onnx(clf, X_train[:1], options={'zipmap': False})

with open("cheat_model.onnx", "wb") as f:
    f.write(onx.SerializeToString())

print("💾 Saved FIXED model to 'cheat_model.onnx'")