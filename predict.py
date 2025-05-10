import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
from sklearn.model_selection import StratifiedShuffleSplit
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score


# Ensure models folder exists
os.makedirs("models", exist_ok=True)

# Load data
df = pd.read_csv("data/gender_affirming_surgery_risk_dataset (1).csv")

# Handle missing values
imputer = SimpleImputer(strategy='most_frequent')
df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

# Encode categorical features
label_encoders = {}
for col in df_imputed.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    df_imputed[col] = le.fit_transform(df_imputed[col])
    label_encoders[col] = le

# Scale features
scaler = StandardScaler()
X = df_imputed.drop(columns=["PostOp_Risk_Level", "Complications"])
y_risk = df_imputed["PostOp_Risk_Level"]
y_complications = df_imputed["Complications"]

X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_risk_train, y_risk_test = train_test_split(X_scaled, y_risk, test_size=0.2, random_state=42)
_, _, y_comp_train, y_comp_test = train_test_split(X_scaled, y_complications, test_size=0.2, random_state=42)

# Train Risk model


sss_risk = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss_risk.split(X_scaled, y_risk):
    X_risk_train, X_risk_test = X_scaled[train_idx], X_scaled[test_idx]
    y_risk_train, y_risk_test = y_risk.iloc[train_idx], y_risk.iloc[test_idx]

# Apply SMOTE to risk training data
smote = SMOTE(random_state=42)
X_risk_train_sm, y_risk_train_sm = smote.fit_resample(X_risk_train, y_risk_train)

# Train risk model with class_weight='balanced'
risk_model = RandomForestClassifier(class_weight='balanced', random_state=42)
risk_model.fit(X_risk_train_sm, y_risk_train_sm)
y_risk_pred = risk_model.predict(X_risk_test)
print("Risk Prediction Report:")
print(classification_report(y_risk_test, y_risk_pred))
print("Accuracy:", accuracy_score(y_risk_test, y_risk_pred))

# Train Complication model
comp_model = RandomForestClassifier(random_state=42)
comp_model.fit(X_train, y_comp_train)
comp_preds = comp_model.predict(X_test)
print("Complications Prediction Report:\n", classification_report(y_comp_test, comp_preds))
print("Accuracy:", accuracy_score(y_comp_test, comp_preds))

# Save models and preprocessors
joblib.dump(risk_model, "api/models/risk_model.pkl")
joblib.dump(comp_model, "api/models/comp_model.pkl")
joblib.dump(scaler, "api/models/scaler.pkl")
joblib.dump(label_encoders, "api/models/label_encoders.pkl")