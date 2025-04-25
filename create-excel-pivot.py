import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.pivot_table import PivotTable, PivotCache, PivotCacheDefinition, DataField, PivotField

# Step 1: Create a DataFrame
data = {
    'Category': ['Fruit', 'Fruit', 'Vegetable', 'Vegetable', 'Fruit'],
    'Item': ['Apple', 'Banana', 'Carrot', 'Tomato', 'Banana'],
    'Amount': [10, 20, 15, 30, 5]
}
df = pd.DataFrame(data)

# Step 2: Save DataFrame to Excel
excel_file = 'pivot_example.xlsx'
df.to_excel(excel_file, sheet_name='Data', index=False)

# Step 3: Load the workbook and sheet
wb = load_workbook(excel_file)
ws = wb['Data']

# Step 4: Create Pivot Cache
pivot_cache = PivotCache(cacheId=1, cacheSource='worksheet', worksheet=ws.title)

# Step 5: Create Pivot Table
pivot_table = PivotTable(
    cache=pivot_cache,
    ref="E4"  # where you want to place the pivot table
)

# Step 6: Add Pivot Fields
pivot_table.rowFields.append(PivotField(name='Category'))
pivot_table.rowFields.append(PivotField(name='Item'))
pivot_table.dataFields.append(DataField(name='Amount', summarizeFunction='sum'))

# Step 7: Add the Pivot Table to the sheet
ws.add_pivot(pivot_table)

# Step 8: Save the workbook
wb.save(excel_file)

print(f"Pivot Table created successfully in '{excel_file}'!")
