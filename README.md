# 📊 Employee Analytics Suite

An interactive, multi-page analytics dashboard built with **Streamlit**, designed to analyze employee data, identify risk factors, evaluate performance, and generate personalized reports.

---

# Problem Description
The Employee Performance and Productivity Analytics System addresses the challenge of optimizing workforce management by providing actionable insights into employee performance, productivity, and retention risks. Traditional HR systems often lack predictive capabilities and comprehensive analytics, making it difficult for organizations to proactively address issues such as employee attrition, training needs, and promotion readiness. This system leverages machine learning techniques to analyze employee data, predict risks, and recommend interventions, enabling data-driven decision-making for HR professionals and managers.

# Functionalities
1.	Dashboard:
- Displays key performance indicators (KPIs) such as average performance score, employee satisfaction, and resignation risk.
- Visualizes performance distribution across the organization.
2.	Employee Analysis:
- Provides detailed profiles of individual employees, including tenure, performance scores, and department.
- Generates personalized recommendations for retention, promotion, and training based on predictive models.
3.	New Employee Evaluation:
- Predicts the performance and resignation risk of new hires based on input metrics.
- Offers actionable recommendations for onboarding and development.
4.	Risk & Growth Insights:
- Identifies employees at high risk of resignation using a simulated risk score.
- Recommends promotion candidates based on performance, tenure, and training.
- Highlights training needs for underperforming employees.
- Alerts managers about employees with concerning sick leave patterns.

## 🚀 Quick Overview

This project enables HR teams or managers to:
- Monitor employee performance and satisfaction
- Predict risks like attrition or poor productivity
- Generate PDF-based evaluation reports
- Visualize department-wise insights
- Perform custom evaluations for new or existing employees

---

## 🧠 Strategy & Logic

- **Weighted Scoring System**: Calculates a custom `Productivity_Score` using a formula that includes training hours, performance scores, and more.
- **Rule-Based Evaluation**: Flags employees for resignation risk, promotion eligibility, or training needs using logical conditions.
- **Dynamic Report Generation**: Generates downloadable PDF evaluations based on current inputs.
- **Session State Tracking**: Uses Streamlit session state to store user inputs temporarily.
- **Data Visualizations**: Interactive charts powered by Plotly for insights by department and employee level.

---

## 📂 Features

- 📈 KPI dashboard: Top performers, underperformers, key metrics
- 🧑‍💼 Employee profile lookup and analysis
- 📝 Add new evaluation with live recommendations
- 📄 Generate printable PDF performance reports
- 📉 Department-wise comparison charts (bar/pie)
- 📧 Email alert generation using pre-filled `mailto:` links

---

## 🗃️ Data Requirement

https://www.kaggle.com/datasets/mexwell/employee-performance-and-productivity-data/data
Extended_Employee_Performance_and_Productivity_Data.csv


