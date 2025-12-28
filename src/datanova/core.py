#-----------------------------------------------------------------
#
#  Name:    core.py
#
#  Purpose: These are the essential functions for DataNova / DSTK
#
#  Date:    Winter 2025
#
#  Author:  Riley & Justyna
#
#-----------------------------------------------------------------
#                            NOTES
#
#     dependents: fastparquet, pyarrow, openpyxl, matplotlib, sklearn, numpy, statsmodels


import os

from typing import Optional, Sequence, Union

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
import matplotlib.ticker as mtick

import pandas as pd 


pd.set_option('display.max_columns', None)

#----------------------------------------
#       Data Loading & Profile    


def hello():
    print("Welcome to DataNova!")


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



#----------------------------------------
#       Descriptive Plotting     


def bar_chart_data( df        : pd.DataFrame, 
                    var_name  : str, 
                    top_n_rows: int   = 6 ) -> pd.DataFrame:
    """
    Efficiently generate bar chart data with counts, cumulative probability.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    var_name : str
        Column name to analyze (data must be categorical / text).

    Returns
    -------
    pd.DataFrame
        A DataFrame with most common values.
    """

    col = df[var_name].fillna("N/A").astype(str)

    pivot_table = (
        col.value_counts()
           .reset_index()
           #.rename(columns={"index": var_name, var_name: "Occurrences"})
           .rename(columns={"index": var_name} )
    )

    pivot_table["Percentage"] = (
        pivot_table["count"] / pivot_table["count"].sum() * 100
    ).round(2)

    pivot_table["Cumulative %"] = pivot_table["Percentage"].cumsum().round(2)

    return( pivot_table.head(top_n_rows) )



def bar(                df       : pd.DataFrame, 
                        col_name : str, 
                        * , 
                        top_n    : int   = 6 ,
                        bar_color: str   = "#4d9b1e", 
                        width    : float = 13.33 , 
                        height   : float =  6.0    ) -> Figure:
    """
    Creates a combined plot with:
    - A bar chart on the left
    - A summary table of most frequent values on the right

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    col_name : str
        Column name to plot (data must be text).

    top_n : int
        Number of bars

    bar_color : str
        Bar color as HEX code (e.g., '#4d9b1e').

    width : float, default 13.33
        Figure width in inches.

    height : float, default 6.0
        Figure height in inches.

    Returns
    -------
    matplotlib.figure.Figure
        Final graph created
    """

    plt.rcParams["font.family"] = "Times New Roman"

    # Calculate bar chart data using your utility function
    bar_data = bar_chart_data(df, col_name, top_n_rows=top_n)

    # Truncate y-axis labels
    max_label_length = 12  # Maximum length for y-axis labels
    bar_data[col_name] = bar_data[col_name].apply(lambda x: x[:max_label_length] + "..." if len(x) > max_label_length else x)

    # Create the figure 
    fig = plt.figure(figsize=(width, height))  # Adjust figure size as needed
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.1, 1])  # Grid layout for bar chart and table

    # Bar Chart (Left)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_bar.grid(axis='x', zorder=1.0)
    ax_bar.barh(bar_data[col_name], bar_data["count"], color=bar_color, edgecolor="black", zorder=2.0)

    ax_bar.set_title(f"Bar Chart of {col_name}", fontsize=15)
    ax_bar.set_xlabel("Occurrences", fontsize=14)
    ax_bar.set_ylabel(col_name, fontsize=14)

    # Increase font size for tick labels
    for label in (ax_bar.get_xticklabels() + ax_bar.get_yticklabels()):
        label.set_fontsize(11)

    ax_bar.invert_yaxis()  # Invert y-axis for better readability
    ax_bar.spines[['top', 'right']].set_visible(False)

    ax_bar.xaxis.set_major_formatter(
        mtick.StrMethodFormatter('{x:,.0f}')
    )

    # Table (Right)
    ax_table = fig.add_subplot(gs[0, 1])
    ax_table.axis("off")  # Turn off axis for table
    table = ax_table.table(
        cellText=bar_data.values,
        colLabels=bar_data.columns,
        loc="center",
        cellLoc="center"
    )

    # Adjust table properties
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Dynamically adjust column widths
    col_width_scale = max(1, width / 13.33 * 1.2)  # Scale columns based on figure width
    table.scale(col_width_scale, 1.55)

    # Truncate long text in the first column
    for cell in table.get_celld().values():
        cell_text = cell.get_text().get_text()
        if len(cell_text) > 20:  # Limit text to 20 characters
            truncated_text = cell_text[:11] + "..."
            cell.get_text().set_text(truncated_text)

    # Adjust layout to avoid overlap
    plt.tight_layout()

    plt.close(fig)
    
    return( fig )



def hist_data(df : pd.DataFrame,  var_name : str) -> pd.DataFrame:
    """
    Calculate statistics for a numeric column in a pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    var_name : str
        Column name to analyze (data must be numeric).

    Returns
    -------
    pd.DataFrame
        A DataFrame with statistic names and their values.
    """
        
    if var_name not in df.columns:
        raise ValueError(f"Column '{var_name}' does not exist in the DataFrame.")

    column_data = df[var_name]
    non_blank_data = column_data.dropna()

    stats = {
        "Statistic": [
            "Min", "25% Quartile","Mean", "Median",  "75% Quartile", 
            "Max",  "Standard Deviation", 
            "Count of Rows", "Count of Rows Not Blank", "% Blank"
        ],
        "Value": [
            column_data.min().round(2),
            column_data.quantile(0.25).round(2),
            column_data.mean().round(2),
            column_data.median().round(2),
            column_data.quantile(0.75).round(2),
            column_data.max().round(2),
            column_data.std().round(2),
            len(column_data),
            len(non_blank_data),
            round(100 * (1 - len(non_blank_data) / len(column_data)), 2) if len(column_data) > 0 else 0
        ]
    }

    S = pd.DataFrame(stats) 
    return( S )


def hist(               df       : pd.DataFrame, 
                        col_name : str, 
                        *,
                        xlim: Union[list, None] = None ,
                        n_bins: int = 20 ,
                        bar_color: str = "#4d9b1e" ,
                        width: float = 13.33 ,
                        height: float = 6.0 ,   
                        ) -> Figure:
    """
    Create a combined visualization: box plot, histogram, and a summary-statistics table.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    col_name : str
        Column name to plot (data must be numeric).
    
    xlim: list
        The min and max range to be plotted

    bar_color : str
        Bar/box color (e.g., '#4d9b1e').

    n_bins : int, default 20
        Number of histogram bins.

    width : float, default 13.33
        Figure width in inches.

    height : float, default 6.0
        Figure height in inches.

    Returns
    -------
    matplotlib.figure.Figure
        Final graph created

    """
    plt.rcParams["font.family"] = "Times New Roman"

    
    # Calculate statistics for the table
    stats = hist_data(df, col_name)  # Use your utility function here 
    stats.columns = ["Statistic", "Value"]  # Ensure proper column labels 

    data = df[col_name].dropna()    

    # Create the figure 
    fig = plt.figure(figsize=(width, height))  # Adjust the figure size as needed
    gs = gridspec.GridSpec(2, 3, width_ratios=[2, 1, 2], height_ratios=[1, 3])  # Adjust grid layout

    # Box Plot (Top-Left)
    ax_box = fig.add_subplot(gs[0, 0:2])
    ax_box.boxplot(data, vert=False, patch_artist=True, boxprops=dict(facecolor=bar_color), zorder=2.0)  
    #ax_box.grid(axis='x',zorder=1.0)

    if xlim is not None:
        ax_box.set_xlim(xlim)
        
    ax_box.axes.get_yaxis().set_visible(False)  # Hide y-axis for box plot
    ax_box.set_xticklabels([])                  # Remove x-axis labels
    ax_box.spines[['top','left', 'right', 'bottom']].set_visible(False)
    ax_box.set_title(f"Histogram of {col_name}", fontsize = 15)

    # Histogram (Bottom-Left)
    ax_hist = fig.add_subplot(gs[1, 0:2])
    ax_hist.grid(axis='x' ,zorder=3.0)


    if xlim == None:
        ax_hist.hist(data, bins=n_bins, color=bar_color, edgecolor='black', zorder = 4.0)
    else:
        ax_hist.hist(data, bins=n_bins, range = xlim, color=bar_color, edgecolor='black', zorder = 4.0)
    
    ax_hist.set_xlabel(col_name, fontsize=13)
    ax_hist.set_ylabel("Count", fontsize = 13)
    for label in (ax_hist.get_xticklabels() + ax_hist.get_yticklabels()): label.set_fontsize(11)
    ax_hist.spines[['top','right']].set_visible(False)
    
    # commas for y-axis (12,345 --> 12,345)
    ax_hist.yaxis.set_major_formatter(
        mtick.StrMethodFormatter('{x:,.0f}')
    )

    # Table (Right)
    ax_table = fig.add_subplot(gs[:, 2])  # Span rows 0 and 1 for the table
    ax_table.axis("off")  # Turn off the axis
    table = ax_table.table(
        cellText=stats.values,
        colLabels=stats.columns,
        loc="center",
        cellLoc="center")
    
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.auto_set_column_width(col=list(range(len(stats.columns))))

    table.scale(1 , 1.75)

    # Adjust layout to avoid overlap
    plt.tight_layout()
    plt.close(fig)
    
    return( fig )




#----------------------------------------
#   Exploritory Data Analysis - EDA   


def _in_notebook() -> bool:
    """
    This function returns True or False:
    
    True  --> The Python code is       being executed in a Jupyter Notebook
    False --> The Python code is  NOT  being executed in a Jupyter Notebook
    
    Returns
    ----------
    bool
    """
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell == "ZMQInteractiveShell"  # Jupyter/VSCode notebooks
    except Exception:
        return False
    

def EDA( df: pd.DataFrame ) -> list[Figure]:
    """
    This function is a quick “EDA” analysis. (Exploratory Data Analysis)
    Plot the distribution for every column in a dataset.  

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    ----------
    list[matplotlib.figure.Figure]
        Figures created.
    """

    n_row, n_col = df.shape
    bar_colors = ["#826fc2","#143499","#4d9b1e","#f865c6","#ecd378","#ba004c","#8f4400","#f65656"]*(n_col*2)
    figs = []


    in_nb = _in_notebook()
    if in_nb:
        from IPython.display import display
    
        
    for count, var_name in enumerate(df.columns):
        
        # IF the column is 100% blank then skip it
        if df[var_name].isna().all():
            continue


        bar_color_i = bar_colors[count]            

        if pd.api.types.is_numeric_dtype( df[var_name] ):
            fig = hist(df,var_name, bar_color = bar_color_i)
            figs.append(fig)

        elif (pd.api.types.is_string_dtype(df[var_name]) or pd.api.types.is_object_dtype(df[var_name]) or pd.api.types.is_categorical_dtype(df[var_name])):
            fig = bar(df, var_name, bar_color = bar_color_i)
            figs.append(fig)
        

        # IF the data type is not numeric, or text, 
        # THEN stop the loop 
        # AND go to the next iteration
        else: 
            continue
        
        if in_nb:
            display(fig)

    return(figs)








#----------------------------------------
#       Appendix - Nice to Have  


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


