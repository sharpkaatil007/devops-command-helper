import streamlit as st
import datetime
import json
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="DevOps Command Helper",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'commands' not in st.session_state:
    st.session_state.commands = []
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Dark mode
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
    <style>
        .stApp {background-color: #1a1a1a; color: #ffffff;}
        .stTextInput>div>div>input {background-color: #2b2b2b; color: #ffffff;}
        .stTextArea>div>div>textarea {background-color: #2b2b2b; color: #ffffff;}
    </style>
    """, unsafe_allow_html=True)

st.title("DevOps Command Helper 🚀")

# Sidebar - User Account
with st.sidebar:
    st.header("👤 User Account")
    
    if st.session_state.current_user is None:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.current_user = username
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
        
        with tab2:
            new_username = st.text_input("Username", key="reg_user")
            new_password = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Register"):
                if new_username and new_password:
                    st.session_state.users[new_username] = new_password
                    st.session_state.current_user = new_username
                    st.success(f"Welcome, {new_username}!")
                    st.rerun()
                else:
                    st.error("Please fill all fields!")
    else:
        st.write(f"👋 Hello, **{st.session_state.current_user}**!")
        if st.button("Logout"):
            st.session_state.current_user = None
            st.rerun()
    
    st.divider()
    category = st.selectbox("Filter:", ["All", "Docker", "Git", "Kubernetes", "Linux", "AWS", "Other"])

# AI explanation function
def get_ai_explanation(command):
    explanations = {
        "docker": f"🐳 Docker command: '{command}' - Manages containers and images",
        "git": f"📦 Git command: '{command}' - Version control operation",
        "kubectl": f"☸️ Kubernetes command: '{command}' - Manages K8s clusters",
        "apt": f"📦 APT command: '{command}' - Package management on Ubuntu/Debian",
        "npm": f"📦 NPM command: '{command}' - Node.js package management",
        "aws": f"☁️ AWS command: '{command}' - Amazon Web Services operation"
    }
    
    for key, explanation in explanations.items():
        if key in command.lower():
            return explanation
    return f"💻 Command: '{command}' - Executes system operations"

# Main content
if st.session_state.current_user:
    with st.expander("➕ Share a New Command", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            command_text = st.text_input("Command:", placeholder="docker ps -a")
            command_category = st.selectbox("Category:", ["Docker", "Git", "Kubernetes", "Linux", "AWS", "Other"])
        with col2:
            command_desc = st.text_area("Description:", placeholder="Lists all Docker containers")
        
        if st.button("Share Command", type="primary", use_container_width=True):
            if command_text and command_desc:
                st.session_state.commands.append({
                    'command': command_text,
                    'description': command_desc,
                    'category': command_category,
                    'votes': 0,
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'author': st.session_state.current_user,
                    'voters': []
                })
                st.success("✅ Command shared!")
                st.balloons()
else:
    st.info("👆 Please login to share commands!")

# Search and Export
col1, col2 = st.columns([3, 1])
with col1:
    search = st.text_input("🔍 Search commands:", "")
with col2:
    if st.button("📥 Export CSV"):
        if st.session_state.commands:
            df = pd.DataFrame(st.session_state.commands)
            csv = df.to_csv(index=False)
            st.download_button("Download", csv, "commands.csv", "text/csv")

# Filter and display commands
filtered_commands = st.session_state.commands
if category != "All":
    filtered_commands = [cmd for cmd in filtered_commands if cmd['category'] == category]
if search:
    filtered_commands = [cmd for cmd in filtered_commands if 
                        search.lower() in cmd['command'].lower() or 
                        search.lower() in cmd.get('description', '').lower()]

# Display commands
for i, cmd in enumerate(list(reversed(filtered_commands))):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown(f"**{cmd['category']}** | By: {cmd.get('author', 'Anonymous')} | {cmd['date']}")
        st.code(cmd['command'], language='bash')
        st.write(f"📝 {cmd['description']}")
        
        if st.button(f"🤖 AI Explain", key=f"ai_{i}"):
            st.info(get_ai_explanation(cmd['command']))
    
    with col2:
        if st.session_state.current_user:
            original_index = st.session_state.commands.index(cmd)
            user_voted = st.session_state.current_user in cmd.get('voters', [])
            
            if st.button(f"{'✅' if user_voted else '👍'} {cmd['votes']}", 
                        key=f"vote_{original_index}", disabled=user_voted):
                if not user_voted:
                    st.session_state.commands[original_index]['votes'] += 1
                    if 'voters' not in st.session_state.commands[original_index]:
                        st.session_state.commands[original_index]['voters'] = []
                    st.session_state.commands[original_index]['voters'].append(st.session_state.current_user)
                    st.rerun()
    
    st.divider()

# Stats
if st.session_state.commands:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Commands", len(st.session_state.commands))
    with col2:
        st.metric("Total Users", len(st.session_state.users))
    with col3:
        total_votes = sum(cmd['votes'] for cmd in st.session_state.commands)
        st.metric("Total Votes", total_votes)