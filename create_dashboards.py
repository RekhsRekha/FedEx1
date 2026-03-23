import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# Load dataset
df = pd.read_csv("SCMS_Delivery_History_Dataset.csv")

# Data Cleaning
# Convert dates to datetime objects
date_cols = [
    'PQ First Sent to Client Date', 'PO Sent to Vendor Date',
    'Scheduled Delivery Date', 'Delivered to Client Date',
    'Delivery Recorded Date'
]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Convert numeric columns, handling strings like "Freight Included in Commodity Cost"
def clean_numeric(x):
    if isinstance(x, str):
        if 'Freight' in x or 'Captured' in x or 'Invoiced' in x:
            return np.nan
        return x.replace(',', '')
    return x

df['Freight Cost (USD)'] = pd.to_numeric(df['Freight Cost (USD)'].apply(clean_numeric), errors='coerce')
df['Weight (Kilograms)'] = pd.to_numeric(df['Weight (Kilograms)'].apply(clean_numeric), errors='coerce')

# Calculate Metrics
# 1. Total Orders
total_orders = len(df)

# 2. Late Deliveries
# Lateness = Delivered to Client Date > Scheduled Delivery Date
df['is_late'] = df['Delivered to Client Date'] > df['Scheduled Delivery Date']
late_deliveries_count = df['is_late'].sum()
late_deliveries_pct = (late_deliveries_count / total_orders) * 100

# 3. Delivery Time (Days)
# Use PO Sent to Vendor Date to Delivered to Client Date
df['delivery_time'] = (df['Delivered to Client Date'] - df['PO Sent to Vendor Date']).dt.days
avg_delivery_time = df['delivery_time'].mean()

# Dashboard 1: Delivery Performance
fig1, axes1 = plt.subplots(2, 2, figsize=(16, 12))
fig1.suptitle('Dashboard 1: Delivery Performance', fontsize=24, fontweight='bold')

# KPI 1: Total Orders
axes1[0, 0].text(0.5, 0.5, f"{total_orders:,}", fontsize=50, ha='center', va='center', color='blue')
axes1[0, 0].text(0.5, 0.3, "Total Orders", fontsize=20, ha='center', va='center')
axes1[0, 0].axis('off')

# KPI 2: Late Delivery %
axes1[0, 1].text(0.5, 0.5, f"{late_deliveries_pct:.1f}%", fontsize=50, ha='center', va='center', color='red')
axes1[0, 1].text(0.5, 0.3, "Late Delivery %", fontsize=20, ha='center', va='center')
axes1[0, 1].axis('off')

# KPI 3: Avg Delivery Time
axes1[1, 0].text(0.5, 0.5, f"{avg_delivery_time:.1f} Days", fontsize=50, ha='center', va='center', color='green')
axes1[1, 0].text(0.5, 0.3, "Avg Delivery Time", fontsize=20, ha='center', va='center')
axes1[1, 0].axis('off')

# Chart: Delays by Region (Top 10 Countries)
late_by_country = df[df['is_late'] == True]['Country'].value_counts().head(10)
sns.barplot(x=late_by_country.values, y=late_by_country.index, ax=axes1[1, 1], palette='viridis')
axes1[1, 1].set_title('Top 10 Countries by Late Deliveries', fontsize=16)
axes1[1, 1].set_xlabel('Number of Late Deliveries')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('delivery_performance_dashboard.png')
print("Dashboard 1 saved: delivery_performance_dashboard.png")

# Dashboard 2: Cost & Efficiency
fig2, axes2 = plt.subplots(2, 2, figsize=(16, 12))
fig2.suptitle('Dashboard 2: Cost & Efficiency', fontsize=24, fontweight='bold')

# Chart 1: Avg Cost by Vendor (Top 10)
avg_cost_vendor = df.groupby('Vendor')['Freight Cost (USD)'].mean().sort_values(ascending=False).head(10)
sns.barplot(x=avg_cost_vendor.values, y=avg_cost_vendor.index, ax=axes2[0, 0], palette='magma')
axes2[0, 0].set_title('Top 10 Vendors by Avg Freight Cost', fontsize=16)
axes2[0, 0].set_xlabel('Avg Freight Cost (USD)')

# Chart 2: Cost vs Delivery Time
# Filter out NaNs for the scatter plot
scatter_data = df.dropna(subset=['Freight Cost (USD)', 'delivery_time'])
# Filter out extreme outliers for better visualization
scatter_data = scatter_data[(scatter_data['Freight Cost (USD)'] < scatter_data['Freight Cost (USD)'].quantile(0.95)) & 
                            (scatter_data['delivery_time'] > 0) & (scatter_data['delivery_time'] < 365)]
sns.scatterplot(data=scatter_data, x='delivery_time', y='Freight Cost (USD)', alpha=0.5, ax=axes2[0, 1])
axes2[0, 1].set_title('Freight Cost vs. Delivery Time', fontsize=16)
axes2[0, 1].set_xlabel('Delivery Time (Days)')
axes2[0, 1].set_ylabel('Freight Cost (USD)')

# Chart 3: Shipment Mode Analysis
shipment_counts = df['Shipment Mode'].value_counts()
axes2[1, 0].pie(shipment_counts, labels=shipment_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
axes2[1, 0].set_title('Shipment Mode Distribution', fontsize=16)

# Chart 4: KPI - Avg Freight Cost
avg_freight_total = df['Freight Cost (USD)'].mean()
axes2[1, 1].text(0.5, 0.5, f"${avg_freight_total:,.2f}", fontsize=50, ha='center', va='center', color='purple')
axes2[1, 1].text(0.5, 0.3, "Avg Freight Cost (Total)", fontsize=20, ha='center', va='center')
axes2[1, 1].axis('off')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('cost_efficiency_dashboard.png')
print("Dashboard 2 saved: cost_efficiency_dashboard.png")
