import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_pipeline():
	print("=== STARTING MOCK SUPPLY DATA PIPELINE ===")

	# 1. Generate Raw Messy Mock Data
	raw_data = {
		'Item_ID': ['MED-101', 'MED-102', 'MED-103', 'MED-104', 'MED-105'],
		'Supply_Name': ['Tourniquet CAT', 'Hemostatic Gauze', 'Trauma Dressing', 'IV Start Kit', 'Naloxone Injector'],
		'Stock_Quantity': [150, 45, np.nan, 200, 30],
		'Unit_Location': ['Camp Pendleton', 'San Diego', 'Coronado', 'Miramar', 'Camp Pendleton'],
		'Expiration_Date': ['2028-05-12', '2027-01-15', '2026-11-20', 'Invalid_Date', '2029-03-01'],
		'Readiness_Status': ['Operational', 'Operational', 'Low Stock', 'Review Required', 'Operational']
	}

	df_raw = pd.DataFrame(raw_data)
    
	# Save raw input file for audit trail
	os.makedirs('data', exist_ok=True)
	df_raw.to_csv('data/mock_supply_raw.csv', index=False)
    
	print("\n--- BEFORE CLEANING ---")
	print(df_raw.to_string())

	# 2. Automated Cleaning Pipeline
	df_clean = df_raw.copy()
    
	# Fill missing stock quantities with 0 baseline
	df_clean['Stock_Quantity'] = df_clean['Stock_Quantity'].fillna(0)
    
	# Standardize invalid date string formats
	df_clean['Expiration_Date'] = df_clean['Expiration_Date'].replace('Invalid_Date', '2027-06-01')

	# Save cleaned file
	df_clean.to_csv('data/mock_supply_cleaned.csv', index=False)

	print("\n--- AFTER AUTOMATED CLEANING ---")
	print(df_clean.to_string())

	# 3. Generate Executive Readiness Visualization
	os.makedirs('docs', exist_ok=True)
    
	plt.figure(figsize=(10, 6))
	sns.set_theme(style="whitegrid")
    
	ax = sns.barplot(
		x='Supply_Name', 
		y='Stock_Quantity', 
		hue='Unit_Location', 
		data=df_clean, 
		palette='Blues_d'
	)
    
	plt.title('Military Medical Logistics - Stock Quantity by Item and Location', fontsize=14, fontweight='bold', pad=15)
	plt.xlabel('Supply Item', fontsize=12)
	plt.ylabel('Stock Quantity', fontsize=12)
	plt.xticks(rotation=15)
	plt.legend(title='Unit Location')
	plt.tight_layout()

	# Save output chart into docs/ for GitHub presentation
	chart_path = 'docs/mock_supply_stock.png'
	plt.savefig(chart_path, dpi=300)
	print(f"\n[SUCCESS] Visualization saved directly to '{chart_path}'")

if __name__ == "__main__":
	run_pipeline()
