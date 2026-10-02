# Build the Power BI dashboard (about 1-2 hours, free Power BI Desktop)

Power BI Desktop is Windows-only and free: Microsoft Store -> "Power BI Desktop".
Do NOT list Power BI on your resume until you have built and can explain this file.

## 1. Load data
1. Get Data -> Text/CSV -> `clean_retail_sales.csv` -> Transform Data.
2. In Power Query set types: `order_date` = Date, `quantity` = Whole Number, `unit_price` and `revenue` = Decimal Number, `month` = Text. Close & Apply.
3. Rename the table to `sales`.
4. Get Data -> Text/CSV -> `data_quality_summary.csv` (table `dq`).

## 2. DAX measures (Modeling -> New measure)
```
Total Revenue = SUM(sales[revenue])
Orders = DISTINCTCOUNT(sales[order_id])
Avg Order Value = DIVIDE([Total Revenue], [Orders])

Revenue Z =
VAR tbl = ADDCOLUMNS(ALLSELECTED(sales[month]), "@rev", [Total Revenue])
VAR mu  = AVERAGEX(tbl, [@rev])
VAR sd  = STDEVX.S(tbl, [@rev])
RETURN DIVIDE([Total Revenue] - mu, sd)

Anomaly Flag = IF(ABS([Revenue Z]) > 1, "Anomaly", "Normal")
```

## 3. Page 1 - Sales overview
- 3 Card visuals: Total Revenue, Orders, Avg Order Value.
- Slicers: `category`, `region`.
- Column chart: X = `month`, Y = Total Revenue. Colour the columns with a rule based on the `Anomaly Flag` measure (Format -> Columns -> Colors -> fx -> Rules).
- Bar chart: `category` by Total Revenue. Bar chart: `region` by Total Revenue.
- Table or bar: top 5 `product` by Total Revenue (Filters pane -> Top N = 5).
- Heatmap: Matrix with `category` rows, `month` columns, Total Revenue values, Conditional formatting -> Background colour scale.
- Add a text box: "Synthetic dataset - for demonstration only."

## 4. Page 2 - Data quality
- Table or bar chart from `dq` (check, count).
- Text box describing the cleaning rules (copy from README).

## 5. Save and share
- File -> Save as `retail_sales_dashboard.pbix` (put it in this folder and commit it).
- File -> Export -> Export to PDF, and take a screenshot to `charts/powerbi_dashboard.png`.

## 6. Only after finishing, update the resume
- Add Power BI and DAX to Technical Skills.
- Replace the HTML-dashboard bullet with the Power BI version commented in `resume/resume.tex`.

## Tableau alternative
Tableau Public (free) -> Connect to Text file -> `clean_retail_sales.csv`. Rebuild the same views, publish to Tableau Public, and put the link on your resume. Use the same rule: list Tableau only once you've built it.
