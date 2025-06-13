# ICFAI Student Dashboard with Role-Based Authentication
# All data pulled from GitLab in real-time
import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="ICFAI Student Dashboard", layout="wide")

# --- Constants ---
GITLAB_API_URL = "https://code.swecha.org/api/v4"

# Handle missing GitLab token gracefully
try:
    GITLAB_TOKEN = st.secrets["Progress_tracker"]
    if GITLAB_TOKEN == "your_gitlab_token_here":
        st.warning("⚠️ Please configure your GitLab token in .streamlit/secrets.toml")
        GITLAB_TOKEN = None
except:
    st.warning("⚠️ GitLab token not found. Some features may not work. Please configure .streamlit/secrets.toml")
    GITLAB_TOKEN = None

headers = {
    "PRIVATE-TOKEN": GITLAB_TOKEN
} if GITLAB_TOKEN else {}

# --- User Authentication ---
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "name": "Administrator",
        "permissions": ["view_all", "manage_users", "analytics", "export_data"]
    },
    "techlead1": {
        "password": "tech123", 
        "role": "techlead",
        "name": "Technical Lead",
        "permissions": ["view_all", "analytics", "export_data"]
    },
    "faculty1": {
        "password": "faculty123",
        "role": "faculty", 
        "name": "Faculty Member 1",
        "assigned_batches": ["Batch1.csv"],
        "permissions": ["view_assigned", "attendance", "progress"]
    },
    "faculty2": {
        "password": "faculty123",
        "role": "faculty",
        "name": "Faculty Member 2", 
        "assigned_batches": ["batch2.csv"],
        "permissions": ["view_assigned", "attendance", "progress"]
    }
}

def authenticate(username, password):
    """Simple authentication function"""
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]
    return None

def has_permission(permission):
    """Check if current user has permission"""
    if "user" not in st.session_state:
        return False
    return permission in st.session_state.user.get("permissions", [])

def show_login():
    """Display login form"""
    st.title("🔐 ICFAI Dashboard Login")
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("### Please log in to continue")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_btn:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success(f"Welcome, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("Please enter both username and password")
    
    # Show demo credentials
    st.sidebar.markdown("### 🔑 Demo Credentials")
    st.sidebar.markdown("**Admin:**")
    st.sidebar.code("Username: admin\nPassword: admin123")
    st.sidebar.markdown("**Tech Lead:**") 
    st.sidebar.code("Username: techlead1\nPassword: tech123")
    st.sidebar.markdown("**Faculty:**")
    st.sidebar.code("Username: faculty1\nPassword: faculty123")

def show_user_info():
    """Show current user info in sidebar"""
    if "user" in st.session_state:
        user = st.session_state.user
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 Logged in as:** {user['name']}")
        st.sidebar.markdown(f"**🎭 Role:** {user['role'].title()}")
        
        if st.sidebar.button("🚪 Logout"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# --- GitLab API Functions ---
@st.cache_data(show_spinner=False, ttl=1800)  # Cache for 30 minutes
def check_file_in_project(project_path, file_path="README.md"):
    """Check if file exists in GitLab project"""
    if not GITLAB_TOKEN:
        # Return demo data when no token
        import random
        return random.choice([True, False])
    
    encoded_project = quote(project_path, safe="")
    encoded_file = quote(file_path, safe="")
    url = f"{GITLAB_API_URL}/projects/{encoded_project}/repository/files/{encoded_file}/raw"
    
    try:
        response = requests.get(url, headers=headers, params={"ref": "main"})
        return response.status_code == 200
    except:
        return False

@st.cache_data(show_spinner=False, ttl=1800)  # Cache for 30 minutes
def check_project_exists(project_path):
    """Check if GitLab project exists"""
    if not GITLAB_TOKEN:
        import random
        return random.choice([True, False])
    
    encoded_project = quote(project_path, safe="")
    url = f"{GITLAB_API_URL}/projects/{encoded_project}"
    
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except:
        return False

@st.cache_data(show_spinner=False, ttl=1800)  # Cache for 30 minutes
def check_multiple_tasks(username):
    """Check completion status of all 4 tasks"""
    if not GITLAB_TOKEN:
        # Return demo data when no token
        import random
        return {
            "readme": random.choice([True, False]),
            "ai_assistant": random.choice([True, False]), 
            "streamlit_app": random.choice([True, False]),
            "linux_install": random.choice([True, False])
        }
    
    tasks = {
        "readme": False,
        "ai_assistant": False,
        "streamlit_app": False, 
        "linux_install": False
    }
    
    try:
        # Task 1: README in profile repo
        profile_path = f"{username}/{username}"
        tasks["readme"] = check_file_in_project(profile_path, "README.md")
        
        # Task 2: AI Assistant project
        ai_project_path = f"{username}/ai-assistant"
        tasks["ai_assistant"] = check_project_exists(ai_project_path)
        
        # Task 3: Streamlit App project  
        streamlit_project_path = f"{username}/streamlit-app"
        tasks["streamlit_app"] = check_project_exists(streamlit_project_path)
        
        # Task 4: Linux Installation - check for documentation
        linux_project_path = f"{username}/linux-installation"
        tasks["linux_install"] = check_project_exists(linux_project_path)
        
    except Exception as e:
        pass
    
    return tasks

@st.cache_data(show_spinner=False)
def get_project_commits_count(project_path):
    """Get total commits count (activity indicator)"""
    if not GITLAB_TOKEN:
        # Return demo data when no token
        import random
        return random.randint(0, 15)
    
    encoded_project = quote(project_path, safe="")
    url = f"{GITLAB_API_URL}/projects/{encoded_project}/repository/commits"
    
    try:
        response = requests.get(url, headers=headers, params={"per_page": 100})
        if response.status_code == 200:
            return len(response.json())
        return 0
    except:
        return 0

@st.cache_data(show_spinner=False) 
def get_project_last_activity(project_path):
    """Get last activity date (attendance indicator)"""
    if not GITLAB_TOKEN:
        # Return demo data when no token
        import random
        from datetime import datetime, timedelta
        days_ago = random.randint(0, 30)
        demo_date = datetime.now() - timedelta(days=days_ago)
        return demo_date.strftime("%Y-%m-%d %H:%M")
    
    encoded_project = quote(project_path, safe="")
    url = f"{GITLAB_API_URL}/projects/{encoded_project}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            last_activity = data.get("last_activity_at", "N/A")
            if last_activity != "N/A":
                # Convert to readable format
                dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M")
            return "Never"
        return "N/A"
    except:
        return "N/A"

@st.cache_data(show_spinner=False)
def get_project_progress_score(project_path):
    """Calculate progress score based on various factors"""
    try:
        has_readme = check_file_in_project(project_path)
        commits_count = get_project_commits_count(project_path)
        
        # Simple scoring system
        score = 0
        if has_readme:
            score += 30  # README worth 30 points
        
        # Commits scoring (up to 70 points)
        if commits_count > 0:
            score += min(commits_count * 5, 70)
        
        return min(score, 100)  # Cap at 100
    except:
        return 0

# --- Load Batch Data ---
def load_batch_data(csv_path):
    """Load batch data with comprehensive GitLab information"""
    try:
        df = pd.read_csv(csv_path)
        df.index = df.index + 1
        
        # Initialize columns for GitLab data - All 4 Tasks
        task1_readme_col = []
        task2_ai_col = []
        task3_streamlit_col = []
        task4_linux_col = []
        commits_count_col = []
        last_activity_col = []
        progress_score_col = []
        attendance_status_col = []
        total_tasks_completed_col = []

        # Show progress for data loading
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_students = len(df)
        
        for idx, row in df.iterrows():
            progress = idx / total_students
            progress_bar.progress(progress)
            status_text.text(f"Loading student data: {idx}/{total_students}")
            
            username = str(row['Gitlab usernames(code.swecha.org)']).strip()
            if username and username.lower() != "nan" and username != "#N/A":
                project_path = f"{username}/{username}"
                
                try:
                    # Check all 4 tasks
                    tasks = check_multiple_tasks(username)
                    commits_count = get_project_commits_count(project_path)
                    last_activity = get_project_last_activity(project_path)
                    
                    # Calculate progress based on completed tasks
                    completed_tasks = sum(tasks.values())
                    progress_score = (completed_tasks / 4) * 100  # 4 total tasks
                    
                    # Determine attendance status based on last activity
                    attendance_status = "🟢 Active" if commits_count > 0 else "🔴 Inactive"
                    
                    # Add task completion status
                    task1_readme_col.append("✅" if tasks["readme"] else "❌")
                    task2_ai_col.append("✅" if tasks["ai_assistant"] else "❌")
                    task3_streamlit_col.append("✅" if tasks["streamlit_app"] else "❌")
                    task4_linux_col.append("✅" if tasks["linux_install"] else "❌")
                    
                    commits_count_col.append(commits_count)
                    last_activity_col.append(last_activity)
                    progress_score_col.append(progress_score)
                    attendance_status_col.append(attendance_status)
                    total_tasks_completed_col.append(f"{completed_tasks}/4")
                    
                except Exception as e:
                    # Handle errors gracefully
                    task1_readme_col.append("❌")
                    task2_ai_col.append("❌")
                    task3_streamlit_col.append("❌")
                    task4_linux_col.append("❌")
                    commits_count_col.append(0)
                    last_activity_col.append("Error")
                    progress_score_col.append(0)
                    attendance_status_col.append("🔴 Inactive")
                    total_tasks_completed_col.append("0/4")
                    
            else:
                # Handle missing usernames
                task1_readme_col.append("❌")
                task2_ai_col.append("❌")
                task3_streamlit_col.append("❌")
                task4_linux_col.append("❌")
                commits_count_col.append(0)
                last_activity_col.append("No GitLab")
                progress_score_col.append(0)
                attendance_status_col.append("🔴 No GitLab")
                total_tasks_completed_col.append("0/4")

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Add all new columns to DataFrame - All 4 Tasks
        df["Task 1: README"] = task1_readme_col
        df["Task 2: AI Assistant"] = task2_ai_col
        df["Task 3: Streamlit App"] = task3_streamlit_col
        df["Task 4: Linux Install"] = task4_linux_col
        df["Tasks Completed"] = total_tasks_completed_col
        df["Commits"] = commits_count_col
        df["Last Activity"] = last_activity_col
        df["Progress Score"] = progress_score_col
        df["Attendance"] = attendance_status_col
        
        return df
        
    except FileNotFoundError:
        st.error(f"CSV file not found at path: {csv_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading batch data: {str(e)}")
        return pd.DataFrame()

# --- Main Application Logic ---
def main():
    """Main application with role-based access"""
    
    # Check if user is authenticated
    if not st.session_state.get("authenticated", False):
        show_login()
        return
    
    # Show user info in sidebar
    show_user_info()
    
    # Get current user and handle session errors
    try:
        user = st.session_state.user
        if not user:
            st.error("Session lost. Please login again.")
            st.session_state.authenticated = False
            st.rerun()
            return
    except Exception as e:
        st.error("Session error occurred. Please login again.")
        st.session_state.clear()
        st.session_state.authenticated = False
        st.rerun()
        return
    
    # Header with session info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title(f"🎓 ICFAI Student Dashboard - {user['role'].title()}")
    with col2:
        # Session info
        try:
            if "session_start_time" in st.session_state:
                session_duration = datetime.now() - st.session_state.session_start_time
                hours = int(session_duration.total_seconds() // 3600)
                minutes = int((session_duration.total_seconds() % 3600) // 60)
                st.caption(f"⏱️ Session: {hours}h {minutes}m")
        except:
            pass
    with col3:
        if st.button("🚪 Logout", key="logout_btn", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Role-based batch access
    if user["role"] == "faculty":
        available_batches = user.get("assigned_batches", [])
        if not available_batches:
            st.error("No batches assigned to you. Please contact an administrator.")
            return
    else:
        available_batches = ["Batch1.csv", "batch2.csv"]
    
    # Batch selection
    if len(available_batches) > 1:
        selected_batch = st.selectbox("📁 Select Batch", available_batches)
    else:
        selected_batch = available_batches[0]
        st.info(f"📁 Viewing: {selected_batch}")
    
    if selected_batch:
        # Load batch data
        with st.spinner("Loading student data from GitLab..."):
            df = load_batch_data(selected_batch)
        
        if not df.empty:
            
            # Dashboard metrics (role-based)
            col1, col2, col3, col4 = st.columns(4)
            
            total_students = len(df)
            active_students = len(df[df["Attendance"].str.contains("Active")])
            avg_progress = df["Progress Score"].mean()
            all_tasks_complete = len(df[df["Tasks Completed"] == "4/4"])
            
            with col1:
                st.metric("👥 Total Students", total_students)
            with col2:
                st.metric("🟢 Active Students", f"{active_students}/{total_students}")
            with col3:
                st.metric("📈 Avg Progress Score", f"{avg_progress:.1f}%")
            with col4:
                st.metric("🎯 All Tasks Complete", f"{all_tasks_complete}/{total_students}")
            
            # Role-based column display
            if user["role"] == "admin":
                # Admin sees everything including all tasks
                display_columns = ["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", 
                                 "Task 1: README", "Task 2: AI Assistant", "Task 3: Streamlit App", "Task 4: Linux Install",
                                 "Tasks Completed", "Commits", "Last Activity", "Progress Score", "Attendance"]
            elif user["role"] == "techlead":
                # Tech leads see detailed GitLab info and all tasks
                display_columns = ["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", 
                                 "Task 1: README", "Task 2: AI Assistant", "Task 3: Streamlit App", "Task 4: Linux Install",
                                 "Tasks Completed", "Commits", "Last Activity", "Progress Score", "Attendance"]
            else:
                # Faculty sees tasks completion and progress focused view
                display_columns = ["Campus ID", "Name", "Task 1: README", "Task 2: AI Assistant", 
                                 "Task 3: Streamlit App", "Task 4: Linux Install", "Tasks Completed", 
                                 "Last Activity", "Progress Score", "Attendance"]
            
            # Task Overview Summary
            st.subheader("📋 Task Completion Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            task1_complete = len(df[df["Task 1: README"] == "✅"])
            task2_complete = len(df[df["Task 2: AI Assistant"] == "✅"])
            task3_complete = len(df[df["Task 3: Streamlit App"] == "✅"])
            task4_complete = len(df[df["Task 4: Linux Install"] == "✅"])
            
            with col1:
                st.metric("📝 Task 1: README", f"{task1_complete}/{total_students}")
            with col2:
                st.metric("🤖 Task 2: AI Assistant", f"{task2_complete}/{total_students}")
            with col3:
                st.metric("💻 Task 3: Streamlit App", f"{task3_complete}/{total_students}")
            with col4:
                st.metric("🐧 Task 4: Linux Install", f"{task4_complete}/{total_students}")

            # Main data table
            st.subheader("📊 Student Overview")
            st.dataframe(df[display_columns], use_container_width=True)
            
            # Analytics section (for admin and techlead)
            if has_permission("analytics"):
                st.subheader("📈 Analytics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Progress distribution
                    st.markdown("**Progress Distribution**")
                    progress_ranges = pd.cut(df["Progress Score"], bins=[0, 25, 50, 75, 100], 
                                           labels=["0-25%", "26-50%", "51-75%", "76-100%"])
                    progress_counts = progress_ranges.value_counts()
                    st.bar_chart(progress_counts)
                
                with col2:
                    # Attendance status
                    st.markdown("**Attendance Status**")
                    attendance_counts = df["Attendance"].value_counts()
                    st.bar_chart(attendance_counts)
            
            # Search functionality
            st.subheader("🔍 Search Students")
            search_query = st.text_input("Search by Name or GitLab Username")
            
            if search_query:
                filtered_df = df[
                    df['Name'].str.contains(search_query, case=False, na=False) |
                    df['Gitlab usernames(code.swecha.org)'].astype(str).str.contains(search_query, case=False, na=False)
                ]
                
                if not filtered_df.empty:
                    st.success(f"Found {len(filtered_df)} student(s) matching '{search_query}'")
                    st.dataframe(filtered_df[display_columns])
                    
                    # Detailed view for faculty (tasks and progress focus)
                    if user["role"] == "faculty":
                        st.subheader("📋 Detailed Student Progress")
                        for _, row in filtered_df.iterrows():
                            with st.expander(f"📊 {row['Name']} - Progress Details"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Overall Progress", f"{row['Progress Score']}%")
                                    st.metric("Tasks Completed", f"{row['Tasks Completed']}")
                                    st.write(f"**Last Activity:** {row['Last Activity']}")
                                with col2:
                                    st.write(f"**Attendance Status:** {row['Attendance']}")
                                    
                                    # Task breakdown
                                    st.write("**📋 Task Status:**")
                                    st.write(f"• README Profile: {row['Task 1: README']}")
                                    st.write(f"• AI Assistant: {row['Task 2: AI Assistant']}")
                                    st.write(f"• Streamlit App: {row['Task 3: Streamlit App']}")
                                    st.write(f"• Linux Install: {row['Task 4: Linux Install']}")
                                    
                                    if has_permission("view_all"):
                                        st.write(f"**Total Commits:** {row['Commits']}")
                else:
                    st.warning("No students found matching your search.")
            
            # Export functionality (for admin and techlead)
            if has_permission("export_data"):
                st.subheader("📤 Export Data")
                if st.button("Download CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📁 Download Student Data",
                        data=csv,
                        file_name=f"{selected_batch.replace('.csv', '')}_report.csv",
                        mime="text/csv"
                    )

# --- Session State Management with Timeout ---
def initialize_session_state():
    """Initialize session state variables with error recovery"""
    try:
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user" not in st.session_state:
            st.session_state.user = None
        if "session_start_time" not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        if "last_activity" not in st.session_state:
            st.session_state.last_activity = datetime.now()
    except Exception as e:
        # Reset session state if corrupted
        st.session_state.clear()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.session_start_time = datetime.now()
        st.session_state.last_activity = datetime.now()

def check_session_timeout():
    """Check if session has timed out (2 hours)"""
    try:
        if "last_activity" in st.session_state:
            time_since_activity = datetime.now() - st.session_state.last_activity
            if time_since_activity.total_seconds() > 7200:  # 2 hours
                st.session_state.clear()
                st.warning("⏰ Session expired due to inactivity. Please login again.")
                return True
        # Update last activity
        st.session_state.last_activity = datetime.now()
        return False
    except Exception:
        return True

# Initialize session state
initialize_session_state()

# Check for session timeout
if st.session_state.get("authenticated", False):
    if check_session_timeout():
        st.session_state.authenticated = False
        st.rerun()

# Run the main application
if __name__ == "__main__":
    main()
