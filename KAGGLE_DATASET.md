# Real Kaggle Dataset Integration

PathNotes can be connected to a real Kaggle job-market dataset instead of relying only on the small demonstration CSV.

## Recommended dataset

**Indian Job Market Dataset 2025-2026** by Shivam Shrivastava:
https://www.kaggle.com/datasets/shivamshrivastava21/indian-job-market-dataset-2025-2026

A public analysis of this dataset describes about 97,929 raw job postings and fields including job title, company, location, skills/tags, experience and salary. The dataset is useful for skill-demand, role, location and salary analysis.

## Download

Install KaggleHub if needed:

```bash
pip install kagglehub
```

Then download it using the Kaggle API / KaggleHub and place the CSV/XLSX under `data/kaggle/`.

The project intentionally keeps the small `career_skill_requirements.csv` as a fallback so the website works offline. For the final submission, use the downloaded Kaggle file as the market-data source and document the exact file/version used.

## Suggested analysis using the real data

1. Clean missing values and duplicates with Pandas.
2. Parse `tagsAndSkills` into normalized skills.
3. Count skill frequency by role.
4. Compare a student's skills with real market demand.
5. Add location and salary filters.
6. Show a "Market Demand" indicator beside each missing skill.
7. Use the What-If Simulator to test how learning a high-demand skill changes readiness.

This separates **real market evidence** from the project's demo role-skill matrix and makes the distinction clear during evaluation.
