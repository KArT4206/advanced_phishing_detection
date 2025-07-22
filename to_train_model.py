import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import joblib
import os

# === Configuration ===
MODEL_PATH = "model/phishing_rf_model.joblib"
os.makedirs("model", exist_ok=True)

# === 1. Skip training if model already exists ===
if os.path.exists(MODEL_PATH):
    print(f"\n📁 Model already exists at: {MODEL_PATH}")
    print("✅ Skipping training.")
    exit()

# === 2. Extended Dataset (Realistic Legit + Phishing Examples) ===
data = [
    # --- Phishing examples ---
    [5.7, 3, 7, 0.91, 0.98, 2, 3],
    [6.5, 4, 0, 0.98, 0.96, 5, 4],
    [6.2, 4, 3, 0.92, 0.94, 3, 5],
    [5.6, 3, 9, 0.89, 0.91, 2, 2],
    [6.0, 4, 6, 0.90, 0.96, 3, 3],
    [6.1, 2, 5, 0.95, 0.97, 3, 3],
    [5.9, 2, 2, 0.92, 0.98, 4, 4],
    [6.3, 3, 1, 0.94, 0.99, 5, 3],

    # --- Legitimate examples (Google/Facebook style) ---
    [4.0, 0, 800, 0.05, 0.01, 0, 0],
    [4.1, 0, 850, 0.06, 0.00, 0, 0],
    [4.2, 0, 1000, 0.04, 0.02, 0, 0],
    [4.3, 0, 900, 0.08, 0.03, 0, 0],
    [4.0, 1, 850, 0.07, 0.01, 0, 0],
    [4.2, 0, 750, 0.06, 0.02, 0, 1],
    [4.4, 0, 900, 0.05, 0.01, 0, 0],
    [4.3, 1, 780, 0.09, 0.02, 0, 0]
]

labels = [
    1, 1, 1, 1, 1, 1, 1, 1,  # phishing
    0, 0, 0, 0, 0, 0, 0, 0   # legit
]

# === 3. Build Dataset and Split ===
df = pd.DataFrame(data, columns=[
    "url_entropy", "tls_flags", "domain_age_days",
    "nlp_conf", "visual_score", "js_flags", "dom_flags"
])
df["label"] = labels

X = df.drop("label", axis=1)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === 4. Train Random Forest Model ===
clf = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
clf.fit(X_train, y_train)

# === 5. Evaluate Model ===
y_pred = clf.predict(X_test)

print("\n🔍 Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2), "%")
print("\n📋 Classification Report:\n", classification_report(y_test, y_pred))
print("\n🧮 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# === 6. Plot & Save Feature Importance ===
importances = clf.feature_importances_
feature_names = X.columns

plt.figure(figsize=(8, 4))
plt.barh(feature_names, importances, color='skyblue')
plt.xlabel("Feature Importance")
plt.title("📊 Phishing Model - Feature Importance")
plt.tight_layout()
plt.savefig("model/feature_importance.png")
print("\n📈 Feature importance plot saved to: model/feature_importance.png")

# === 7. Save the Trained Model ===
joblib.dump(clf, MODEL_PATH)
print(f"\n✅ Model saved to: {MODEL_PATH}")
