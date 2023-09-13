from dotenv import load_dotenv
import os
import sys

import json

import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gmail_api import *

load_dotenv()

# Parse config.json
with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)

streamlit_port = int(config.get("port", 8501))

if "gmail_api" not in st.session_state:
    st.session_state["gmail_api"] = None

with st.sidebar:
    page = st.selectbox("Choose a page", ["Compose Email", "Reply/Follow-up"])

    st.subheader("Gmail API Credentials")
    gmail_api_client_id = st.text_input("Client ID", value=os.environ.get("GMAIL_API_CLIENT_ID", ""), type="password")
    gmail_api_client_secret = st.text_input("Client Secret", value=os.environ.get("GMAIL_API_CLIENT_SECRET", ""), type="password")
    
if page == "Compose Email":
    st.header("Compose and Send Mass Emails")

    # Email composition UI
    recipient_emails = st.text_area("Recipient Emails (comma separated)", "")
    subject = st.text_input("Email Subject", "")
    body = st.text_area("Email Body", "")
    is_bold = st.checkbox("Bold text")
    is_italic = st.checkbox("Italicize text")

    # Style text
    if is_bold:
        body = f"<b>{body}</b>"
    if is_italic:
        body = f"<i>{body}</i>"

    # Preview & Test UI
    if st.button("Preview Email"):
        st.write("Email Preview:")
        st.write(body, unsafe_allow_html=True)

    test_email = st.text_input("Test Email Address", "")
    if st.button("Send Test Email"):
        # send_email(subject, body, [test_email], is_test=True, test_email=test_email)
        st.success("Test email sent!")

    if st.button("Send Email"):
        to_emails = [email.strip() for email in recipient_emails.split(",")]
        # send_email(subject, body, to_emails)
        st.success("Email sent!")

elif page == "Reply/Follow-up":
    st.header("Reply/Follow-up to Emails")
    # Reply/Follow-up UI can be added here

# st.title("Email Automation Tool")

# st.session_state["gmail_api"] = GmailAPI(gmail_api_client_id, gmail_api_client_secret, streamlit_port)

# # Create a button to start the OAuth flow
# if st.button("Log into Gmail"):
#     st.toast("Authenticating...")
#     authentication_url = st.session_state["gmail_api"].get_authentication_url()

#     st.markdown(f"Visit this [url]({authentication_url}) to authenticate.")

#     # if st.session_state["gmail_api"].service:
#     #     st.success("Authenticated!")
#     # else:
#     #     st.error("Could not authenticate. Try again.")

# if "token" not in st.session_state:
#     st.session_state.token = None

# if st.session_state.token is None:
#     try:
#         code = st.experimental_get_query_params()["code"][0]
#         # access_token = st.session_state["gmail_api"].get_access_token(code)
#         print(code)
#         st.session_state["gmail_api"].build_service(code)

#         print(st.session_state["gmail_api"].service.users().getProfile(userId="me").execute())
#     except Exception as e:
#         st.write("Login again into Gmail to authenticate.")
#         print(e)
#         st.stop()