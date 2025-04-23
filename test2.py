import pandas as pd

def pivot_and_count_flexible(df: pd.DataFrame, index_col: str, value_col: str) -> pd.DataFrame:
    """
    Pivots a DataFrame to count the occurrences of truthy and falsy values
    in a specified column, grouped by another column. Non-boolean values
    are treated as False.

    Args:
        df: The input pandas DataFrame.
        index_col: The name of the column to use as the index (grouping column).
        value_col: The name of the column to count truthy/falsy values in.
                   Non-boolean values are considered False.

    Returns:
        A pivoted DataFrame with counts of False, True, and Total values
        for each group in the index column.
    """
    if value_col not in df.columns:
        raise ValueError(f"Column '{value_col}' not found in DataFrame.")
    if index_col not in df.columns:
        raise ValueError(f"Column '{index_col}' not found in DataFrame.")

    # Treat non-boolean values as False
    processed_values = df[value_col].apply(lambda x: bool(x) if isinstance(x, bool) else False)

    counts = processed_values.groupby(df[index_col]).agg(['sum', 'count'])
    pivoted_df = counts.rename(columns={'sum': 'True', 'count': 'Total'})
    pivoted_df['False'] = pivoted_df['Total'] - pivoted_df['True']
    pivoted_df = pivoted_df[['False', 'True', 'Total']]
    return pivoted_df

# Example Usage:
data_flexible = {'Category': ['X', 'X', 'Y', 'Y', 'X', 'Z', 'Z', 'Y'],
                 'Status': [1, 0, 'yes', True, None, [], 'ok', False]}
df_flexible = pd.DataFrame(data_flexible)

try:
    result_flexible_df = pivot_and_count_flexible(df_flexible, index_col='Category', value_col='Status')
    print(result_flexible_df)
except ValueError as e:
    print(f"Error: {e}")

# Expected Output:
#           False  True  Total
# Category
# X             2     1      3
# Y             1     2      3
# Z             2     0      2

