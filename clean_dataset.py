import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("SCMS_Delivery_History_Dataset.csv")

# 1. Remove duplicate rows
df = df.drop_duplicates()

# 2. Handle missing values
# Fill numeric columns with median
num_cols = df.select_dtypes(include=np.number).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Fill categorical columns with mode
cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    if not df[col].mode().empty:
        df[col] = df[col].fillna(df[col].mode()[0])

# 3. Clean numeric columns that are currently objects
def clean_numeric(x):
    if isinstance(x, str):
        if 'Freight' in x or 'Captured' in x or 'Invoiced' in x:
            return np.nan
        return x.replace(',', '')
    return x

df['Weight (Kilograms)'] = pd.to_numeric(df['Weight (Kilograms)'].apply(clean_numeric), errors='coerce')
df['Freight Cost (USD)'] = pd.to_numeric(df['Freight Cost (USD)'].apply(clean_numeric), errors='coerce')

# Fill newly created NaNs with median
df['Weight (Kilograms)'] = df['Weight (Kilograms)'].fillna(df['Weight (Kilograms)'].median())
df['Freight Cost (USD)'] = df['Freight Cost (USD)'].fillna(df['Freight Cost (USD)'].median())

# 4. Fix column names (clean format)
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('#', 'num').str.replace('/', 'or').str.replace('(', '').str.replace(')', '')

# 5. Convert date columns
date_cols = [col for col in df.columns if 'date' in col]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 6. Reset index
df.reset_index(drop=True, inplace=True)

# Save cleaned dataset
df.to_csv("SCMS_Delivery_History_Dataset_Cleaned.csv", index=False)
print("Cleaned dataset saved: SCMS_Delivery_History_Dataset_Cleaned.csv")
print("Shape:", df.shape)
