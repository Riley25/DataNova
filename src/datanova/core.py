import os
import pandas as pd
from typing import Optional, Sequence, Union

pd.set_option('display.max_columns', None)


def hello():
    print("Welcome to DataNova!")



#########################################################
###                  NOTES
#
#     We need fastparquet, pyarrow, openpyxl, matplotlib, sklearn, numpy, statsmodels
#
## All functions live here. 

import pandas as pd 
import os

def load_data(uploaded_file:str,  excel_sheet: Optional[Union[str, int]] = 0) -> pd.DataFrame:
    """
    PURPOSE: Load an Excel, CSV, or Parquet file into a Pandas DataFrame.

    Returns
    -------
    pd.DataFrame
        The loaded data.
    """

    uploaded_file = str(uploaded_file)
    _, file_extension = os.path.splitext(uploaded_file)
    file_extension = file_extension.lower()


    if file_extension in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file, sheet_name= excel_sheet, engine=None)
        return(df)
        
    elif file_extension == ".csv":
        df = pd.read_csv(uploaded_file, engine="c", low_memory=False)
        return(df)
        
    elif file_extension == ".parquet":
        df = pd.read_parquet( uploaded_file, engine = 'auto' )
        return(df)
        
    else:
        raise ValueError(f"Unsupported file extension: '{file_extension}'")
    



def highlight_missing(val):
    """
    Color code cells in '%_Blank' based on thresholds (0-100 scale).

    95-100 %    : #b80000
    90- 95 %    : #c11e11
    85- 90 %    : #c62d19
    80- 85 %    : #ca3b21
    75- 80 %    : #cf4a2a
    70- 75 %    : #d35932
    65- 70 %    : #d8673a
    60- 65 %    : #dc7643
    55- 60 %    : #e0854b
    50- 55 %    : #e59353
    45- 50 %    : #e9a25b
    40- 45 %    : #eeb164
    35- 40 %    : #f2bf6c 
    30- 35 %    : #f7ce74
    25- 30 %    : #fbdd7c
    20- 25 %    : #ffeb84
    15- 20 %    : #d7df81
    10- 15 %    : #b0d47f
     5- 10 %    : #8ac97d
     0-  5 %    : #63be7b
    """

    if val > 95:
        color = '#b80000'
    elif val > 90:
        color = '#c11e11'
    elif val > 85:
        color = '#c62d19'
    elif val > 80:
        color = '#ca3b21'
    elif val > 75:
        color = '#cf4a2a'
    elif val > 70:
        color = '#d35932'
    elif val > 65:
        color = '#d8673a'
    elif val > 60:
        color = '#dc7643'
    elif val > 55:
        color = '#e0854b'
    elif val > 50:
        color = '#e59353'
    elif val > 45:
        color = '#e9a25b'
    elif val > 40:
        color = '#eeb164'
    elif val > 35:
        color = '#f2bf6c'
    elif val > 30:
        color = '#f7ce74'
    elif val > 25:
        color = '#fbdd7c'
    elif val > 20:
        color = '#ffeb84'
    elif val > 15:
        color = '#d7df81'
    elif val > 10:
        color = '#b0d47f'
    elif val > 5:
        color = '#8ac97d'
    else:
        color = '#63be7b'
    
    return f'background-color: {color}'


def profile( df:pd.DataFrame ) -> pd.DataFrame:
    """
    PURPOSE
    -------
    Create a data profile of a pandas DataFrame to assess data quality.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    pd.DataFrame
        A summary with numeric stats, column metadata, etx.
    """

    n_row, n_col = df.shape
    r_total = "{:,}".format(n_row)
    print("ROW TOTAL = " + str(r_total) + " COLUMNS = " + str(n_col))

    # Basic summary
    summary = pd.DataFrame({
        "Variable Name": df.columns,
        "Variable Type": df.dtypes.astype(str),
        "Missing Count": df.isna().sum(),
        "% Blank": (df.isna().mean() * 100).round(0).astype("Int64"),
        "Unique Values": df.nunique(dropna=True),
        "Most Frequent Value": df.apply(
            lambda col: col.mode(dropna=True).iloc[0] if not col.mode(dropna=True).empty else pd.NA
        ),
    })

    # Universal describe (works for text-only, numeric-only, or mixed)
    desc = (
        df.describe(include="all")
          .T
          .reset_index()
          .rename(columns={"index":"Variable Name", 'count':'Count', 'unique':'Unique', 'top':'Top', "mean":"Mean", "50%": "Median", "max":"Max", "min":"Min", "std":"Standard Deviation"})
    )

    # Round numeric-looking stats if present (coerce non-numerics to NaN, which stay untouched)
    for col in ["Mean", "Standard Deviation", "Min", "25%", "Median", "75%", "Max"]:
        if col in desc.columns:
            desc[col] = pd.to_numeric(desc[col], errors="coerce").round(2)

    # Merge and return
    final = summary.merge(desc, on="Variable Name", how="left")


    if 'freq' in final.columns:
        final.drop(columns='freq', inplace=True)

    if 'top' in final.columns:
        final.drop(columns='top', inplace=True)

    if 'Top' in final.columns:
        final.drop(columns='Top', inplace=True)

    if 'Count' in final.columns:
        final.drop(columns='Count', inplace=True)

    if 'Unique' in final.columns:
        final.drop(columns='Unique', inplace=True)

    return( final )





###############################
#    Descriptive Plotting     #
###############################





