import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import base64
# ========== SETUP ==========
st.set_page_config(
    page_title="Employee Analytics Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .risk-card {
        border-left: 4px solid #ef4444;
        padding: 1rem;
        background: #fef2f2;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .promotion-card {
        border-left: 4px solid #10b981;
        padding: 1rem;
        background: #f0fdf4;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .training-card {
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        background: #eff6ff;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .performer-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        height: 220px;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATA LOADING ==========
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Extended_Employee_Performance_and_Productivity_Data.csv")
        
        # Data cleaning
        df['Hire_Date'] = pd.to_datetime(df['Hire_Date'], errors='coerce')
        df['Tenure'] = (pd.Timestamp.now() - df['Hire_Date']).dt.days / 365.25
        
        # Ensure numeric columns
        numeric_cols = ['Performance_Score', 'Monthly_Salary', 'Work_Hours_Per_Week', 
                       'Projects_Handled', 'Overtime_Hours', 'Sick_Days', 
                       'Team_Size', 'Training_Hours', 'Promotions', 
                       'Employee_Satisfaction_Score']
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create categories
        df['Performance_Category'] = pd.cut(
            df['Performance_Score'],
            bins=[0, 2.5, 3.5, 5],
            labels=['Low', 'Medium', 'High']
        )
        
        # Calculate Productivity Score (custom metric)
        df['Productivity_Score'] = (
            0.4 * df['Performance_Score'] + 
            0.3 * (df['Projects_Handled'] / df['Projects_Handled'].max()) +
            0.2 * (df['Training_Hours'] / df['Training_Hours'].max()) +
            0.1 * (df['Employee_Satisfaction_Score'] / 10)
        ) * 100
        
        return df.dropna()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("No data loaded. Please check your data file.")
    st.stop()

# ========== DASHBOARD PAGE ==========
def dashboard_page():
    st.title("📊 Executive Dashboard")
    
    # KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Employees", len(df))
    with col2:
        st.metric("Avg Performance", f"{df['Performance_Score'].mean():.1f}/5")
    with col3:
        st.metric("Avg Satisfaction", f"{df['Employee_Satisfaction_Score'].mean():.1f}/10")
    with col4:
        st.metric("Avg Productivity", f"{df['Productivity_Score'].mean():.1f}")
    
    st.markdown("---")
    
    # Top 5 Performers in Cards
    st.subheader("🏆 Top 5 Performers")
    top_performers = df.sort_values('Performance_Score', ascending=False).head(5)
    
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_performers.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div class="performer-card">
                <h4 style="margin-top:0;color:#3b82f6">#{i+1}</h4>
                <p><b>{row['Employee_ID']}</b></p>
                <p>{row.get('Name','')}</p>
                <p>{row['Department']}</p>
                <p>Performance: <b>{row['Performance_Score']:.1f}/5</b></p>
                <p>Productivity: <b>{row['Productivity_Score']:.1f}</b></p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Department Productivity Comparison
    st.subheader("📊 Department Comparison")
    
    # Metric selection
    metric_options = {
        'Productivity_Score': 'Productivity Score',
        'Performance_Score': 'Performance Score',
        'Projects_Handled': 'Projects Handled',
        'Training_Hours': 'Training Hours',
        'Employee_Satisfaction_Score': 'Satisfaction Score',
        'Overtime_Hours': 'Overtime Hours',
        'Sick_Days': 'Sick Days',
        'Promotions': 'Promotions',
        'Tenure': 'Tenure (Years)'
    }
    
    selected_metric = st.selectbox(
        "Select metric to compare:",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )
    
    # Department selection
    all_depts = df['Department'].unique().tolist()
    selected_depts = st.multiselect(
        "Select departments to compare:",
        options=all_depts,
        default=all_depts,
        help="Select 'All Departments' or choose specific ones"
    )
    
    # Filter and prepare data
    dept_stats = df[df['Department'].isin(selected_depts)].groupby('Department').agg({
        'Productivity_Score': 'mean',
        'Performance_Score': 'mean',
        'Projects_Handled': 'mean',
        'Training_Hours': 'mean',
        'Employee_Satisfaction_Score': 'mean',
        'Overtime_Hours': 'mean',
        'Sick_Days': 'mean',
        'Promotions': 'mean',
        'Tenure': 'mean'
    }).reset_index()
    
    # Create comparison chart
    if not dept_stats.empty:
        fig = px.bar(
            dept_stats.sort_values(selected_metric, ascending=False),
            x='Department',
            y=selected_metric,
            color='Department',
            text_auto='.2f',
            title=f"{metric_options[selected_metric]} by Department",
            labels={'Department': '', selected_metric: metric_options[selected_metric]},
            height=500
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title=metric_options[selected_metric],
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No departments selected for comparison")

# ========== EMPLOYEE ANALYSIS PAGE ==========
def employee_analysis_page():
    st.title("👤 Employee Analysis")
    
    # Employee Selector
    employee = st.selectbox("Select Employee", df['Employee_ID'])
    emp_data = df[df['Employee_ID'] == employee].iloc[0]
    
    # Profile Card
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Employee Profile")
        st.write(f"**ID:** {emp_data['Employee_ID']}")
        st.write(f"**Department:** {emp_data['Department']}")
        st.write(f"**Job Title:** {emp_data['Job_Title']}")
        st.write(f"**Tenure:** {emp_data['Tenure']:.1f} years")
        st.write(f"**Performance:** {emp_data['Performance_Score']}/5 ({emp_data['Performance_Category']})")
    
    # Recommendations
    with col2:
        st.subheader("Recommendations")
        
        # Resignation Risk
        risk_score = min(100, max(0, 
            30 * (10 - emp_data['Employee_Satisfaction_Score']) / 10 +
            20 * (5 - emp_data['Performance_Score']) / 5 +
            15 * emp_data['Overtime_Hours'] / 40 -
            10 * emp_data['Promotions'] -
            25 * emp_data['Tenure'] / 10
        ))
        
        if risk_score > 50:
            st.error(f"🚨 High resignation risk: {risk_score:.0f}%")
            st.write(f"""
            - Conduct retention interview
            - Review workload (current overtime: {emp_data['Overtime_Hours']} hrs/week)
            - Consider recognition or promotion
            """)
        
        # Promotion Potential
        if (emp_data['Performance_Score'] >= 4 and 
            emp_data['Tenure'] >= 2 and 
            emp_data['Training_Hours'] >= 30):
            st.success(f"🌟 Promotion candidate (Score: {(emp_data['Performance_Score']*10 + emp_data['Tenure']*5):.1f}/100)")
            st.write("""
            - Eligible for next level
            - Consider leadership training
            """)
        
        # Training Needs
        if emp_data['Training_Hours'] < 20 or emp_data['Performance_Score'] < 3:
            st.warning(f"📚 Training recommended (Current: {emp_data['Training_Hours']} hrs)")
            st.write(f"""
            - Needs {max(20, 40 - emp_data['Training_Hours'])} additional hours
            - Skills development program
            - Mentorship opportunity
            """)

# ========== NEW EVALUATION PAGE ==========
def new_evaluation_page():
    st.title("✨ New Employee Evaluation")
    
    # Initialize session state to store evaluation results
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = None
    
    with st.form("evaluation_form"):
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name (optional)")
        with col2:
            existing_ids = df['Employee_ID'].unique()
            sample_id = existing_ids[0] if len(existing_ids) > 0 else "1"
            employee_id = st.text_input("Employee ID*", value="", 
                                      help=f"Must be unique numeric ID (like {sample_id})")
        
        col3, col4 = st.columns(2)
        with col3:
            department = st.selectbox("Department*", df['Department'].unique())
        with col4:
            job_title = st.text_input("Job Title*")
        
        st.subheader("Productivity Metrics")
        col5, col6 = st.columns(2)
        with col5:
            work_hours = st.slider("Work Hours/Week*", 20, 80, 40)
            projects = st.number_input("Projects Handled*", 1, 10, 3)
            training = st.number_input("Training Hours*", 0, 100, 20)
        with col6:
            overtime = st.number_input("Overtime Hours*", 0, 40, 5)
            sick_days = st.number_input("Sick Days*", 0, 30, 2)
            satisfaction = st.slider("Satisfaction (1-10)*", 1, 10, 7)
        
        remote_freq = st.selectbox(
            "Remote Work Frequency*",
            options=["Never", "Rarely", "Sometimes", "Often", "Always"]
        )
        
        submitted = st.form_submit_button("Evaluate Employee")
        
        if submitted:
            # Validate required fields
            if not all([employee_id, department, job_title]):
                st.error("Please fill all required fields (*)")
                st.stop()
            
            # Validate employee ID is numeric
            if not employee_id.isdigit():
                st.error("Employee ID must be a numeric value")
                st.stop()
                
            # Validate employee ID doesn't exist
            if employee_id in df['Employee_ID'].astype(str).values:
                st.error(f"Employee ID {employee_id} already exists. Please use a unique ID.")
                st.stop()
            
            # Predict performance score (1-5 scale)
            performance = min(5, max(1,
                0.4 * (work_hours / 50) * 5 +
                0.3 * (projects / 5) * 5 +
                0.2 * (training / 50) * 5 +
                0.1 * (satisfaction / 10) * 5
            ))
            
            # Calculate risk factors
            risk_score = min(100, max(0,
                40 * (10 - satisfaction) / 10 +
                30 * (5 - performance) / 5 +
                20 * overtime / 40 -
                10 * 0  # New employee has 0 promotions
            ))
            
            # Store results in session state
            st.session_state.evaluation_results = {
                'name': name,
                'employee_id': employee_id,
                'department': department,
                'job_title': job_title,
                'remote_freq': remote_freq,
                'performance': performance,
                'risk_score': risk_score,
                'work_hours': work_hours,
                'projects': projects,
                'training': training,
                'overtime': overtime,
                'sick_days': sick_days,
                'satisfaction': satisfaction
            }
            
            # Display results
            st.success("Evaluation Complete!")
            
            # Score Visualization
            col7, col8 = st.columns(2)
            with col7:
                st.metric("Predicted Performance", f"{performance:.1f}/5")
                st.progress(performance / 5)
                
            with col8:
                st.metric("Resignation Risk", f"{risk_score:.0f}%")
                st.progress(risk_score / 100)
            
            # Detailed Recommendations
            st.subheader("📋 Actionable Recommendations")
            
            # Performance Recommendations
            if performance >= 4:
                st.success("**High Performer Detected** 🌟")
                st.write("- Fast-track for leadership training")
                st.write("- Consider special projects assignment")
                st.write("- Eligible for early promotion review")
            elif performance <= 2:
                st.error("**Performance Concerns** ⚠️")
                st.write("- Implement 90-day improvement plan")
                st.write("- Assign mentor for weekly check-ins")
                st.write("- Required training: 40+ hours")
            else:
                st.info("**Solid Performer** 👍")
                st.write("- Recommend skill development plan")
                st.write("- Regular performance feedback")
            
            # Risk Mitigation
            if risk_score > 60:
                st.error("**High Attrition Risk** 🚨")
                st.write("- Schedule retention interview immediately")
                st.write("- Review workload balance")
                st.write("- Consider spot bonus/recognition")
            elif risk_score > 30:
                st.warning("**Moderate Risk** 🔍")
                st.write("- Monitor engagement closely")
                st.write("- Conduct stay interviews quarterly")
            
            # Training Needs
            if training < 15:
                st.warning("**Training Deficiency** 📚")
                st.write(f"- Minimum {25-training} additional training hours needed")
                st.write("- Enroll in foundational skills program")
            
            # Workload Analysis
            if overtime > 10:
                st.warning("**Excessive Overtime** ⏳")
                st.write("- Review workload distribution")
                st.write("- Consider temporary assistance")
            
            # Health Indicators
            if sick_days > 5:
                st.warning("**Elevated Sick Days** 🤒")
                st.write("- Recommend wellness check")
                st.write("- Review work-life balance")
    
    # PDF Generation Button (outside the form)
    if st.session_state.evaluation_results:
        if st.button("📄 Generate PDF Report"):
            results = st.session_state.evaluation_results
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Set font and styles
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Employee Evaluation Report", 0, 1, 'C')
            pdf.ln(10)
            
            # Report metadata
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
            pdf.cell(0, 6, f"Employee ID: {results['employee_id']}", 0, 1)
            if results['name']:
                pdf.cell(0, 6, f"Employee Name: {results['name']}", 0, 1)
            pdf.ln(5)
            
            # Section 1: Basic Information
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "1. Basic Information", 'B', 1)
            pdf.set_font("Arial", '', 10)
            pdf.cell(40, 6, "Department:", 0, 0)
            pdf.cell(0, 6, results['department'], 0, 1)
            pdf.cell(40, 6, "Job Title:", 0, 0)
            pdf.cell(0, 6, results['job_title'], 0, 1)
            pdf.cell(40, 6, "Remote Work:", 0, 0)
            pdf.cell(0, 6, results['remote_freq'], 0, 1)
            pdf.ln(5)
            
            # Section 2: Evaluation Scores
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "2. Evaluation Scores", 'B', 1)
            pdf.set_font("Arial", '', 10)
            
            # Performance Score
            pdf.cell(60, 6, "Predicted Performance Score:", 0, 0)
            pdf.cell(0, 6, f"{results['performance']:.1f}/5", 0, 1)
            
            # Risk Score
            pdf.cell(60, 6, "Resignation Risk Score:", 0, 0)
            pdf.cell(0, 6, f"{results['risk_score']:.0f}%", 0, 1)
            pdf.ln(5)
            
            # Section 3: Key Metrics
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "3. Key Metrics", 'B', 1)
            pdf.set_font("Arial", '', 10)
            
            metrics = [
                ("Work Hours/Week", str(results['work_hours'])),
                ("Projects Handled", str(results['projects'])),
                ("Training Hours", str(results['training'])),
                ("Overtime Hours", str(results['overtime'])),
                ("Sick Days", str(results['sick_days'])),
                ("Satisfaction Score", f"{results['satisfaction']}/10")
            ]
            
            for label, value in metrics:
                pdf.cell(60, 6, f"{label}:", 0, 0)
                pdf.cell(0, 6, value, 0, 1)
            
            pdf.ln(5)
            
            # Section 4: Recommendations
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "4. Recommendations", 'B', 1)
            pdf.set_font("Arial", '', 10)
            
            # Performance Recommendations
            if results['performance'] >= 4:
                pdf.multi_cell(0, 6, "High Performer Detected:\n- Fast-track for leadership training\n- Consider special projects assignment\n- Eligible for early promotion review")
            elif results['performance'] <= 2:
                pdf.multi_cell(0, 6, "Performance Concerns:\n- Implement 90-day improvement plan\n- Assign mentor for weekly check-ins\n- Required training: 40+ hours")
            else:
                pdf.multi_cell(0, 6, "Solid Performer:\n- Recommend skill development plan\n- Regular performance feedback")
            
            pdf.ln(3)
            
            # Risk Mitigation
            if results['risk_score'] > 60:
                pdf.multi_cell(0, 6, "High Attrition Risk:\n- Schedule retention interview immediately\n- Review workload balance\n- Consider spot bonus/recognition")
            elif results['risk_score'] > 30:
                pdf.multi_cell(0, 6, "Moderate Risk:\n- Monitor engagement closely\n- Conduct stay interviews quarterly")
            
            pdf.ln(3)
            
            # Training Needs
            if results['training'] < 15:
                pdf.multi_cell(0, 6, f"Training Deficiency:\n- Minimum {25-results['training']} additional training hours needed\n- Enroll in foundational skills program")
            
            # Workload Analysis
            if results['overtime'] > 10:
                pdf.multi_cell(0, 6, "Excessive Overtime:\n- Review workload distribution\n- Consider temporary assistance")
            
            # Health Indicators
            if results['sick_days'] > 5:
                pdf.multi_cell(0, 6, "Elevated Sick Days:\n- Recommend wellness check\n- Review work-life balance")
            
            # Footer
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 6, "This report was generated automatically by the Employee Analytics Suite", 0, 1, 'C')
            
            # Generate PDF and create download link
            pdf_output = pdf.output(dest='S').encode('latin1')
            b64 = base64.b64encode(pdf_output).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="employee_evaluation_{results["employee_id"]}.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)
# ========== RISK & GROWTH PAGE ==========
def risk_growth_page():
    st.title("⚠️ Employee Risk & Growth Insights")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Resignation Risk", 
        "Promotion Candidates", 
        "Training Needs", 
        "Sick Leave Alerts"
    ])
    
    def create_mailto_button(employee_id, subject, body):
        with st.expander(f"✉️ Email {employee_id}"):
            recipient = st.text_input("Recipient Email", key=f"recipient_{employee_id}")
            email_body = st.text_area("Email Body", value=body, height=200, key=f"body_{employee_id}")
            # Replace newlines and spaces separately
            encoded_body = email_body.replace('\n', '%0D%0A').replace(' ', '%20')
            mailto_link = f"mailto:{recipient}?subject={subject}&body={encoded_body}"
            st.markdown(
                f'<a href="{mailto_link}" target="_blank">'
                '<button style="background-color:#4CAF50;color:white;padding:8px 16px;border:none;border-radius:4px;">'
                'Open in Email Client</button></a>', 
                unsafe_allow_html=True
            )
    
    with tab1:
        st.subheader("Employees at Risk of Resignation")
        at_risk = df.sort_values('Employee_Satisfaction_Score').head(10)
        
        for _, emp in at_risk.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="risk-card">
                    <h4>{emp['Employee_ID']} ({emp['Department']})</h4>
                    <p>Satisfaction: {emp['Employee_Satisfaction_Score']}/10 | 
                    Performance: {emp['Performance_Score']}/5 | 
                    Tenure: {emp['Tenure']:.1f} yrs</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Resignation email template
                resignation_body = f"""Dear {emp.get('Name', 'Employee')},

We've noticed some indicators that you might be considering other opportunities. We value your contributions and would like to understand how we can better support you.

Some areas we'd like to discuss:
- Your current satisfaction level ({emp['Employee_Satisfaction_Score']}/10)
- Workload balance (current overtime: {emp['Overtime_Hours']} hrs/week)
- Career development opportunities

Would you be available for a conversation this week to discuss how we can improve your experience?

Best regards,
[Your Name]
[Your Position]"""
                
                create_mailto_button(
                    emp['Employee_ID'],
                    f"Retention Discussion - {emp['Employee_ID']}",
                    resignation_body
                )
        
    with tab2:
        st.subheader("Promotion Recommendations")
        promotions = df[(df['Performance_Score'] >= 4) & (df['Tenure'] >= 2)].sort_values('Performance_Score', ascending=False).head(10)
        
        for _, emp in promotions.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="promotion-card">
                    <h4>{emp['Employee_ID']} ({emp['Job_Title']})</h4>
                    <p>Performance: {emp['Performance_Score']}/5 | 
                    Tenure: {emp['Tenure']:.1f} yrs | 
                    Training: {emp['Training_Hours']} hrs</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Promotion email template
                promotion_body = f"""Dear HR Team,

I'm recommending {emp.get('Name', emp['Employee_ID'])} for promotion consideration based on their outstanding performance and contributions.

Key highlights:
- Consistent high performance ({emp['Performance_Score']}/5)
- Tenure with company: {emp['Tenure']:.1f} years
- Completed {emp['Training_Hours']} training hours
- Currently handling {emp['Projects_Handled']} projects

Suggested next steps:
1. Schedule promotion review meeting
2. Discuss potential new role and responsibilities
3. Plan announcement timeline

Please let me know your availability to discuss.

Best regards,
[Your Name]
[Your Position]"""
                
                create_mailto_button(
                    emp['Employee_ID'],
                    f"Promotion Recommendation - {emp['Employee_ID']}",
                    promotion_body
                )
    
    with tab3:
        st.subheader("Training Recommendations")
        training_needs = df[(df['Training_Hours'] < 20) | (df['Performance_Score'] < 3)].sort_values('Training_Hours').head(10)
        
        for _, emp in training_needs.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="training-card">
                    <h4>{emp['Employee_ID']} ({emp['Department']})</h4>
                    <p>Training Hours: {emp['Training_Hours']} | 
                    Performance: {emp['Performance_Score']}/5 | 
                    Projects: {emp['Projects_Handled']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Training email template
                training_body = f"""Dear {emp.get('Name', 'Employee')},

As part of our ongoing development program, I'd like to recommend some training opportunities that would help support your growth.

Current status:
- Training hours completed: {emp['Training_Hours']}
- Performance score: {emp['Performance_Score']}/5
- Projects handled: {emp['Projects_Handled']}

Recommended training areas:
1. Core skills development (estimated 20 hours)
2. Advanced {emp['Department']} methodologies
3. Professional effectiveness workshops

Would you be available to discuss a personalized training plan?

Best regards,
[Your Name]
[Your Position]"""
                
                create_mailto_button(
                    emp['Employee_ID'],
                    f"Training Recommendation - {emp['Employee_ID']}",
                    training_body
                )
    
    with tab4:
        st.subheader("Sick Leave Alerts")
        sick_alerts = df.sort_values('Sick_Days', ascending=False).head(10)
        
        for _, emp in sick_alerts.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="risk-card">
                    <h4>{emp['Employee_ID']} ({emp['Job_Title']})</h4>
                    <p>Sick Days: {emp['Sick_Days']} | 
                    Last Promotion: {emp['Promotions']} yrs ago | 
                    Satisfaction: {emp['Employee_Satisfaction_Score']}/10</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Wellness email template
                wellness_body = f"""Dear {emp.get('Name', 'Employee')},

I wanted to check in as I noticed you've had {emp['Sick_Days']} sick days recently. Your health and wellbeing are important to us.

We'd like to offer:
- A confidential discussion with HR about any support you might need
- Information about our wellness programs
- Flexible work options if helpful

Please know we're here to support you. Would you be available for a conversation?

Best regards,
[Your Name]
[Your Position]"""
                
                create_mailto_button(
                    emp['Employee_ID'],
                    f"Wellness Check-In - {emp['Employee_ID']}",
                    wellness_body
                )

# ========== MAIN APP ==========
def main():
    st.sidebar.title("Employee Analytics Suite")
    page = st.sidebar.radio("Navigation", [
        "Dashboard", 
        "Employee Analysis", 
        "New Evaluation",
        "Risk & Growth Insights"
    ])
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Employee Analysis":
        employee_analysis_page()
    elif page == "New Evaluation":
        new_evaluation_page()
    elif page == "Risk & Growth Insights":
        risk_growth_page()

if __name__ == "__main__":
    main()
