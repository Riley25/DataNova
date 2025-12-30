from __future__ import annotations

import textwrap
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick
from matplotlib.figure import Figure


# -----------------------------
# Styling helpers
# -----------------------------

def _set_plot_style() -> None:
    """Consistent, professional style (matches our STIX look)."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIXGeneral"],
            "mathtext.fontset": "stix",
        }
    )



def _wrap_cell_text(x: object, width: int = 12) -> str:
    """Wrap long strings to multiple lines for narrow tables."""
    s = "" if x is None else str(x)
    return "\n".join(textwrap.wrap(s, width=width)) if s else s



def _style_grid(ax, *, axis: str = "x") -> None:
    """Light dashed grid behind bars."""
    ax.grid(
        axis=axis,
        linestyle=(0, (5, 10)),
        linewidth=0.8,
        color="#c7c7c7",
        alpha=0.7,
        zorder=1.0,
    )


#def _style_table(table) -> None:
#    """Light borders + consistent padding/alignment."""
#    for cell in table.get_celld().values():
#        cell.set_linewidth(0.5)
#        cell.PAD = 0.12
#        cell.get_text().set_multialignment("center")



# -----------------------------
# Data prep
# -----------------------------
def bar_chart_data( df        : pd.DataFrame, 
                    var_name  : str, 
                    top_n_rows: int   = 5 ) -> pd.DataFrame:
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

    pivot_table["%"] = (
        pivot_table["count"] / pivot_table["count"].sum() * 100
    ).round(2)

    pivot_table["Cum. %"] = pivot_table["%"].cumsum().round(2)

    return( pivot_table.head(top_n_rows) )



def _set_table_column_widths(table, widths):
    """
    widths: list of floats, one per column, in *axes fraction* units.
    """
    cells = table.get_celld()
    nrows = max(r for (r, c) in cells.keys()) + 1

    for c, w in enumerate(widths):
        for r in range(nrows):
            if (r, c) in cells:
                cells[(r, c)].set_width(w)

# -----------------------------
# Main plot
# -----------------------------
def bar(
    df: pd.DataFrame,
    col_name: str,
    *,
    top_n: int = 5,
    bar_color: str = "#118dff",
    width: float = 10.0,
    height: float = 5.0,
    table_wrap_width: int = 12,
    ) -> Figure:
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

    width : float, default 10.0
        Figure width in inches.

    height : float, default 5.0
        Figure height in inches.
    
    table_wrap_width: int, default 12
        Maximum number of characters per line for text wrapping inside the table categorical column.

    Returns
    -------
    matplotlib.figure.Figure
        Final graph created
    """

    _set_plot_style()

    # ---- Data
    bar_data = bar_chart_data(df, col_name, top_n_rows=top_n).copy()

    # Wrap the categorical column in the TABLE (not the y-axis labels)
    bar_data[col_name] = bar_data[col_name].apply(lambda s: _wrap_cell_text(s, width=table_wrap_width))

    # ---- Layout
    fig = plt.figure(figsize=(width, height)  ,  constrained_layout=True)

    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 0.80], wspace=0.04)

    # ---- Bar chart
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_bar.barh(
        bar_data[col_name],
        bar_data["count"],
        color=bar_color,
        edgecolor="black",
        zorder=2.0)

    ax_bar.set_title(f"Bar Chart of {col_name}", fontsize=15)
    ax_bar.set_xlabel("Occurrences", fontsize=14)
    ax_bar.set_ylabel(col_name, fontsize=14)

    for label in (ax_bar.get_xticklabels() + ax_bar.get_yticklabels()):
        label.set_fontsize(11)

    ax_bar.invert_yaxis()
    ax_bar.spines[["top", "right"]].set_visible(False)

    _style_grid(ax_bar, axis="x")
    ax_bar.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))

    # ---- Table
    ax_table = fig.add_subplot(gs[0, 1])
    ax_table.axis("off")



    # Format BEFORE creating the table
    table_df = bar_data.copy()
    table_df["count"] = pd.to_numeric(table_df["count"], errors="coerce").fillna(0).astype(int).map("{:,}".format)
    table_df["%"] = pd.to_numeric(table_df["%"], errors="coerce").map(lambda v: f"{v:.2f}")
    table_df["Cum. %"] = pd.to_numeric(table_df["Cum. %"], errors="coerce").map(lambda v: f"{v:.2f}")



    table = ax_table.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        loc="center",
        cellLoc="center",
        bbox=[0.00 , 0.00 , 0.95 , 0.95 ]  # BBox ( left position , bottom position , table width (%), table height (%) )
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)            # slightly smaller = cleaner


    # Base styling first
    for cell in table.get_celld().values():
        cell.set_linewidth(0.4)
        cell.PAD = 0.12
        cell.get_text().set_multialignment("center")

    # Set column widths (must happen after table exists)
    _set_table_column_widths(table, widths=[0.45, 0.20, 0.17, 0.18])

    cells = table.get_celld()

    # Header styling (do this AFTER base styling so it doesn't get overwritten)
    ncols = len(table_df.columns)
    for c in range(ncols):
        cells[(0, c)].get_text().set_weight("bold")
        cells[(0, c)].set_facecolor("#ebebeb")
        cells[(0, c)].PAD = 0.22

    nrows = max(r for (r, c) in cells.keys()) + 1
    for r in range(1, nrows):
        cells[(r, 0)].get_text().set_ha("left")
        cells[(r, 0)].PAD = 0.05

    return( fig )


# Example usage:
df = pd.read_csv(r'D:\Documents\Python\CREATE_DATA\winemag-data_first150k.csv')

fig = bar(df, "country", top_n =  10 , bar_color="#118dff", width=10.0, height=5.0)
plt.savefig(r'C:\Users\riley\OneDrive\Desktop\country.png',dpi = 550)
plt.show()




