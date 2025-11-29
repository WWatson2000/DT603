import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# 1. LOAD AND PREPARE DATA
# Update the path if your file is in a different folder
df = pd.read_csv("monthly_expiring_by_title.csv")

# Assume first column is the month label
month_col = df.columns[0]

# Parse month as datetime (optional but useful)
df[month_col] = pd.to_datetime(df[month_col])

# Ensure numeric data and replace any missing values with 0
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Creating a simple time index for regression (0, 1, 2, ..., n-1)
df["MonthIndex"] = np.arange(len(df))
X = df[["MonthIndex"]].values  # shape (n_samples, 1)


# 2. RUN A SIMPLE LINEAR REGRESSION FOR EACH ACCREDITATION
results = []

for acc_title in df.columns[1:-1]:  # skip Month and MonthIndex
    y = df[acc_title].values

    # Fit linear regression: y = a + b * MonthIndex
    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    slope = model.coef_[0]          # "b" in the line above
    intercept = model.intercept_    # "a"
    r2 = r2_score(y, y_pred)

    results.append({
        "Accreditation": acc_title,
        "Slope": slope,
        "Intercept": intercept,
        "R2": r2,
        "TotalExpiring": y.sum()
    })

# Convert results to a dataFrame for easy viewing
results_df = pd.DataFrame(results)

# Sort by slope (descending) to see which accreditation is trending up fastest
results_sorted = results_df.sort_values(by="Slope", ascending=False)

print("Regression summary by accreditation (sorted by slope):")
print(results_sorted.to_string(index=False))


# 3. IDENTIFY THE HIGHEST-RISK ACCREDITATION
highest_risk = results_sorted.iloc[0]
print("\nHighest-risk accreditation based on trend:")
print(highest_risk)


# 4 PLOT ACTUAL VS REGRESSION LINE FOR THE HIGHEST-RISK TYPE
acc = highest_risk["Accreditation"]
y = df[acc].values

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

plt.figure(figsize=(8, 5))
plt.plot(df[month_col], y, marker="o", label="Actual monthly expiries")
plt.plot(df[month_col], y_pred, label="Regression trend line")
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Number expiring")
plt.title(f"Trend for {acc}")
plt.legend()
plt.tight_layout()
plt.show()
