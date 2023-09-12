import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gmail_api import *

# Create sidebar in streamlit with fields for inputting gmail API credentials; have them default to the environment variables GMAIL_API_CLIENT_ID and GMAIL_API_CLIENT_SECRET   
with st.sidebar:
    st.subheader("Gmail API Credentials")
    st.text_input("Gmail API Client ID", value=os.environ.get("GMAIL_API_CLIENT_ID", ""))
    st.text_input("Gmail API Client Secret", value=os.environ.get("GMAIL_API_CLIENT_SECRET", ""))

st.title("Email Automation Tool")

# Create a button to start the OAuth flow
if st.button("Authenticate with Gmail"):
    st.toast("Authenticating...")
    authenticated = main()
    if authenticated:
        st.toast("Authenticated!")
    else:
        st.toast("Couldn not authenticate.")