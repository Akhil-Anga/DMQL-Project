-- Q1: Hospital revenue and ranking
SELECT
    h.hospital_name,
    COUNT(a.admission_id) AS total_admissions,
    SUM(a.billing_amount) AS total_revenue,
    ROUND(AVG(a.billing_amount), 2) AS avg_bill_per_admission,
    RANK() OVER (ORDER BY SUM(a.billing_amount) DESC) AS revenue_rank
FROM admission a
JOIN hospital h
    ON a.hospital_id = h.hospital_id
GROUP BY h.hospital_name
ORDER BY total_revenue DESC;


-- Q2: Readmissions within 30 days
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


-- Q3: Test result distribution by medical condition
SELECT
    c.condition_name,
    COUNT(*) AS total_tests,
    SUM(CASE WHEN t.test_result = 'Normal' THEN 1 ELSE 0 END) AS normal_count,
    SUM(CASE WHEN t.test_result = 'Abnormal' THEN 1 ELSE 0 END) AS abnormal_count,
    SUM(CASE WHEN t.test_result = 'Inconclusive' THEN 1 ELSE 0 END) AS inconclusive_count,
    ROUND(
        100.0 * SUM(CASE WHEN t.test_result = 'Abnormal' THEN 1 ELSE 0 END) 
        / NULLIF(COUNT(*), 0),
        2
    ) AS abnormal_rate_percent
FROM test_result t
JOIN admission a
    ON t.admission_id = a.admission_id
JOIN medical_condition c
    ON a.condition_id = c.condition_id
GROUP BY c.condition_name
ORDER BY abnormal_rate_percent DESC;


-- Q4: Insurance providers with above-average billing
WITH provider_stats AS (
    SELECT
        i.provider_name,
        COUNT(a.admission_id) AS total_admissions,
        AVG(a.billing_amount) AS avg_bill
    FROM admission a
    JOIN insurance_provider i
        ON a.insurance_id = i.insurance_id
    GROUP BY i.provider_name
),
overall AS (
    SELECT AVG(billing_amount) AS overall_avg
    FROM admission
)
SELECT
    p.provider_name,
    p.total_admissions,
    ROUND(p.avg_bill, 2) AS avg_bill,
    ROUND(o.overall_avg, 2) AS overall_avg_across_all_providers
FROM provider_stats p
CROSS JOIN overall o
WHERE p.avg_bill > o.overall_avg
ORDER BY p.avg_bill DESC;
