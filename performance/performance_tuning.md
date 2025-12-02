# Query Performance Tuning

## 1. Context & Goal

Our OLTP database models a healthcare system with patient admissions.  
For Phase 2, we focused on **analytical queries** over the `admission` fact table and related dimensions.

The goal of this tuning exercise is to:

- Analyze the performance of a **readmission detection query**.
- Use `EXPLAIN ANALYZE` to inspect the query plan.
- Design and apply an **indexing strategy** to improve performance.
- Compare **before vs. after** execution times and explain why the index helps.


## 2. Target Query — Readmissions Within 30 Days

**Business Question**

> For each patient, identify admissions that occur within 30 days of their previous admission.

This is an important metric for healthcare quality and cost analysis.

**SQL Query**

```
WITH ordered_admissions AS (
    SELECT
        a.admission_id,
        a.patient_id,
        a.date_of_admission,
        LAG(a.date_of_admission) OVER (
            PARTITION BY a.patient_id
            ORDER BY a.date_of_admission
        ) AS previous_admission_date
    FROM admission a
)
SELECT
    oa.patient_id,
    p.name AS patient_name,
    oa.admission_id,
    oa.date_of_admission,
    oa.previous_admission_date,
    EXTRACT(DAY FROM (oa.date_of_admission - oa.previous_admission_date)) AS days_since_last_admission
FROM ordered_admissions oa
JOIN patient p
    ON oa.patient_id = p.patient_id
WHERE oa.previous_admission_date IS NOT NULL
  AND oa.date_of_admission - oa.previous_admission_date <= INTERVAL '30 days'
ORDER BY oa.patient_id, oa.date_of_admission;
```
### Why this query is complex
- Uses a window function `LAG()` with `PARTITION BY` and `ORDER BY`.
- Processes potentially many rows in `admission`.
- Joins with `patient` to add human-readable names.
- Filters on date intervals and sorts the final result.

This makes it a good candidate for profiling and optimization.

## 3. Baseline Performance (Before Index)
We first ran the query with:
```
EXPLAIN ANALYZE
WITH ordered_admissions AS ( ... same query ... )
SELECT ...;
```
- Observed execution time before indexing:

#### Execution Time: 44.088 ms

From the query plan, PostgreSQL needed to:
- Scan the `admission` table.
- Sort rows per `patient_id` by `date_of_admission` to support the window function.
- Join with `patient` on `patient_id`.
Although the runtime is already acceptable, we aimed to improve performance and reduce sorting cost, especially if the dataset grows.

## 4. Index Design & Rationale
```
CREATE INDEX idx_admission_patient_date
ON admission (patient_id, date_of_admission);
```
Why this index?

The critical part of the query is:
```
LAG(a.date_of_admission) OVER (
    PARTITION BY a.patient_id
    ORDER BY a.date_of_admission
)
```
This means:
- We access rows grouped by `patient_id`.
- Within each patient, we order by `date_of_admission`.

A composite B-tree index on (`patient_id`, `date_of_admission`) aligns perfectly with this access pattern:
- PostgreSQL can read admissions for each patient already ordered by date.
- This reduces the need for explicit sorting and allows more efficient window-function processing.
- It also helps other queries that filter or group by `patient_id` and order by `date_of_admission`.

## 5. Performance After Index
After creating the index, we re-ran the same `EXPLAIN ANALYZE` query.
- Observed execution time after indexing:

#### Execution Time: 33.802 ms

Improvement
- Absolute improvement: `44.088 ms → 33.802 ms`
- Time saved: ≈ 10.286 ms
- Relative improvement: ≈ 23.3% faster
On a larger or more heavily-loaded system, this type of improvement becomes much more significant.

All performance measurements were taken using PostgreSQL running inside Docker, using pgAdmin's Query Tool.
**Summary**
- Before index: 44.088 ms  
- After index: 33.802 ms  
- Improvement: 23.3% faster

## 6. Interpretation of Results
The composite index on (`patient_id`, `date_of_admission`) helps because:
- The database engine can quickly retrieve admissions for each patient in the required order.
- The window function no longer needs a full sort of all rows; instead, it can leverage the index order.
- The join to `patient` on `patient_id` also benefits indirectly from better-structured access patterns.
Even though the dataset size (≈55k rows) is moderate, the query still gained a ~23% performance improvement, demonstrating correct use of indexing principles.

## 7. Possible Future Optimizations
If this system were deployed in production with much larger data volumes, we could explore:
- Additional indexes for other analytical queries (e.g., on `condition_id`, `hospital_id`, or `insurance_id`).
- Partitioning the `admission` table by year or month on `date_of_admission`.
- Materialized views for frequently-used rollups (e.g., monthly readmission rates per hospital).

For our course project, the current optimization is sufficient to demonstrate:
- Use of `EXPLAIN ANALYZE`.
- A justified indexing strategy.
- Measurable performance improvement aligned with the query’s access pattern.
