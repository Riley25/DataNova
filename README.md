<p align="center">
  <img src="https://raw.githubusercontent.com/Riley25/DataNova/refs/heads/main/images/supernova.jpg" alt="DataNova Logo" width="800">
</p>

# 🌌 DataNova
**DataNova** — a toolkit for quick data exploration in Python.  
Analyze, summarize, and visualize your data in just a few lines of code.

---

## 🚀 Features
- **Instant profiling**: Summarize your dataset structure with `profile(df)`
- **Bar Graph**: Show the top 5 most common 
- **Simple regression & stats** (coming soon!)




---

## 🧭 Examples

Examples use a dataset called `WINE_DF`

```python
profile( WINE_DF )
```
* Most of our data is not blank, expect for 'price' (only 5% blank). *

|   | Variable Name | Variable Type | Missing Count | % Blank | Unique Values | Most Frequent Value | Mean  | Standard Deviation | Min | 25% | Median | 75% | Max |
|---|---------------|---------------|---------------|---------|----------------|---------------------|-------|--------------------|-----|-----|--------|-----|-----|
| 0 | country       | object        | 0             | 0       | 24             | US                  |     |                  |   |   |      |   |   |
| 1 | province      | object        | 0             | 0       | 120            | California          |     |                 |   |   |      |   |   |
| 2 | points        | int64         | 0             | 0       | 13             | 90                  | 89.55 | 2.32               | 84.0| 88.0| 90.0   | 91.0| 96.0|
| 3 | price         | float64       | 88            | 5       | 110            | 20.0                | 38.71 | 29.39              | 7.0 | 20.0| 30.0   | 48.0| 500.0|
| 4 | variety       | object        | 0             | 0       | 161            | Pinot Noir          |       |                    |     |     |        |     |     |




```python
bar( WINE_DF , 'province')
```

<p align="center">
  <img src="https://raw.githubusercontent.com/Riley25/DataNova/refs/heads/main/images/BAR_GRAPH_v3.png" alt="Bar Graph Example" width="800">
</p>



```python
hist( WINE_DF , 'price' )
```
On average, a bottle of wine costs $38. The price ranges from: $20-$48

<p align="center">
  <img src="https://raw.githubusercontent.com/Riley25/DataNova/refs/heads/main/images/HIST.png" alt="Histogram Example" width="800">
</p>



--- 

## 🛠️ Installation
```bash
pip install datanova
``` 

