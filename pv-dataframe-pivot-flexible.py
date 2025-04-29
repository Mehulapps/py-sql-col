import pandas as pd

def write_df_to_excel_with_pivot(df, file_name, sheet_name, pivot_sheet_name, pivot_func):
    """
    Write a pandas DataFrame to a named Excel file and worksheet, preserving column names,
    and create a pivot table in another sheet within the same file using a provided pivot function.
    
    Parameters:
    df (pandas.DataFrame): The DataFrame to write
    file_name (str): Name of the Excel file (e.g., 'output.xlsx')
    sheet_name (str): Name of the worksheet for raw data
    pivot_sheet_name (str): Name of the worksheet for pivot table
    pivot_func (callable): Function that takes a DataFrame and returns a pivot table DataFrame
    """
    # Create ExcelWriter object
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        # Write original DataFrame to specified sheet, including column names
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Apply the pivot function to create the pivot table
        pivot_table = pivot_func(df)
        
        # Write pivot table to another sheet
        pivot_table.to_excel(writer, sheet_name=pivot_sheet_name, index=False)

# Example pivot function
def example_pivot_func(df):
    """
    Example pivot function: Count of Names by City
    """
    return pd.pivot_table(
        df,
        values='Name',
        index='City',
        aggfunc='count'
    ).reset_index()

# Example usage
if __name__ == "__main__":
    # Sample DataFrame
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 28, 22],
        'City': ['New York', 'London', 'Paris', 'New York', 'London']
    }
    df = pd.DataFrame(data)
    
    # Write to Excel with pivot table using the pivot function
    write_df_to_excel_with_pivot(df, 'sample_output.xlsx', 'EmployeeData', 'CityPivot', example_pivot_func)
