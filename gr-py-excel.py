import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import uuid

# Sample DataFrame
data = {
    'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
    'Product': ['Apple', 'Apple', 'Banana', 'Banana', 'Orange', 'Orange', 'Apple', 'Apple'],
    'Sales': [100, 150, 200, 120, 180, 90, 110, 130],
    'Year': [2023, 2023, 2023, 2023, 2024, 2024, 2024, 2024]
}
df = pd.DataFrame(data)

# Create Excel file
excel_file = 'sales_report.xlsx'
writer = pd.ExcelWriter(excel_file, engine='openpyxl')

# Write DataFrame to first sheet
df.to_excel(writer, sheet_name='RawData', index=False)

# Create pivot table
pivot_df = df.pivot_table(values='Sales', 
                         index='Region', 
                         columns=['Year', 'Product'], 
                         aggfunc='sum', 
                         fill_value=0)

# Write pivot table to new sheet
pivot_df.to_excel(writer, sheet_name='PivotTable')

# Save the Excel file
writer.close()

print(f"Excel file '{excel_file}' created with raw data and pivot table.")
