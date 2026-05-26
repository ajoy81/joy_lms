import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_google_sheets_client():
    """Initializes and returns the gspread client using Streamlit secrets."""
    # This requires Streamlit secrets to be configured with GCP credentials.
    # We will simulate/mock it if credentials are not found so the app doesn't crash in dev.
    try:
        # Check if running in Streamlit cloud with secrets
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
            client = gspread.authorize(creds)
            return client
    except Exception as e:
        print(f"Failed to initialize gspread client: {e}")
    
    return None

def fetch_google_sheet_data(sheet_url):
    """Fetches data from a given Google Sheet URL and returns a Pandas DataFrame."""
    client = get_google_sheets_client()
    if not client:
        # Return a mock dataframe if no credentials
        st.warning("Google Sheets credentials not found. Showing mock data.")
        return pd.DataFrame({
            "Timestamp": ["2026-05-23 10:00:00", "2026-05-23 10:05:00"],
            "Score": ["10/10", "8/10"],
            "Student Name": ["kid1", "kid2"]
        })
        
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error fetching Google Sheet: {e}")
        return pd.DataFrame()

def render_google_sheet_view(sheet_url):
    """Fetches and renders the google sheet as a Streamlit dataframe."""
    st.markdown("### 📊 External Responses (Google Forms/Sheets)")
    if sheet_url:
        with st.spinner("Fetching data from Google Sheets..."):
            df = fetch_google_sheet_data(sheet_url)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No data found or unable to access the sheet.")
    else:
        st.info("No Google Sheet URL provided for this item.")
