-- Trusted calculations for the example project.
-- Every metric reads the trusted history views (v_<source>), never staging.
-- The browser displays these results; it never recalculates them.

-- metric: total_amount
-- kind: kpi
-- title: Total revenue
-- format: money
-- unit: SAR
SELECT ROUND(SUM(amount), 2) AS value FROM v_sales;

-- metric: invoice_count
-- kind: kpi
-- title: Invoices
-- format: integer
SELECT COUNT(DISTINCT invoice_no) AS value FROM v_sales;

-- metric: average_invoice_value
-- kind: kpi
-- title: Average invoice
-- format: money
-- unit: SAR
SELECT ROUND(SUM(amount) / NULLIF(COUNT(DISTINCT invoice_no), 0), 2) AS value FROM v_sales;

-- metric: customers_served
-- kind: kpi
-- title: Customers served
-- format: integer
SELECT COUNT(DISTINCT customer_id) AS value FROM v_sales;

-- metric: amount_by_month
-- kind: series
-- title: Revenue by month
-- format: money
SELECT substr(invoice_date, 1, 7) AS label, ROUND(SUM(amount), 2) AS value
FROM v_sales
GROUP BY 1
ORDER BY 1;

-- metric: amount_by_segment
-- kind: series
-- title: Revenue by customer segment
-- format: money
SELECT COALESCE(c.segment, 'Unknown') AS label, ROUND(SUM(s.amount), 2) AS value
FROM v_sales s
LEFT JOIN v_customers c ON c.customer_id = s.customer_id
GROUP BY 1
ORDER BY 2 DESC;

-- metric: top_customers
-- kind: table
-- title: Top customers
SELECT COALESCE(c.customer_name, s.customer_id) AS "Customer",
       COALESCE(c.segment, 'Unknown')           AS "Segment",
       COUNT(DISTINCT s.invoice_no)             AS "Invoices",
       ROUND(SUM(s.amount), 2)                  AS "Revenue"
FROM v_sales s
LEFT JOIN v_customers c ON c.customer_id = s.customer_id
GROUP BY 1, 2
ORDER BY 4 DESC
LIMIT 10;
