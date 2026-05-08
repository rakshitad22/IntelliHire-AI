# ==============================
# 📌 IntelliHire - Data Analysis
# ==============================

# STEP 1: Import libraries
import pandas as pd
import matplotlib.pyplot as plt

# STEP 2: Load dataset
df = pd.read_csv("resumes_dataset.csv")

print("\n✅ Dataset Loaded Successfully!\n")
print(df.head())


# ==============================
# 🔹 UNIVARIATE ANALYSIS
# ==============================

print("\n--- Univariate Analysis ---")

# 1. Label Distribution
print("\nLabel Counts:")
print(df['label'].value_counts())

# Plot 1: Label Distribution
plt.figure(1)
df['label'].value_counts().plot(kind='bar')
plt.title("Label Distribution (0 = Not Match, 1 = Match)")
plt.xlabel("Label")
plt.ylabel("Count")


# 2. Resume Length
df['resume_length'] = df['resume_text'].apply(lambda x: len(x.split()))

print("\nResume Length Stats:")
print(df['resume_length'].describe())

# Plot 2: Resume Length Histogram
plt.figure(2)
df['resume_length'].hist()
plt.title("Resume Length Distribution")
plt.xlabel("Number of Words")
plt.ylabel("Frequency")


# ==============================
# 🔹 MULTIVARIATE ANALYSIS
# ==============================

print("\n--- Multivariate Analysis ---")

# Average resume length vs label
print("\nAverage Resume Length by Label:")
print(df.groupby('label')['resume_length'].mean())

# Plot 3: Scatter Plot
plt.figure(3)
plt.scatter(df['resume_length'], df['label'])
plt.title("Resume Length vs Match")
plt.xlabel("Resume Length")
plt.ylabel("Match (0/1)")


# ==============================
# 📊 SHOW ALL GRAPHS
# ==============================
plt.show()