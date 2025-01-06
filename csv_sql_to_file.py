import pandas as pd
import os

# Read the CSV file
csv_file = "your_file.csv"  # Update with your actual file path
output_dir = "sql_files"  # Directory to store the SQL files

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the CSV file
df = pd.read_csv(csv_file)

# Iterate through the rows and create .sql files
for _, row in df.iterrows():
    row_num = str(row["RowNum"]).strip()  # Convert to string and strip spaces
    logical_sql_name = str(row["Logical_SQL_Name"]).strip().replace(" ", "_")  # Remove spaces
    sql_select = str(row["SQL_Select"]).strip()

    # Define file name
    file_name = f"{row_num}_{logical_sql_name}.sql"
    file_path = os.path.join(output_dir, file_name)

    # Write SQL content to the file
    with open(file_path, "w", encoding="utf-8") as sql_file:
        sql_file.write(sql_select)

print(f"SQL files created in '{output_dir}' directory.")
