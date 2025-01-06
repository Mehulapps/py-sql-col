import csv
import os

# Define the input CSV file and output directory
csv_file = "your_file.csv"  # Replace with your actual CSV file path
output_dir = "sql_files"  # Directory to store the SQL files

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Open the CSV file and process it
with open(csv_file, mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    
    # Skip the header row
    next(reader)

    for row in reader:
        if len(row) < 3:
            continue  # Skip if the row doesn't have enough columns

        row_num = row[0].strip()  # Get RowNum
        logical_sql_name = row[1].strip().replace(" ", "_")  # Get Logical_SQL_Name and replace spaces with underscores
        sql_select = row[2].strip()  # Get SQL_Select

        # Define the SQL file name
        file_name = f"{row_num}_{logical_sql_name}.sql"
        file_path = os.path.join(output_dir, file_name)

        # Write the SQL statement to a file
        with open(file_path, mode="w", encoding="utf-8") as sql_file:
            sql_file.write(sql_select)

print(f"SQL files have been successfully created in the '{output_dir}' directory.")
