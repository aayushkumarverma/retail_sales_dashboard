RETAIL SALES INTELLIGENCE - FRONTEND VERSION

RUN ON WINDOWS:
1. Open this folder in VS Code.
2. Open Terminal.
3. Run: python -m pip install -r requirements.txt
4. Run: python -m streamlit run app.py
5. Your browser will open the dashboard.

PAGES:
- Overview: KPI cards and charts.
- Sales Analytics: filters and product/category analysis.
- Loss & Slow-Mover Detector: low-margin, discount-pressure and sales-decline flags.
- Profit Simulator: test price and discount scenarios.
- Data Explorer: inspect and download processed data.

CSV COLUMNS:
Date, OrderID, Product, Category, Quantity, Unit Price, Unit Cost, Discount

LIMITATIONS:
Sales decline is a warning, not proof of unsold stock; stock-on-hand data is not included.
The simulator assumes historical unit volume stays unchanged. Overheads are excluded.
