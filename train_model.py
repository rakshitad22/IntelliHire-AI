# ==============================
# 📌 IntelliHire - Model Training
# ==============================

# STEP 1: Import libraries
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix


# STEP 2: Load dataset
df = pd.read_csv("resumes_dataset.csv")

print("\n✅ Dataset Loaded!\n")
print(df.head())


# STEP 3: Combine resume + job description
df['text'] = df['resume_text'] + " " + df['job_description']

X = df['text']
y = df['label']


# STEP 4: Convert text → numbers (TF-IDF)
tfidf = TfidfVectorizer()
X = tfidf.fit_transform(X)


# STEP 5: Train-Test Split (IMPORTANT: stratify)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)


# STEP 6: Train Model
model = LogisticRegression()
model.fit(X_train, y_train)


# STEP 7: Predictions
y_pred = model.predict(X_test)


# STEP 8: Evaluation
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n🎯 Accuracy:", round(accuracy, 2))
print("🎯 F1 Score:", round(f1, 2))

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))


# STEP 9: Confusion Matrix (Graph)
cm = confusion_matrix(y_test, y_pred)

plt.imshow(cm)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.colorbar()
plt.show()