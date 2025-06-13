# import streamlit as st
# import pandas as pd
# import requests
# from urllib.parse import quote

# # --- Page Config ---
# st.set_page_config(page_title="ICFAI Student Dashboard", layout="centered")

# # --- Constants ---
# CSV_PATH = "students_info.csv"
# GITLAB_API_URL = "https://code.swecha.org/api/v4"
# GITLAB_TOKEN = st.secrets["Progress_tracker"]  # stored securely in .streamlit/secrets.toml

# headers = {
#     "PRIVATE-TOKEN": GITLAB_TOKEN
# }

# # --- GitLab README Check ---
# @st.cache_data(show_spinner=False)
# def check_file_in_project(project_path, file_path="README.md"):
#     encoded_project = quote(project_path, safe="")
#     encoded_file = quote(file_path, safe="")
#     url = f"{GITLAB_API_URL}/projects/{encoded_project}/repository/files/{encoded_file}/raw"

#     response = requests.get(url, headers=headers, params={"ref": "main"})
#     return response.status_code == 200

# # --- Load CSV ---
# try:
#     df = pd.read_csv(CSV_PATH)
# except FileNotFoundError:
#     st.error(f"CSV file not found at path: {CSV_PATH}")
#     st.stop()

# df.index = df.index + 1  # start index at 1

# # --- Process each student ---
# has_readme_col = []

# for _, row in df.iterrows():
#     username = str(row['Gitlab usernames(code.swecha.org)']).strip()
#     if username and username.lower() != "nan":
#         project_path = f"{username}/{username}"
#         try:
#             has_readme = check_file_in_project(project_path)
#             has_readme_col.append("✅" if has_readme else "❌")
#         except Exception as e:
#             has_readme_col.append("❌")
#             st.error(f"Error checking {username}: {e}")
#     else:
#         has_readme_col.append("❌")

# # Add column to DataFrame
# df["Created PROFILE README"] = has_readme_col

# # --- Streamlit UI ---
# st.title("ICFAI Student Dashboard")

# st.subheader("📋 PS1 Students")
# st.dataframe(df[["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", "Created PROFILE README"]], use_container_width=True)

# # --- Search ---
# st.subheader("🔍 Search Student")
# search_query = st.text_input("Search by Name, Email, or GitLab Username")

# if search_query:
#     filtered_df = df[
#         df['Name'].str.contains(search_query, case=False, na=False) |
#         df['Gitlab usernames(code.swecha.org)'].astype(str).str.contains(search_query, case=False, na=False)
#     ]

#     if not filtered_df.empty:
#         matched_names = ", ".join(filtered_df['Name'].dropna().unique())
#         st.write(f"### Matched Student(s): {matched_names}")
#         st.dataframe(filtered_df[["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", "Created PROFILE README"]])

#         st.subheader("GitLab Usernames")
#         st.text("\n".join(filtered_df['Gitlab usernames(code.swecha.org)'].dropna()))

#         st.subheader("Profile README Status")
#         for _, row in filtered_df.iterrows():
#             if row["Created PROFILE README"] == "✅":
#                 st.markdown(f"✅ `{row['Name']}` has created their GitLab profile README.")
#             else:
#                 st.markdown(f"❌ `{row['Name']}` needs to create their GitLab profile README.")
#     else:
#         st.warning("No matching students found.")



# import streamlit as st
# import pandas as pd
# import requests
# from urllib.parse import quote

# # --- Page Config ---
# st.set_page_config(page_title="ICFAI Student Dashboard", layout="centered")

# # --- Constants ---
# GITLAB_API_URL = "https://code.swecha.org/api/v4"
# GITLAB_TOKEN = st.secrets["Progress_tracker"]

# headers = {
#     "PRIVATE-TOKEN": GITLAB_TOKEN
# }

# # --- GitLab README Check ---
# @st.cache_data(show_spinner=False)
# def check_file_in_project(project_path, file_path="README.md"):
#     encoded_project = quote(project_path, safe="")
#     encoded_file = quote(file_path, safe="")
#     url = f"{GITLAB_API_URL}/projects/{encoded_project}/repository/files/{encoded_file}/raw"

#     response = requests.get(url, headers=headers, params={"ref": "main"})
#     return response.status_code == 200

# # --- Load Batch Data ---
# def load_batch_data(csv_path):
#     try:
#         df = pd.read_csv(csv_path)
#         df.index = df.index + 1
#         has_readme_col = []

#         for _, row in df.iterrows():
#             username = str(row['Gitlab usernames(code.swecha.org)']).strip()
#             if username and username.lower() != "nan":
#                 project_path = f"{username}/{username}"
#                 try:
#                     has_readme = check_file_in_project(project_path)
#                     has_readme_col.append("✅" if has_readme else "❌")
#                 except Exception as e:
#                     has_readme_col.append("❌")
#                     st.error(f"Error checking {username}: {e}")
#             else:
#                 has_readme_col.append("❌")

#         df["Created PROFILE README"] = has_readme_col
#         return df
#     except FileNotFoundError:
#         st.error(f"CSV file not found at path: {csv_path}")
#         return pd.DataFrame()

# # --- UI ---
# st.title("ICFAI Student Dashboard")

# batch = None
# col1, col2 = st.columns(2)

# with col1:
#     if st.button("📁 Batch1"):
#         batch = "batch1.csv"
# with col2:
#     if st.button("📁 Batch2"):
#         batch = "batch2.csv"

# # --- Show data if batch selected ---
# if batch:
#     df = load_batch_data(batch)

#     if not df.empty:
#         st.subheader("📋 Students")
#         st.dataframe(df[["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", "Created PROFILE README"]],
#                      use_container_width=True)

#         # --- Search ---
#         st.subheader("🔍 Search Student")
#         search_query = st.text_input("Search by Name or GitLab Username")

#         if search_query:
#             filtered_df = df[
#                 df['Name'].str.contains(search_query, case=False, na=False) |
#                 df['Gitlab usernames(code.swecha.org)'].astype(str).str.contains(search_query, case=False, na=False)
#             ]

#             if not filtered_df.empty:
#                 matched_names = ", ".join(filtered_df['Name'].dropna().unique())
#                 st.write(f"### Matched Student(s): {matched_names}")
#                 st.dataframe(filtered_df[["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", "Created PROFILE README"]])

#                 st.subheader("GitLab Usernames")
#                 st.text("\n".join(filtered_df['Gitlab usernames(code.swecha.org)'].dropna()))

#                 st.subheader("Profile README Status")
#                 for _, row in filtered_df.iterrows():
#                     if row["Created PROFILE README"] == "✅":
#                         st.markdown(f"✅ `{row['Name']}` has created their GitLab profile README.")
#                     else:
#                         st.markdown(f"❌ `{row['Name']}` needs to create their GitLab profile README.")
#             else:
#                 st.warning("No matching students found.")
# else:
#     st.info("Please select a batch to view student details.")
import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote

# --- Page Config ---
st.set_page_config(page_title="ICFAI Student Dashboard", layout="centered")

# --- Constants ---
GITLAB_API_URL = "https://code.swecha.org/api/v4"
GITLAB_TOKEN = st.secrets["Progress_tracker"]

headers = {
    "PRIVATE-TOKEN": GITLAB_TOKEN
}

# --- GitLab README Check ---
@st.cache_data(show_spinner=False)
def check_file_in_project(project_path, file_path="README.md"):
    encoded_project = quote(project_path, safe="")
    encoded_file = quote(file_path, safe="")
    url = f"{GITLAB_API_URL}/projects/{encoded_project}/repository/files/{encoded_file}/raw"

    response = requests.get(url, headers=headers, params={"ref": "main"})
    return response.status_code == 200

# --- Load Batch Data ---
def load_batch_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df.index = df.index + 1
        has_readme_col = []

        for _, row in df.iterrows():
            username = str(row['Gitlab usernames(code.swecha.org)']).strip()
            if username and username.lower() != "nan":
                project_path = f"{username}/{username}"
                try:
                    has_readme = check_file_in_project(project_path)
                    has_readme_col.append("✅" if has_readme else "❌")
                except Exception as e:
                    has_readme_col.append("❌")
                    st.error(f"Error checking {username}: {e}")
            else:
                has_readme_col.append("❌")

        df["Created PROFILE README"] = has_readme_col
        return df
    except FileNotFoundError:
        st.error(f"CSV file not found at path: {csv_path}")
        return pd.DataFrame()

# --- Initialize session state ---
if "selected_batch" not in st.session_state:
    st.session_state.selected_batch = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# --- Batch Buttons ---
st.title("ICFAI Student Dashboard")

col1, col2 = st.columns(2)
with col1:
    if st.button("📁 Batch1"):
        st.session_state.selected_batch = "batch1.csv"
        st.session_state.search_query = ""  # reset search on batch switch
with col2:
    if st.button("📁 Batch2"):
        st.session_state.selected_batch = "batch2.csv"
        st.session_state.search_query = ""  # reset search on batch switch

# --- Show batch data if selected ---
if st.session_state.selected_batch:
    df = load_batch_data(st.session_state.selected_batch)

    if not df.empty:
        st.subheader("📋 Students")
        st.dataframe(df[["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", "Created PROFILE README"]],
                     use_container_width=True)

        # --- Search Input ---
        st.subheader("🔍 Search Student")
        search_input = st.text_input("Search by Name or GitLab Username", st.session_state.search_query)

        # Update session state if input changes
        if search_input != st.session_state.search_query:
            st.session_state.search_query = search_input

        search_query = st.session_state.search_query

        if search_query:
            filtered_df = df[
                df['Name'].str.contains(search_query, case=False, na=False) |
                df['Gitlab usernames(code.swecha.org)'].astype(str).str.contains(search_query, case=False, na=False)
            ]

            if not filtered_df.empty:
                matched_names = ", ".join(filtered_df['Name'].dropna().unique())
                st.write(f"### Matched Student(s): {matched_names}")
                st.dataframe(filtered_df[["Campus ID", "Name", "Gitlab usernames(code.swecha.org)", "Created PROFILE README"]])

                st.subheader("GitLab Usernames")
                st.text("\n".join(filtered_df['Gitlab usernames(code.swecha.org)'].dropna()))

                st.subheader("Profile README Status")
                for _, row in filtered_df.iterrows():
                    if row["Created PROFILE README"] == "✅":
                        st.markdown(f"✅ `{row['Name']}` has created their GitLab profile README.")
                    else:
                        st.markdown(f"❌ `{row['Name']}` needs to create their GitLab profile README.")
            else:
                st.warning("No matching students found.")
else:
    st.info("Please select a batch to view student details.")
