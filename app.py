import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
import base64 
import os # Added for file path handling

# --- Configuration and Aesthetics (High-Contrast Dark Look) ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define Plotly Theme for Dark Mode Consistency
PLOTLY_THEME = 'plotly_dark'

# --- Behaviour Profile Plan and Data Constants ---

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    # Special roles that require manual name input
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

MOCK_STUDENTS = [
    {'id': 'stu_jp_high', 'name': 'Marcus A.', 'area': 'JP', 'grade': 'R', 'teacher': 'Smith', 'edid': 'JP001A', 'dob': '2019-03-15'},
    {'id': 'stu_jp_low', 'name': 'Chloe T.', 'area': 'JP', 'grade': 'Y2', 'teacher': 'Davids', 'edid': 'JP002T', 'dob': '2017-11-20'},
    {'id': 'stu_py_high', 'name': 'Noah K.', 'area': 'PY', 'grade': 'Y5', 'teacher': 'Williams', 'edid': 'PY003K', 'dob': '2014-07-01'},
    {'id': 'stu_py_low', 'name': 'Leah S.', 'area': 'PY', 'grade': 'Y6', 'teacher': 'Brown', 'edid': 'PY004S', 'dob': '2013-09-10'},
    {'id': 'stu_sy_high', 'name': 'Ethan B.', 'area': 'SY', 'grade': 'Y9', 'teacher': 'Green', 'edid': 'SY005B', 'dob': '2010-01-25'},
    {'id': 'stu_sy_low', 'name': 'Mia P.', 'area': 'SY', 'grade': 'Y10', 'teacher': 'Clark', 'edid': 'SY006P', 'dob': '2009-04-05'},
]

BEHAVIORS_BPP = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Out of Seat', 'Non-Compliance', 'Physical Aggression (Staff)']
WINDOW_OF_TOLERANCE = ['Hypo-aroused', 'Hyper-aroused', 'Coping'] 
SETTINGS = ['Classroom', 'Gate', 'Yard', 'Playground', 'Toilets', 'Admin', 'Spill out', 'Kitchen', 'Library', 'Excursion', 'Swimming', 'Bus/Van', 'Specialist Lesson']
SUPPORT_TYPES = ['Unstructured', 'Small Group', 'Independent', 'Large Group', 'Peer', '1:1']
ANTECEDENTS_NEW = ['Peer Interaction', 'Tired', 'Hungry', 'Transition', 'Routine Change', 'Environmental Disturbance', 'Limit Setting', 'Group Work', 'Adult Demand', 'No Medication', 'Task Demand', 'Other']
FUNCTIONAL_HYPOTHESIS = ['Seek/Get Something', 'Avoid/Escape Something', 'Self Stimulation']
FUNCTION_PRIMARY = ['Sensory', 'Social', 'Tangible/Activity']
FUNCTION_SECONDARY = ['Peer', 'Adult', '-'] 
RISK_LEVELS = [1, 2, 3, 4, 5] # 1=Low, 5=Extreme

CONSEQUENCES = ['Redirection/Prompt', 'Time-Out (Brief)', 'Ignored (Planned)', 'Preferred Activity Access']
INTERVENTION_EFFECTIVENESS = ['Highly Effective', 'Moderately Effective', 'Ineffective', 'Worsened Behaviour']
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
HOW_TO_RESPOND_DEFAULT = "No detailed plan required or specified."


# --- NEW: Background Image Utility Functions ---

def get_base64_of_image(file_path):
    """Reads an image file and returns its base64 encoded string."""
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def set_landing_page_background(image_file):
    """
    Sets the given image as a full-page, fixed background using custom CSS.
    
    MODIFIED: Removed white box styling, fixed duplicate titles, and updated box styling.
    """
    try:
        # Use a relative path if the file is in the same directory
        b64 = get_base64_of_image(image_file)
        
        # Define a consistent blue-green color for the buttons
        BUTTON_BG_COLOR = "#008080"  # A nice Teal/Blue-Green
        BUTTON_TEXT_COLOR = "#FFFFFF"
        
        css = f"""
        <style>
        /* 1. Set the fixed, full-page background image */
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed; 
        }}
        
        /* 2. Make the main Streamlit content area transparent on the landing page */
        .main {{
            background-color: transparent !important;
            padding-top: 0 !important; /* Start content higher */
        }}
        
        /* NEW: Remove duplicate Streamlit title/header element */
        header {{
            display: none !important;
        }}

        /* 3. Custom button styling for landing page elements (Blue/Green) */
        /* Target primary buttons within the main content of the landing page */
        .stButton button[kind="primary"] {{
            background-color: {BUTTON_BG_COLOR} !important;
            color: {BUTTON_TEXT_COLOR} !important;
            border-color: {BUTTON_BG_COLOR} !important;
            transition: all 0.2s ease;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4); /* Strong shadow for visibility */
        }}

        .stButton button[kind="primary"]:hover {{
            background-color: #00AAAA !important; /* Slightly lighter on hover */
            border-color: #00AAAA !important;
            color: {BUTTON_TEXT_COLOR} !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.6);
        }}
        
        /* 4. Style for content placed over the background to improve readability */
        /* Apply a subtle text shadow for better contrast */
        #landing-page-content h2, #landing-page-content h3 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        /* 5. Placeholder for the three images/columns (UPDATED COLOR AND HOVER) */
        .image-placeholder {{
            background-color: rgba(44, 62, 80, 0.7); /* Darker Yellow-Gray / Slate (e.g., #2c3e50) */
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            height: 250px;
            color: white;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            cursor: pointer; /* Hint at interactivity */
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        
        /* Interactive Hover Effect */
        .image-placeholder:hover {{
            background-color: rgba(52, 73, 94, 0.8); /* Slightly darker on hover */
            border: 2px solid #00FFFF; /* Bright cyan border for interactivity */
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.6);
        }}

        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback if the image isn't found in the expected path
        st.warning(f"⚠️ Background image '{image_file}' not found. Please ensure it's in the same directory as app.py for the professional look.")
    except Exception as e:
        st.warning(f"⚠️ Error loading background image: {e}")

# --- Utility Functions (Existing) ---

def get_session_from_time(t):
    """Determines the session based on time of day."""
    if time(8, 30) <= t <= time(11, 0):
        return 'Morning (8:30-11:00)'
    elif time(11, 1) <= t <= time(13, 0):
        return 'Middle (11:01-1:00)'
    elif time(13, 1) <= t <= time(15, 0):
        return 'Afternoon (1:01-3:00)'
    else:
        return 'Outside Hours'

def get_random_time():
    """Generates a random time between 8:30 and 15:00."""
    start = datetime(2000, 1, 1, 8, 30, 0)
    end = datetime(2000, 1, 1, 15, 0, 0)
    random_seconds = random.randint(0, int((end - start).total_seconds()))
    return (start + timedelta(seconds=random_seconds)).time()

def get_time_slot(t):
    """Converts time to the nearest half-hour slot for heatmap."""
    # MODIFIED: Ensure time is a datetime.time object
    if isinstance(t, str):
        t = datetime.strptime(t, '%H:%M').time()
        
    minutes = t.minute
    hour = t.hour
    if minutes < 30:
        return f"{hour:02d}:00"
    else:
        # Note: This means 10:30-10:59 falls into 10:30 slot. 
        # The next hour's 00:00-00:29 falls into the next hour's :00 slot.
        return f"{hour:02d}:30"

def generate_mock_abch_outcomes():
    """Generates random outcomes for critical incidents (for mock data)."""
    outcomes = {
        'outcome_send_home': random.choice([True, False]),
        'outcome_leave_area': random.choice([True, False]),
        'outcome_assault': random.choice([True, False]),
        'outcome_property_damage': random.choice([True, False]),
        'outcome_staff_injury': random.choice([True, False]),
        'outcome_sapol_callout': random.choice([True, False]),
        'outcome_ambulance': random.choice([True, False]),
    }
    if not any(outcomes.values()):
        outcomes[random.choice(list(outcomes.keys()))] = True
    
    return outcomes

# --- FIX: Apply caching to data generation to prevent blank screen errors ---
@st.cache_resource
def generate_mock_incidents():
    """Generates a list of mock incident dictionaries with new BPP fields and outcomes."""
    incidents = []
    
    # 1. High Incident Student (Marcus A. - stu_jp_high) - 15 incidents
    for i in range(1, 16):
        incident_date = (datetime.now() - pd.Timedelta(days=random.randint(1, 45))).strftime('%Y-%m-%d')
        incident_time = get_random_time()
        
        is_high_risk = random.choice([True, True, False])
        
        behaviour = random.choice(['Verbal Refusal', 'Elopement', 'Physical Aggression (Staff)']) if i % 3 == 0 else random.choice(BEHAVIORS_BPP)
        risk = random.choice([4, 5]) if is_high_risk else random.choice([1, 2, 3])
        
        incident_data = {
            'id': str(uuid.uuid4()),
            'student_id': 'stu_jp_high',
            'date': incident_date,
            'time': incident_time.strftime('%H:%M'),
            'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
            'session': get_session_from_time(incident_time),
            'behaviour': behaviour,
            'window_of_tolerance': random.choice(['Hyper-aroused']) if is_high_risk else random.choice(WINDOW_OF_TOLERANCE),
            'setting': random.choice(['Classroom', 'Yard', 'Gate', 'Admin']), # Added more variety
            'support_type': random.choice(['1:1', 'Small Group']) if is_high_risk else random.choice(SUPPORT_TYPES),
            'antecedent': random.choice(['Task Demand', 'Limit Setting', 'Adult Demand', 'Peer Interaction', 'Transition']), # Added more variety
            'func_hypothesis': random.choice(['Avoid/Escape Something', 'Seek/Get Something']),
            'func_primary': random.choice(FUNCTION_PRIMARY),
            'func_secondary': random.choice(FUNCTION_SECONDARY),
            'risk_level': risk,
            'consequence': random.choice(CONSEQUENCES), 
            'effectiveness': random.choice(['Ineffective', 'Worsened Behaviour']) if is_high_risk else random.choice(['Highly Effective', 'Moderately Effective']),
            'logged_by': 's1',
            'other_staff': ['s_trt:Jane Doe'] if i % 5 == 0 else [],
            'is_abch_completed': is_high_risk,
            'context': f"HIGH-DETAIL LOG: {behaviour} during {incident_time.strftime('%H:%M')}. Requires immediate follow-up." if is_high_risk else "Basic log captured. No detailed context entered.",
            'notes': f"Staff noted lack of sleep prior to incident {i}.",
            'how_to_respond': "Use a 5-step break card system." if is_high_risk else HOW_TO_RESPOND_DEFAULT
        }
        
        if is_high_risk:
            incident_data.update(generate_mock_abch_outcomes())
        else:
            incident_data.update({
                'outcome_send_home': False, 'outcome_leave_area': False, 
                'outcome_assault': False, 'outcome_property_damage': False, 
                'outcome_staff_injury': False, 'outcome_sapol_callout': False, 
                'outcome_ambulance': False,
            })
            
        incidents.append(incident_data)
    
    # --- START FIX FOR TYPERROR: 'datetime.time' and 'datetime.timedelta' (Approx. line 255) ---
    # The original code at this line caused a TypeError because 'datetime.time' cannot be 
    # subtracted by 'timedelta'. The fix is to use datetime.combine() with a date 
    # (datetime.now().date()) before performing the subtraction.
    
    # This block represents the problematic incident from the traceback, now corrected.
    incident_time_for_fix = get_random_time()
    incidents.append({
        'id': str(uuid.uuid4()),
        'student_id': 'stu_jp_high', # Example student assignment
        'date': (datetime.now() - pd.Timedelta(days=random.randint(1, 45))).strftime('%Y-%m-%d'),
        # CORRECTED LINE: Use datetime.combine() to allow timedelta subtraction
        'time': (datetime.combine(datetime.now().date(), incident_time_for_fix) - timedelta(minutes=random.randint(1, 5))).strftime('%H:%M'), 
        'day': datetime.strptime((datetime.now() - pd.Timedelta(days=random.randint(1, 45))).strftime('%Y-%m-%d'), '%Y-%m-%d').strftime('%A'),
        'session': get_session_from_time(incident_time_for_fix),
        'behaviour': 'Pacing', 
        'window_of_tolerance': 'Hypo-aroused',
        'setting': 'Hallway',
        'support_type': random.choice(SUPPORT_TYPES),
        'antecedent': random.choice(ANTECEDENTS_NEW),
        'func_hypothesis': random.choice(FUNCTIONAL_HYPOTHESIS),
        'func_primary': random.choice(FUNCTION_PRIMARY),
        'func_secondary': random.choice(FUNCTION_SECONDARY),
        'risk_level': random.choice(RISK_LEVELS),
        'consequence': random.choice(CONSEQUENCES), 
        'effectiveness': random.choice(INTERVENTION_EFFECTIVENESS),
        'logged_by': 's1',
        'other_staff': [],
        'is_abch_completed': False,
        'context': "Mock incident created to resolve the TypeError.",
        'notes': None,
        'how_to_respond': HOW_TO_RESPOND_DEFAULT,
        'outcome_send_home': False, 'outcome_leave_area': False, 
        'outcome_assault': False, 'outcome_property_damage': False, 
        'outcome_staff_injury': False, 'outcome_sapol_callout': False, 
        'outcome_ambulance': False,
    })
    # --- END FIX BLOCK ---

    # 2. Other students (3 incidents each)
    for student in MOCK_STUDENTS:
        if student['id'] == 'stu_jp_high':
            continue

        for i in range(1, 4):
            incident_date = (datetime.now() - pd.Timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')
            incident_time = get_random_time()
            
            incident_data = {
                'id': str(uuid.uuid4()),
                'student_id': student['id'],
                'date': incident_date,
                'time': incident_time.strftime('%H:%M'),
                'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
                'session': get_session_from_time(incident_time),
                'behaviour': random.choice(BEHAVIORS_BPP),
                'window_of_tolerance': random.choice(WINDOW_OF_TOLERANCE),
                'setting': random.choice(SETTINGS),
                'support_type': random.choice(SUPPORT_TYPES),
                'antecedent': random.choice(ANTECEDENTS_NEW),
                'func_hypothesis': random.choice(FUNCTIONAL_HYPOTHESIS),
                'func_primary': random.choice(FUNCTION_PRIMARY),
                'func_secondary': random.choice(FUNCTION_SECONDARY),
                'risk_level': random.choice(RISK_LEVELS),
                'consequence': random.choice(CONSEQUENCES), 
                'effectiveness': random.choice(INTERVENTION_EFFECTIVENESS),
                'logged_by': random.choice(['s1', 's2', 's3']),
                'other_staff': [],
                'is_abch_completed': False,
                'context': "Basic log captured. No detailed context entered.",
                'notes': None,
                'how_to_respond': HOW_TO_RESPOND_DEFAULT
            }
            incident_data.update({
                'outcome_send_home': False, 'outcome_leave_area': False, 
                'outcome_assault': False, 'outcome_property_damage': False, 
                'outcome_staff_injury': False, 'outcome_sapol_callout': False, 
                'outcome_ambulance': False,
            })
            incidents.append(incident_data)
            
    return incidents


# --- Session State Initialization ---

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'
if 'current_role' not in st.session_state:
    st.session_state.current_role = None 
if 'students' not in st.session_state:
    st.session_state.students = MOCK_STUDENTS
if 'incidents' not in st.session_state:
    # Use the cached function to initialize the data only once
    st.session_state.incidents = generate_mock_incidents() 
if 'staff' not in st.session_state:
    st.session_state.staff = MOCK_STAFF
if 'selected_student_id' not in st.session_state:
    st.session_state.selected_student_id = None
if 'mode' not in st.session_state:
    st.session_state.mode = 'home'
if 'temp_log_area' not in st.session_state:
    st.session_state.temp_log_area = None
if 'temp_incident_data' not in st.session_state:
    st.session_state.temp_incident_data = None
if 'abch_chronology' not in st.session_state:
    st.session_state.abch_chronology = []


# --- Utility Functions ---

def navigate_to(page_name, role=None, mode='home', student_id=None):
    """Sets the session state to change the current page, role, and mode."""
    st.session_state.current_page = page_name
    if role:
        st.session_state.current_role = role
    st.session_state.mode = mode
    st.session_state.selected_student_id = student_id
    st.session_state.temp_log_area = None
    st.rerun()

def get_students_by_area(area):
    """Filters the student list by area (JP, PY, SY)."""
    return [s for s in st.session_state.students if s['area'] == area]

def get_student_by_id(student_id):
    """Retrieves a single student dictionary by ID."""
    return next((s for s in st.session_state.students if s['id'] == student_id), None)

def get_incidents_by_student(student_id):
    """Filters incidents for a specific student."""
    # Convert to DataFrame for easy filtering and sorting
    df = pd.DataFrame(st.session_state.incidents)
    df_student = df[df['student_id'] == student_id].sort_values(by=['date', 'time'], ascending=False)
    # Convert back to list of dictionaries for use in the app
    return df_student.to_dict('records')


def staff_header(role):
    """Renders the standard header for staff areas."""
    st.sidebar.markdown(f"## 👤 {role} Area Dashboard")
    st.sidebar.markdown(f"**Current User Role:** {role}")
    st.sidebar.markdown("---")

    # Navigation options grouped by role
    nav_options = {
        'JP': {"🏠 Home / Student List": 'home'},
        'PY': {"🏠 Home / Student List": 'home'},
        'SY': {"🏠 Home / Student List": 'home'},
        'ADM': {
            "🏠 Admin Dashboard": 'home',
            "👥 Staff Management": 'staff_management',
            "➕ Add New Staff": 'add_staff',
            "📄 All Incidents Log": 'all_incidents'
        }
    }
    
    col_nav, col_back = st.sidebar.columns([3, 2])
    
    # Render main navigation for the role
    cols = st.columns(len(nav_options.get(role, {})))
    for idx, (label, mode_name) in enumerate(nav_options.get(role, {}).items()):
        if cols[idx].button(label, key=f"nav_{mode_name}_{role}"):
            navigate_to('staff_area', role=role, mode=mode_name)

    # Back button always visible
    with col_back:
        if st.button("⬅ Home", key="back_to_landing_from_staff_area"):
            navigate_to('landing')
    st.sidebar.markdown("---")


def render_risk_level_info():
    """Renders the risk level matrix for user guidance."""
    st.markdown("##### 🚨 Behaviour Risk Level Guide")
    risk_data = [
        (1, "Low Risk", "Minor non-compliance, brief distraction, low-level disruption.", "Simple redirection or verbal prompt."),
        (2, "Moderate Risk", "Repeated refusal, sustained low-level defiance, brief elopement (easily retrieved).", "Planned ignoring, re-engagement strategy, 1:1 check-in."),
        (3, "Substantial Risk", "Verbal aggression, property destruction (minor), sustained non-compliance, elopement (requires active search).", "Tactical retreat, use of protective break space, referral for support."),
        (4, "High Risk", "Physical aggression (no injury), significant property destruction, self-injurious behaviour (low severity).", "Physical intervention (only if trained and necessary), emergency call for assistance."),
        (5, "Extreme Risk", "Physical aggression resulting in injury, substantial risk to the health and safety of others. Pattern of persistent Level 4.", "Emergency intervention or hospitalization, long-term suspension or expulsion, and law enforcement involvement.")
    ]
    # Using markdown for a clear table structure
    st.markdown("""
| Level | Severity | Common Characteristics | Example Intervention/Impact |
| :---: | :--- | :--- | :--- |
""")
    for level, severity, characteristics, intervention in risk_data:
        st.markdown(f"| **{level}** | **{severity}** | {characteristics} | *{intervention}* |")
    st.markdown("---")


# --- Behaviour Profile Plan Content Generation and Download ---

def generate_bpp_report_content(student, latest_plan_incident, df):
    """
    Generates the structured text content for the full BPP report, incorporating 
    Trauma-Informed (Berry Street) and CPI models.
    """
    # 1. Gather Key Data Insights for the Summary
    total_incidents = len(df)
    abch_count = len(df[df['is_abch_completed'] == True])
    most_freq_behaviour = df['behaviour'].mode().iloc[0] if not df.empty else 'N/A'
    peak_risk = df['risk_level'].max() if not df.empty else 'N/A'
    
    # 2. Determine CPI Stage based on latest incident/max risk/mode
    cpi_stage = "Unknown"
    cpi_response = "N/A"
    
    if latest_plan_incident:
        # Check against latest incident data
        latest_behaviour = latest_plan_incident['behaviour']
        
        if latest_behaviour in ['Physical Aggression (Staff)', 'Self-Injurious Behaviour', 'Property Destruction'] or peak_risk >= 4:
            cpi_stage = "High-Risk: Acting Out (Danger)"
            cpi_response = "Nonviolent Physical Crisis Intervention (where appropriate) followed by Therapeutic Rapport to restore the relationship immediately after the crisis."
        elif latest_behaviour in ['Aggression (Peer)', 'Elopement', 'Verbal Refusal'] or peak_risk == 3:
            cpi_stage = "Peak Risk: Defensive"
            cpi_response = "Use Supportive language and Directive strategies (offering choices, clear limits) to guide the student toward an appropriate choice."
        else:
            cpi_stage = "Low-Risk: Questioning / Refusal"
            cpi_response = "Use Information Seeking and Challenging questions as opportunities for connection and teaching appropriate ways to communicate needs."
            
    # 3. Format 'How to Respond'
    how_to_respond_content = latest_plan_incident['how_to_respond'] if latest_plan_incident else HOW_TO_RESPOND_DEFAULT
    if how_to_respond_content and how_to_respond_content != HOW_TO_RESPOND_DEFAULT:
        # Format the text area content into a list if possible (assuming line breaks)
        action_steps = "\n".join([f"* {line.strip()}" for line in how_to_respond_content.split('\n') if line.strip()])
    else:
        action_steps = f"*{HOW_TO_RESPOND_DEFAULT}*"
        
    # --- Report Content Template ---
    content = f'''
# BEHAVIOUR PROFILE PLAN (BPP)
## Student: {student['name']} (EDID: {student['edid']})
**Date Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Review Date:** {datetime.now().date() + pd.Timedelta(days=30)}

---

## 1. Summary of Clinical Findings and Data Analysis

| Metric | Detail |
| :--- | :--- |
| **Total Incidents Logged** | {total_incidents} |
| **Critical Incidents (ABCH)** | {abch_count} |
| **Most Frequent Behaviour** | {most_freq_behaviour} |
| **Peak Risk Level Observed** | {peak_risk} |
| **Primary Hypothesized Function** | {latest_plan_incident['func_hypothesis'] if latest_plan_incident else 'N/A'} |
| **Primary Antecedent (Trigger)** | {latest_plan_incident['antecedent'] if latest_plan_incident else 'N/A'} |
| **Window of Tolerance State** | {latest_plan_incident['window_of_tolerance'] if latest_plan_incident else 'N/A'} |

---

## 2. Comprehensive Action Plan (How to Respond)

This section outlines the immediate and strategic responses derived from the last critical incident analysis.

### Primary De-escalation Strategy (The 'H' in ABCH)
**Last Updated:** {latest_plan_incident['date'] if latest_plan_incident else 'N/A'}
{action_steps}

### Crisis Prevention Institute (CPI) Protocol
The student is currently demonstrating behaviours aligning with the **{cpi_stage}** stage of the CPI Verbal Escalation Continuum.
* **Recommended Staff Response:** {cpi_response}
* **Goal:** Maintain safety and use *Supportive* and *Directive* nonverbal strategies to prevent escalation.

---

## 3. Trauma-Informed (Berry Street) Strategy
The core strategy focuses on **De-escalation and Rhythms** (calming the nervous system) and **Relationships** (re-establishing safety).
* **Focus during escalation:** Ensure a calm, predictable presence. Use neutral body language and provide choices to restore a sense of control.
* **Focus post-incident:** Prioritize therapeutic rapport. This involves a planned, brief check-in to repair the relationship and process the event, reinforcing that the student is safe and valued.
* **Focus for Proactive Teaching:** Identify and create an area of contribution within the classroom to shift the student's sense of self from 'problem' to 'valued member'.

---

## 4. Chronological Incident Context (Last Detailed Log)

### Incident Date: {latest_plan_incident['date'] if latest_plan_incident else 'N/A'}
### Final Summary: {latest_plan_incident['context'] if latest_plan_incident else 'N/A'}

*This Behaviour Profile Plan is a dynamic document and must be reviewed after any further critical incident or after 30 calendar days.*
'''
    return content

def get_download_link(file_content, filename):
    """Generates a downloadable file link for Streamlit."""
    b64 = base64.b64encode(file_content.encode()).decode()
    # Create the download link in Markdown
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">⬇ Download Full Behaviour Profile Plan (.txt)</a>'


# --- Plotly Graph Enhancement ---

def render_data_analysis(student, df):
    """ Renders the comprehensive data analysis and clinical summary section with enhanced Plotly charts. """
    st.subheader(f"📊 Comprehensive Data Analysis for: **{student['name']}**")
    
    # --- Data Preprocessing for Analysis ---
    df['time_obj'] = pd.to_datetime(df['time'], format='%H:%M').dt.time # NEW: Time object
    df['time_slot'] = df['time_obj'].apply(get_time_slot) # NEW: Half-hour slot
    df['is_abch_completed_label'] = df['is_abch_completed'].apply(lambda x: 'Critical Incident (ABCH) - Activated' if x else 'Basic Log')
    
    # Get the latest plan incident for BPP review
    latest_plan_incident = next((i for i in df.to_dict('records') if i.get('is_abch_completed') == True), df.to_dict('records')[0] if not df.empty else None)
    
    if df.empty:
        st.info("No incident data available for this student yet.")
        return

    # --- BPP Review and Download ---
    st.markdown("### 📄 Behaviour Profile Plan (BPP) Status")
    
    col_bpp1, col_bpp2 = st.columns([3, 2])
    
    with col_bpp1:
        st.markdown(f"**Latest BPP-Update Incident:** {latest_plan_incident['date'] if latest_plan_incident else 'N/A'}")
        st.markdown(f"**Primary Antecedent:** {latest_plan_incident['antecedent'] if latest_plan_incident else 'N/A'}")
        st.markdown(f"**Primary Function:** {latest_plan_incident['func_hypothesis'] if latest_plan_incident else 'N/A'}")

    with col_bpp2:
        if latest_plan_incident:
            report_content = generate_bpp_report_content(student, latest_plan_incident, df)
            filename = f"BPP_Report_{student['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            st.markdown(get_download_link(report_content, filename), unsafe_allow_html=True)
            
    st.markdown("---")
    
    # --- Row 1: Frequency, Severity, Location ---
    col_graph1, col_graph2, col_graph3 = st.columns(3)
    
    # 1. FREQUENCY GRAPH (Incidents over time)
    with col_graph1:
        st.markdown("##### 📈 Incidents Over Time")
        df_time = df.groupby('date')['id'].count().reset_index(name='Count')
        df_time['date'] = pd.to_datetime(df_time['date'])
        
        fig_time = px.line(
            df_time, 
            x='date', 
            y='Count', 
            title='Incidents Per Day', 
            template=PLOTLY_THEME, 
            markers=True
        )
        fig_time.update_xaxes(dtick="M1", tickformat="%b %d")
        fig_time.update_traces(line=dict(color='#3498DB', width=3))
        st.plotly_chart(fig_time, use_container_width=True)

    # 2. SEVERITY GRAPH (Risk Level Distribution)
    with col_graph2:
        st.markdown("##### 🔥 Severity and ABCH Activation")
        df_severity = df.groupby(['risk_level', 'is_abch_completed_label'])['id'].count().reset_index(name='Count')
        
        fig_severity = px.bar(
            df_severity, 
            x='risk_level', 
            y='Count', 
            color='is_abch_completed_label',
            title='Risk Level Distribution vs. ABCH Activation',
            template=PLOTLY_THEME,
            labels={'risk_level': 'Risk Level (1=Low, 5=Extreme)', 'Count': 'Incident Count', 'is_abch_completed_label': 'ABCH Activation'},
            category_orders={"risk_level": sorted(df['risk_level'].unique())},
            color_discrete_map={'Critical Incident (ABCH) - Activated': '#FF5733', 'Basic Log': '#5B5E63'}, # Orange/Red for Critical
            barmode='stack'
        )
        fig_severity.update_xaxes(dtick=1)
        fig_severity.update_traces(marker_line_width=1, marker_line_color='gray')
        st.plotly_chart(fig_severity, use_container_width=True)
    
    # 3. LOCATION GRAPH (NEW Requirement)
    with col_graph3:
        st.markdown("##### 📍 Incidents by Setting (Location)")
        location_counts = df['setting'].value_counts().reset_index(name='Count')
        location_counts.columns = ['Setting', 'Count']
        fig_location = px.bar(
            location_counts, 
            x='Setting', 
            y='Count', 
            title='Incident Frequency by Location',
            template=PLOTLY_THEME,
            labels={'Setting': 'Setting', 'Count': 'Incident Count'},
            color_discrete_sequence=['#2ECC71'] # Green
        )
        fig_location.update_traces(marker_line_width=1, marker_line_color='gray')
        fig_location.update_layout(xaxis={'categoryorder':'total descending', 'tickangle': -45})
        st.plotly_chart(fig_location, use_container_width=True)
        
    st.markdown("---")
    
    # --- Row 2: Time/Session, Behaviour, Function ---
    col_graph4, col_graph5, col_graph6 = st.columns(3)
    
    # 4. TIME OF DAY GRAPH (Heatmap)
    with col_graph4:
        st.markdown("##### ⏰ Time and Day Heatmap")
        df_heatmap = df.groupby(['day', 'time_slot'])['id'].count().reset_index(name='Count')
        
        # Order days for display
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_heatmap['day'] = pd.Categorical(df_heatmap['day'], categories=day_order, ordered=True)
        df_heatmap = df_heatmap.sort_values('day')
        
        fig_heatmap = px.density_heatmap(
            df_heatmap,
            x='time_slot', 
            y='day', 
            z='Count', 
            title='Incident Heatmap by Time Slot and Day',
            template=PLOTLY_THEME,
            color_continuous_scale="Plasma",
            labels={'time_slot': 'Time Slot', 'day': 'Day of Week', 'z': 'Incident Count'}
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    # 5. BEHAVIOUR GRAPH (Pareto/Bar Chart)
    with col_graph5:
        st.markdown("##### 💥 Behaviour Frequency (Top 5)")
        behaviour_counts = df['behaviour'].value_counts().head(5).reset_index(name='Count')
        behaviour_counts.columns = ['Behaviour', 'Count']
        
        fig_behaviour = px.bar(
            behaviour_counts, 
            x='Behaviour', 
            y='Count', 
            title='Most Frequent Behaviours',
            template=PLOTLY_THEME,
            color='Count',
            color_continuous_scale='Mint',
            labels={'Count': 'Incident Count'}
        )
        fig_behaviour.update_traces(marker_line_width=1, marker_line_color='gray')
        fig_behaviour.update_layout(xaxis={'categoryorder':'total descending', 'tickangle': -45})
        st.plotly_chart(fig_behaviour, use_container_width=True)
        
    # 6. FUNCTION GRAPH (Hypothesis Distribution)
    with col_graph6:
        st.markdown("##### 💡 Hypothesized Function")
        func_counts = df['func_hypothesis'].value_counts().reset_index(name='Count')
        func_counts.columns = ['Function', 'Count']
        
        fig_func = px.pie(
            func_counts, 
            names='Function', 
            values='Count', 
            title='Function of Behaviour Distribution',
            template=PLOTLY_THEME,
            hole=.3,
            color_discrete_sequence=px.colors.sequential.Agsunset
        )
        fig_func.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig_func, use_container_width=True)
        
    st.markdown("---")
    
    # --- Clinical Deep Dive: Outcomes ---
    df_outcomes = df[df['is_abch_completed'] == True].copy()
    if not df_outcomes.empty:
        st.markdown("### ⚠️ Clinical Deep Dive: Critical Incident Outcomes")
        
        col_out1, col_out2 = st.columns(2)
        
        # Outcomes by Count
        outcome_columns = [col for col in df_outcomes.columns if col.startswith('outcome_')]
        outcome_counts = df_outcomes[outcome_columns].sum().reset_index(name='Count')
        outcome_counts.columns = ['Outcome', 'Count']
        # Clean up column names for display
        outcome_counts['Outcome'] = outcome_counts['Outcome'].str.replace('outcome_', '').str.replace('_', ' ').str.title()
        
        with col_out1:
            st.markdown("##### Total Count of Severe Outcomes (ABCH Logs Only)")
            fig_outcomes = px.bar(
                outcome_counts.sort_values('Count', ascending=False),
                x='Outcome', 
                y='Count', 
                title='Frequency of Incident Outcomes',
                template=PLOTLY_THEME,
                color_discrete_sequence=['#E74C3C'] # Red
            )
            fig_outcomes.update_layout(xaxis={'categoryorder':'total descending', 'tickangle': -45})
            st.plotly_chart(fig_outcomes, use_container_width=True)

        # Behaviours leading to assault
        with col_out2:
            assault_by_behaviour = df_outcomes[df_outcomes['outcome_assault'] == True].groupby('behaviour')['id'].count().reset_index(name='Assault Count')
            
            if not assault_by_behaviour.empty:
                st.markdown("##### 🚩 Behaviours that Escalated to Documented Assault (ABCH Logs Only)")
                fig_assault = px.bar(
                    assault_by_behaviour, 
                    x='behaviour', 
                    y='Assault Count', 
                    title='Assault Outcomes by Behaviour Type',
                    template=PLOTLY_THEME,
                    labels={'behaviour': 'Observed Behaviour', 'Assault Count': 'Count of Assault Outcomes'},
                    color_discrete_sequence=['#F39C12']
                )
                fig_assault.update_traces(marker_line_width=1, marker_line_color='gray')
                fig_assault.update_layout(xaxis={'categoryorder':'total descending', 'tickangle': -45})
                st.plotly_chart(fig_assault, use_container_width=True)
            else:
                st.info("No incidents logged with documented assault outcomes.")

    st.markdown("---")
    
    # --- Clinical Interpretation Section ---
    st.markdown("### 🧠 Clinical Interpretation & Next Steps")
    
    # 1. Summary of Findings
    st.markdown("#### 1. Summary of Data Findings")
    st.markdown(f"""
- **Primary Concern:** **{most_freq_behaviour}** is the most frequent behaviour, suggesting a targeted intervention is needed.
- **Timing:** Incidents peak on **{df['day'].mode().iloc[0] if not df.empty else 'N/A'}** during the **{df['session'].mode().iloc[0] if not df.empty else 'N/A'}**.
- **Context:** The highest concentration of risk incidents occurs in the **{df[df['risk_level'] >= 4]['setting'].mode().iloc[0] if not df[df['risk_level'] >= 4].empty else 'N/A'}** setting.
- **Function:** The most hypothesized function is **{latest_plan_incident['func_hypothesis'] if latest_plan_incident else 'N/A'}**, indicating the intervention must teach a replacement behaviour that achieves this function appropriately.
""")

    # 2. Recommended Proactive Strategy (Replicating BPP)
    st.markdown("#### 2. Proactive Strategy Focus (Berry Street)")
    st.markdown("""
The focus should be on **Relationships** and **Rhythms**. Specifically:
- **Relational Shift:** Systematically identify and create an area of contribution within the classroom to shift the student's sense of self from 'problem' to 'valued member'.
""")
    
    # 3. CPI Staging and Protocol
    st.markdown("### 3. Crisis Prevention Institute (CPI) Protocol Staging")
    
    # Replicate CPI logic for consistency
    if latest_plan_incident:
        if most_freq_behaviour in ['Physical Aggression (Staff)', 'Self-Injurious Behaviour', 'Property Destruction'] or peak_risk >= 4:
            cpi_stage = "High-Risk: Acting Out (Danger)"
            cpi_response = "Nonviolent Physical Crisis Intervention (where appropriate) followed by Therapeutic Rapport to restore the relationship immediately after the crisis."
        elif most_freq_behaviour in ['Aggression (Peer)', 'Elopement', 'Verbal Refusal'] or peak_risk == 3:
            cpi_stage = "Peak Risk: Defensive"
            cpi_response = "Use Supportive language and Directive strategies (offering choices, clear limits) to guide the student toward an appropriate choice."
        else:
            cpi_stage = "Low-Risk: Questioning / Refusal"
            cpi_response = "Use Information Seeking and Challenging questions as opportunities for connection and teaching appropriate ways to communicate needs."
            
        st.markdown(f"The student's data indicates a pattern aligning with the **{cpi_stage}** stage.")
        st.markdown(f"* **Recommended Protocol:** {cpi_response}")
    else:
        st.info("No data available to determine CPI Staging.")


# --- Form Rendering Functions (Quick Log, ABCH, General Log) ---

def render_abch_chronology_form():
    """Renders the form for logging the sequential A-B-C steps for a critical incident."""
    st.markdown("##### 📝 Chronological Incident Log (A-B-C Steps)")
    with st.form("abch_chronology_form", clear_on_submit=False):
        
        # If chronology exists, display it
        if st.session_state.abch_chronology:
            st.markdown("###### Incident Timeline (Current Logged Layers)")
            for i, entry in enumerate(st.session_state.abch_chronology):
                st.markdown(f"**Layer {i+1}** ({entry['time']}): **L:** {entry['location'] or 'N/A'}; **A:** {entry['antecedent'] or 'N/A'}; **B:** {entry['behaviour'] or 'N/A'}; **C:** {entry['consequence'] or 'N/A'}")
            st.markdown("---")

        st.markdown("###### New Incident Layer")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            time_val = st.time_input("Time of Layer", datetime.now().time(), key="chrono_time")
        with col_t2:
            location = st.selectbox("L: Location of Layer", options=['-'] + SETTINGS, key="chrono_location")
            
        col_abc1, col_abc2, col_abc3 = st.columns(3)
        with col_abc1:
            antecedent = st.selectbox("A: Antecedent/Trigger (What happened just before)", options=['-'] + ANTECEDENTS_NEW, key="chrono_antecedent")
        with col_abc2:
            behaviour = st.selectbox("B: Observed Behaviour", options=['-'] + BEHAVIORS_BPP, key="chrono_behaviour")
        with col_abc3:
            consequence = st.selectbox("C: Consequence/Staff Response", options=['-'] + CONSEQUENCES, key="chrono_consequence")
            
        context = st.text_area("Context/Detailed Observation (Optional)", key="chrono_context", height=100, placeholder="E.g., Staff used proximity and verbal prompt. Student responded with property destruction.")
        
        submitted = st.form_submit_button("Add Layer to Chronology")
        
        if submitted:
            # Append the new layer to the chronology list in session state
            st.session_state.abch_chronology.append({
                'time': time_val.strftime('%H:%M'),
                'location': location if location != '-' else None,
                'antecedent': antecedent if antecedent != '-' else None,
                'behaviour': behaviour if behaviour != '-' else None,
                'consequence': consequence if consequence != '-' else None,
                'context': context if context.strip() else None
            })
            # Re-run the app to clear the form and display the new layer
            st.rerun()

def save_new_incident(incident_data, student, is_abch=False, return_role='direct'):
    """Appends a new incident to the session state and navigates appropriately."""
    
    # 1. Generate core metadata
    incident_data.update({
        'id': str(uuid.uuid4()),
        'student_id': student['id'],
        'day': datetime.strptime(incident_data['date'], '%Y-%m-%d').strftime('%A'),
        'session': get_session_from_time(datetime.strptime(incident_data['time'], '%H:%M').time()),
        'is_abch_completed': is_abch,
        'notes': None # Placeholder for now, can be updated later
    })
    
    # 2. Ensure all outcome fields are present (defaulting to False if not an ABCH log)
    if not is_abch:
        incident_data.update({
            'outcome_send_home': False, 'outcome_leave_area': False, 
            'outcome_assault': False, 'outcome_property_damage': False, 
            'outcome_staff_injury': False, 'outcome_sapol_callout': False, 
            'outcome_ambulance': False,
            'how_to_respond': incident_data.get('how_to_respond', HOW_TO_RESPOND_DEFAULT),
            'context': incident_data.get('context', "Basic log captured. No detailed context entered.")
        })
    
    # 3. Append to incidents list
    st.session_state.incidents.append(incident_data)
    
    # 4. Success message and navigation
    st.success(f"Incident Logged Successfully for {student['name']}!")
    
    # Navigate to student analysis page if staff area, or landing page if direct log
    if return_role in ['JP', 'PY', 'SY', 'ADM']:
        navigate_to('staff_area', role=return_role, mode='analysis', student_id=student['id'])
    else: # Default for 'direct' log
        navigate_to('landing')


def render_abch_follow_up_form(student):
    """Renders the A-B-C-H Follow-up form (Step 2) for critical incidents."""
    
    # Use the preliminary data saved from the previous form submission
    prelim_data = st.session_state.temp_incident_data
    
    # Determine the return role/page based on where the user came from
    return_role = st.session_state.current_role
    return_mode = 'analysis' if return_role in ['JP', 'PY', 'SY', 'ADM'] else 'landing'
    
    if not prelim_data:
        # Fallback: Find the most recent, non-completed incident for the student
        incidents = get_incidents_by_student(student['id'])
        target_incident = next((i for i in reversed(incidents) if i['is_abch_completed'] == False and i['risk_level'] >= 3), None)
        
        if target_incident:
            prelim_data = target_incident
            st.warning("No live incident data found. Loading the most recent high-risk incident for ABCH completion.")
        else:
            st.error("Cannot find a preliminary incident log to complete the ABCH follow-up.")
            if st.button("⬅ Back to Home"):
                navigate_to('landing')
            return

    st.markdown(f"## 📝 Critical Incident ABCH Follow-up (Step 2 of 2)")
    st.markdown(f"**Student:** **{student['name']}** | **Date:** {prelim_data['date']} | **Time:** {prelim_data['time']}")
    st.markdown(f"**Initial Behaviour:** {prelim_data['behaviour']} | **Initial Risk:** Level {prelim_data['risk_level']}")
    st.markdown("---")

    # --- CHRONOLOGY INPUT ---
    render_abch_chronology_form()
    st.markdown("---")
    
    with st.form("abch_final_form"):
        # --- Final WOT and Action Plan (H) ---
        st.markdown("#### Final BPP Refinement and Action Plan (H)")
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            refined_wot = st.selectbox(
                "Window of Tolerance State (Student state during escalation)", 
                options=WINDOW_OF_TOLERANCE, 
                key="abch_wot",
                index=WINDOW_OF_TOLERANCE.index(prelim_data['window_of_tolerance']) if prelim_data['window_of_tolerance'] in WINDOW_OF_TOLERANCE else 0
            )
        with col_h2:
            func_hypothesis = st.selectbox(
                "Primary Function (H: Hypothesized/Confirmed Function)", 
                options=FUNCTIONAL_HYPOTHESIS, 
                key="abch_func_hypothesis",
                index=FUNCTIONAL_HYPOTHESIS.index(prelim_data['func_hypothesis']) if prelim_data['func_hypothesis'] in FUNCTIONAL_HYPOTHESIS else 0
            )
            
        # The key Action Plan field
        how_to_respond = st.text_area(
            "H: HOW TO RESPOND (New/Updated Action Plan for staff - Mandatory)",
            height=200, 
            key="abch_how_to_respond",
            placeholder="E.g., 1. Use visual schedule; 2. Offer two choices; 3. Ignore verbal aggression; 4. Redirection."
        )
        final_summary = st.text_area(
            "Final Clinical Summary / Root Cause Analysis (Mandatory)", 
            key="abch_final_notes", 
            height=150
        )

        # --- INTENDED OUTCOMES (REPLICATING THE SCREENSHOT TABLE) ---
        st.markdown("---")
        st.markdown("#### 📝 INTENDED OUTCOMES")
        col_left_table, col_right_table = st.columns([5, 5])
        
        with col_left_table:
            st.markdown("##### Incident Details & Outcomes Checklist (Required)")
            outcome_send_home = st.checkbox("Sent home", key="outcome_send_home", value=False)
            outcome_leave_area = st.checkbox("Required student to leave area (Exclusion)", key="outcome_leave_area", value=False)
            outcome_assault = st.checkbox("Physical assault (Student to Staff/Peer)", key="outcome_assault", value=False)
            outcome_property_damage = st.checkbox("Property damage (Significant)", key="outcome_property_damage", value=False)
            outcome_staff_injury = st.checkbox("Staff Injury (Required first aid/medical)", key="outcome_staff_injury", value=False)
            outcome_sapol_callout = st.checkbox("SAPOL Callout", key="outcome_sapol_callout", value=False)
            outcome_ambulance = st.checkbox("Ambulance Callout", key="outcome_ambulance", value=False)

        with col_right_table:
            st.markdown("##### Follow-up Required (Management Only)")
            st.text_area("Future Risk Plan: To be developed / reviewed:", key="safety_risk_plan", height=80, placeholder="Specify the next steps for RMP update.")
            st.text_area("Other outcomes to be pursued by Cowandilla Learning Centre Management:", key="cowandilla_management_outcomes", height=80)
            
        final_submitted = st.form_submit_button("Finalize and Save ABCH Log (Updates BPP)", type="primary")

        if final_submitted:
            if not how_to_respond:
                st.error("Submission blocked: Please complete the **H: HOW TO RESPOND (New/Updated Action Plan)** field.")
                return
            if not final_summary:
                st.error("Submission blocked: Please complete the **Final Clinical Summary / Root Cause Analysis** field.")
                return

            # 1. Compile chronological and clinical summary into final context
            final_context = "Chronological Log:\n"
            for i, entry in enumerate(st.session_state.abch_chronology):
                # Only include layers with at least one data point
                if entry['location'] or entry['context'] or entry['behaviour'] or entry['consequence']:
                    final_context += f"Layer {i+1} ({entry['time']}): L: {entry['location'] or 'N/A'}; A: {entry['antecedent'] or 'N/A'}; B: {entry['behaviour'] or 'N/A'}; C: {entry['consequence'] or 'N/A'}\n"
                    if entry['context']:
                        final_context += f"   - Context: {entry['context']}\n"
            
            final_context += f"\n---\nFinal Clinical Summary:\n{final_summary}"

            # 2. Compile final incident data
            final_incident_data = prelim_data.copy()
            final_incident_data.update({
                # H step updates
                'func_hypothesis': func_hypothesis,
                'window_of_tolerance': refined_wot,
                'how_to_respond': how_to_respond,
                'context': final_context, # Final context replaces initial context
                'is_abch_completed': True,
                # Outcomes
                'outcome_send_home': outcome_send_home,
                'outcome_leave_area': outcome_leave_area,
                'outcome_assault': outcome_assault,
                'outcome_property_damage': outcome_property_damage,
                'outcome_staff_injury': outcome_staff_injury,
                'outcome_sapol_callout': outcome_sapol_callout,
                'outcome_ambulance': outcome_ambulance,
                # Management notes (stored in 'notes' field for simplicity)
                'notes': f"Safety Risk Plan: {st.session_state.safety_risk_plan}\nManagement Outcomes: {st.session_state.cowandilla_management_outcomes}"
            })

            # 3. Save the new, completed incident
            save_new_incident(final_incident_data, student, is_abch=True, return_role=return_role)
            
            # 4. Clear temporary state
            st.session_state.temp_incident_data = None
            st.session_state.abch_chronology = []

            # st.rerun() is called inside save_new_incident


def render_incident_log_form(student, is_abch_step=False, role='direct'):
    """Renders the general incident log form (Step 1 or Quick Log)."""
    
    st.markdown(f"#### Log Incident for **{student['name']}**")
    
    with st.form("incident_log_form"):
        # --- Time and Date ---
        col_date, col_time = st.columns(2)
        with col_date:
            date_val = st.date_input("Date of Incident", datetime.now().date(), key="inc_date")
        with col_time:
            time_val = st.time_input("Time of Incident", datetime.now().time(), key="inc_time")

        auto_session = get_session_from_time(time_val)
        session_options = ['Morning (8:30-11:00)', 'Middle (11:01-1:00)', 'Afternoon (1:01-3:00)', 'Outside Hours']
        if auto_session not in session_options:
            session_options.append(auto_session)

        col1, col2, col3 = st.columns(3)
        with col1:
            behaviour = st.selectbox("Observed Behaviour", options=BEHAVIORS_BPP, key="inc_behaviour")
        with col2:
            antecedent = st.selectbox("A: Antecedent (Trigger)", options=ANTECEDENTS_NEW, key="inc_antecedent")
        with col3:
            session = st.selectbox("Session", options=session_options, index=session_options.index(auto_session), key="inc_session")

        col4, col5 = st.columns(2)
        with col4:
            setting = st.selectbox("Location (Setting)", options=SETTINGS, key="inc_setting")
        with col5:
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES, key="inc_support_type")
            
        col6, col7 = st.columns(2)
        with col6:
            # Risk Level - determines whether ABCH follow-up is required
            risk_level = st.selectbox("Risk Level (1=Low, 5=Extreme)", options=RISK_LEVELS, key="inc_risk_level")
        with col7:
            consequence = st.selectbox("C: Consequence/Staff Response", options=CONSEQUENCES, key="inc_consequence")

        # --- Logged By Staff Selection ---
        st.markdown("---")
        st.markdown("#### Staff Logging")
        
        staff_options = {s['id']: s['name'] for s in st.session_state.staff}
        
        col_staff1, col_staff2 = st.columns(2)
        
        with col_staff1:
            logged_by_name = st.selectbox(
                "Logged By (Your Name/Role)", 
                options=list(staff_options.values()), 
                key="logged_by_name"
            )
            
            # Get the ID of the selected staff member
            logged_by_id = next((k for k, v in staff_options.items() if v == logged_by_name), None)
            staff_details = next((s for s in st.session_state.staff if s['id'] == logged_by_id), {})
            is_special_logged = staff_details.get('special', False)
            logged_by_name_override = None
            
            if is_special_logged:
                logged_by_name_override = st.text_input(
                    f"Enter your name for **{logged_by_name}**", 
                    key="logged_by_name_override", 
                    placeholder=f"E.g., Jane Doe (Logged as '{logged_by_id}: Jane Doe')"
                )
                if not logged_by_name_override:
                    st.error(f"Name required for special role: {logged_by_name}")
                    
        with col_staff2:
            st.markdown("Other Staff Involved (Check all that apply)")
            other_staff_ids = []
            for staff_id, name in staff_options.items():
                if staff_id == logged_by_id: # Skip the person logging
                    continue
                
                staff_details = next((s for s in st.session_state.staff if s['id'] == staff_id), {})
                
                if st.checkbox(name, key=f"other_staff_{staff_id}"):
                    if staff_details.get('special'):
                        special_name_input = st.text_input(
                            f"Enter name for **{name}**", 
                            key=f"other_staff_special_name_input_{staff_id}",
                            placeholder=f"E.g., Jane Doe (Logged as '{name}: Jane Doe')"
                        )
                        if special_name_input:
                            other_staff_ids.append(f"{staff_id}:{special_name_input}")
                    else:
                        other_staff_ids.append(staff_id)
        
        # --- Final logged_by ID construction ---
        final_logged_by_id = logged_by_id
        if is_special_logged and logged_by_name_override:
            final_logged_by_id = f"{logged_by_id}:{logged_by_name_override}"
        elif is_special_logged and not logged_by_name_override:
            # This case must be handled to block submission if the required field is empty
            pass

        # --- Risk and Follow-up ---
        st.markdown("---")
        # NEW RISK INFO FUNCTION HERE
        render_risk_level_info()
        # END NEW FUNCTION CALL
        
        # Non-ABCH specific fields
        st.markdown("#### Additional Details (For Low/Moderate Risk Logs)")
        
        col_func1, col_func2 = st.columns(2)
        with col_func1:
            func_hypothesis = st.selectbox("Primary Functional Hypothesis", options=FUNCTIONAL_HYPOTHESIS, key="inc_func_hypothesis")
        with col_func2:
            wot = st.selectbox("Window of Tolerance State", options=WINDOW_OF_TOLERANCE, key="inc_wot")
            
        effectiveness = st.selectbox("Intervention Effectiveness", options=INTERVENTION_EFFECTIVENESS, key="inc_effectiveness")
        context = st.text_area("Context/Detailed Observation (Optional)", key="inc_context", height=150, placeholder="E.g., Student was pacing after being asked to transition. Provided a choice of two tasks and student complied.")
        
        # This field is only relevant for Quick Logs, not for ABCH Step 1
        how_to_respond = HOW_TO_RESPOND_DEFAULT
        if risk_level < 3 and not is_abch_step:
            how_to_respond = st.text_area(
                "Basic Action/Response Plan (Optional)", 
                key="inc_how_to_respond_basic", 
                height=100,
                placeholder="E.g., Remind student of break card next time."
            )

        submit_label = "Save Basic Incident Log"
        if risk_level >= 3 and not is_abch_step:
            submit_label = "Save Log & Proceed to ABCH Follow-up (Mandatory)"

        submitted = st.form_submit_button(submit_label, type="primary")

        if submitted:
            # Form submission logic
            
            # Block submission for special roles if name override is empty
            if is_special_logged and not logged_by_name_override:
                # Error already displayed above
                return 

            # 1. Compile initial data
            initial_incident_data = {
                'date': date_val.strftime('%Y-%m-%d'),
                'time': time_val.strftime('%H:%M'),
                'behaviour': behaviour,
                'antecedent': antecedent,
                'setting': setting,
                'support_type': support_type,
                'risk_level': risk_level,
                'consequence': consequence,
                'func_hypothesis': func_hypothesis,
                'window_of_tolerance': wot,
                'effectiveness': effectiveness,
                'logged_by': final_logged_by_id,
                'other_staff': other_staff_ids,
                'context': context,
                'how_to_respond': how_to_respond if risk_level < 3 or is_abch_step else HOW_TO_RESPOND_DEFAULT,
            }
            
            if risk_level >= 3 and not is_abch_step:
                # High Risk: Save preliminary data and navigate to ABCH Step 2
                st.session_state.temp_incident_data = initial_incident_data
                navigate_to('abch_follow_up', student_id=student['id'], role=role)
            else:
                # Low/Moderate Risk: Save incident directly
                save_new_incident(initial_incident_data, student, is_abch=False, return_role=role)


def render_direct_log_form():
    """Renders the incident log form directly after selection from the landing page."""
    student = get_student_by_id(st.session_state.selected_student_id)
    if student:
        col_title, col_back = st.columns([4, 1])
        with col_title:
            st.markdown(f"## Quick Incident Log (Step 1)")
        with col_back:
            # If navigating back, clear the temporary direct log state
            if st.button("⬅ Change Student", key="back_to_direct_select_form"):
                st.session_state.temp_incident_data = None
                st.session_state.abch_chronology = []
                st.session_state.current_role = None
                navigate_to('landing')
        st.markdown("---")
        
        # We pass the role as 'direct' temporarily here so render_incident_log_form knows 
        # what to do on submission (return to landing page).
        render_incident_log_form(student)
    else:
        st.error("No student selected.")
        navigate_to('landing')

# --- Page Rendering Functions ---

def render_landing_page():
    """Renders the initial welcome and role selection page."""
    
    # 1. Apply the custom background image
    set_landing_page_background("image_cd111d.png") # Assumes this file is present
    
    st.markdown("<div id='landing-page-content'>", unsafe_allow_html=True)
    st.markdown("## Behaviour Support & Data Analysis Tool", unsafe_allow_html=True)
    st.markdown("### Please select your area or a student to log an incident.")
    st.markdown("---")

    col_role1, col_role2 = st.columns([1, 1])
    
    with col_role1:
        st.markdown("### 🧑‍💻 Staff Area Login")
        st.markdown("Access dashboards, student analysis, and BPP reports.")
        
        # Role selection buttons styled as primary buttons via CSS and type="primary")
        col_jp, col_py, col_sy, col_adm = st.columns(4)
        with col_jp:
            if st.button("Junior Primary (JP)", use_container_width=True, type="primary"):
                navigate_to('staff_area', role='JP', mode='home')
        with col_py:
            if st.button("Primary Years (PY)", use_container_width=True, type="primary"):
                navigate_to('staff_area', role='PY', mode='home')
        with col_sy:
            if st.button("Senior Years (SY)", use_container_width=True, type="primary"):
                navigate_to('staff_area', role='SY', mode='home')
        with col_adm:
            if st.button("Administration (ADM)", use_container_width=True, type="primary"):
                navigate_to('staff_area', role='ADM', mode='home')

    with col_role2:
        st.markdown("### ⚡ Quick Incident Log")
        st.markdown("Direct logging for immediate, on-the-spot data capture.")
        
        with st.form("quick_log_select_form", border=True):
            student_list = sorted([s['name'] for s in st.session_state.students])
            selected_name = st.selectbox(
                "Select Student", 
                options=['-- Select Student --'] + student_list,
                key="direct_log_student_select"
            )
            
            submitted = st.form_submit_button("Start Quick Log", type="primary")
            
            if submitted and selected_name != '-- Select Student --':
                selected_student = next((s for s in st.session_state.students if s['name'] == selected_name), None)
                if selected_student:
                    # Set the student ID and navigate to the quick log page.
                    navigate_to('quick_log', student_id=selected_student['id'])
                else:
                    st.error("Student not found.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_staff_area():
    """Renders the main staff dashboard, handling all modes."""
    role = st.session_state.current_role
    student_id = st.session_state.selected_student_id
    mode = st.session_state.mode
    staff_header(role)
    
    # -----------------------------------------------------
    # MODE: Home/Student List (for JP, PY, SY)
    # -----------------------------------------------------
    if mode == 'home' and role != 'ADM':
        st.subheader(f"Students in the **{role}** Area")
        area_students = get_students_by_area(role)
        
        if not area_students:
            st.warning("No students assigned to this area.")
            return

        cols = st.columns(len(area_students))
        for idx, student in enumerate(area_students):
            student_incidents = get_incidents_by_student(student['id'])
            incident_count = len(student_incidents)
            
            with cols[idx]:
                container = st.container(border=True)
                container.markdown(f"**{student['name']}**")
                container.write(f"Grade: **{student['grade']}**")
                container.write(f"Teacher: **{student['teacher']}**")
                container.write(f"Incidents: **{incident_count}**")
                
                if container.button("View Analysis & Log", key=f"view_analysis_{student['id']}", use_container_width=True):
                    navigate_to('staff_area', role=role, mode='analysis', student_id=student['id'])


    # -----------------------------------------------------
    # MODE: Admin Dashboard (for ADM)
    # -----------------------------------------------------
    elif mode == 'home' and role == 'ADM':
        st.subheader("System Administration Dashboard")
        
        total_incidents = len(st.session_state.incidents)
        detailed_logs = len([i for i in st.session_state.incidents if i['is_abch_completed']])
        total_staff = len(st.session_state.staff)
        
        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.metric("Total Incidents Logged", total_incidents)
        col_t2.metric("Detailed ABCH Logs", detailed_logs)
        col_t3.metric("Total Staff Accounts", total_staff)
        
        st.markdown("---")
        st.markdown("#### Top 5 Most Frequent Behaviours (All Students)")
        df_all = pd.DataFrame(st.session_state.incidents)
        
        if not df_all.empty:
            behaviour_counts = df_all['behaviour'].value_counts().head(5).reset_index()
            behaviour_counts.columns = ['Behaviour', 'Count']
            st.bar_chart(behaviour_counts, x='Behaviour', y='Count', use_container_width=True)
        else:
            st.info("No incident data available.")


    # -----------------------------------------------------
    # MODE: Student Analysis (for JP, PY, SY, ADM)
    # -----------------------------------------------------
    elif mode == 'analysis' and student_id:
        student = get_student_by_id(student_id)
        if student:
            st.subheader(f"Student Profile: **{student['name']}** ({student['edid']})")
            
            col_info1, col_info2, col_log = st.columns([1, 1, 1])
            with col_info1:
                st.info(f"**Area:** {student['area']} | **Grade:** {student['grade']}")
            with col_info2:
                st.info(f"**Teacher:** {student['teacher']} | **DOB:** {student['dob']}")
            with col_log:
                if st.button(f"➕ Log New Incident for {student['name']}", type="primary", use_container_width=True):
                    navigate_to('staff_area', role=role, mode='log', student_id=student['id'])

            st.markdown("---")
            
            # Render the analysis charts
            student_incidents = get_incidents_by_student(student_id)
            df_student = pd.DataFrame(student_incidents)
            render_data_analysis(student, df_student)
            

    # -----------------------------------------------------
    # MODE: Incident Log (for JP, PY, SY, ADM)
    # -----------------------------------------------------
    elif mode == 'log' and student_id:
        student = get_student_by_id(student_id)
        if student:
            st.markdown("## Log Incident (Step 1 of 2 if High Risk)")
            st.markdown("---")
            # Pass the staff role so the save function knows where to navigate back to
            render_incident_log_form(student, role=role)
        else:
            st.error("Student not found.")
            navigate_to('staff_area', role=role)


    # -----------------------------------------------------
    # MODE: ABCH Follow-up (Navigated from a high-risk log)
    # -----------------------------------------------------
    elif st.session_state.current_page == 'abch_follow_up' and student_id:
        student = get_student_by_id(student_id)
        if student:
            render_abch_follow_up_form(student)
        else:
            st.error("Student not found for ABCH follow-up.")
            navigate_to('landing')
            
    # -----------------------------------------------------
    # MODE: Staff Management / Add Staff (ADM Only - Placeholder)
    # -----------------------------------------------------
    elif mode == 'staff_management' and role == 'ADM':
        st.subheader("Staff Management (Placeholder)")
        st.write("Current Staff:")
        df_staff = pd.DataFrame(st.session_state.staff)
        st.dataframe(df_staff, hide_index=True)
        st.info("Staff management UI functionality to be implemented here.")

    elif mode == 'add_staff' and role == 'ADM':
        st.subheader("Add New Staff Account (Placeholder)")
        st.info("Form to add new staff members will go here.")
        
    # -----------------------------------------------------
    # MODE: All Incidents Log (ADM Only)
    # -----------------------------------------------------
    elif mode == 'all_incidents' and role == 'ADM':
        st.subheader("📄 Full Incident Log (All Students)")
        df_all = pd.DataFrame(st.session_state.incidents)
        
        # Merge student names into the log
        df_students = pd.DataFrame(MOCK_STUDENTS)[['id', 'name']]
        df_all = df_all.merge(df_students, left_on='student_id', right_on='id', how='left').drop(columns=['id_x', 'id_y'])
        
        # Select and reorder columns for display
        display_columns = ['date', 'time', 'name', 'risk_level', 'behaviour', 'antecedent', 'consequence', 'is_abch_completed', 'logged_by', 'setting']
        
        st.dataframe(
            df_all[display_columns].rename(columns={'name': 'Student', 'is_abch_completed': 'ABCH'}), 
            hide_index=True, 
            use_container_width=True
        )


# --- Main App Execution ---
def main():
    """The main function to drive the Streamlit application logic."""
    
    # Main routing logic
    if st.session_state.current_page == 'landing':
        render_landing_page()
    elif st.session_state.current_page == 'staff_area':
        render_staff_area()
    elif st.session_state.current_page == 'quick_log':
        render_direct_log_form()
    elif st.session_state.current_page == 'abch_follow_up':
        # This is a specific follow-up mode, which is handled here
        student = get_student_by_id(st.session_state.selected_student_id)
        if student:
            render_abch_follow_up_form(student)
        else:
            st.error("Cannot find student for ABCH follow-up.")
            navigate_to('landing')
    
if __name__ == '__main__':
    main()