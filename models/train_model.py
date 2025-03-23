import pandas as pd
import numpy as np
import joblib  # For saving the model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier  # Using a more powerful model
from sklearn.metrics import accuracy_score

# Step 1: Load the dataset
df = pd.read_csv(r"C:\Users\DELL\diabetic_retinopathy_detection\diabetes.csv")  # Make sure the dataset is inside 'uploads' folder

# Step 2: Features and Target
X = df.drop(columns=["Outcome"])  # Selecting all columns except the target (Outcome)
y = df["Outcome"]  # Selecting the target column

# Step 3: Split data into Training (80%) and Testing (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Normalize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Step 5: Train the model (Random Forest Classifier)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Step 7: Save the trained model and scaler for Flask usage
joblib.dump(model, "diabetes_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model training complete! Model and scaler saved successfully.")
