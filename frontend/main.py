# streamlit_app.py
import streamlit as st
import time
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
# Assuming you have these extras installed
# pip install streamlit-extras requests python-dotenv fpdf
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.metric_cards import style_metric_cards
# from streamlit_extras.stylable_container import stylable_container # Not used in active code
# from streamlit_lottie import st_lottie # Not used in active code
# from fpdf import FPDF # Not used in active code

load_dotenv()

# --- Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000") # Use environment variable or default

# --- Backend API Call Functions ---
def upload_and_extract_text(file):
    """Send file to FastAPI backend for extraction"""
    try:
        # Correct way to send file with requests: pass a tuple (filename, file_object, content_type)
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f'{BACKEND_URL}/upload/proposal', files=files)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        if data.get("status") == "success" and "text" in data:
            return data["text"]
        else:
            st.error(f"❌ API Error: {data.get('detail', 'Unknown error during upload/processing.')}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Network Error calling API: {e}")
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected Error during file processing: {e}")
        return None

def analyze_proposal(proposal_text, extra_components=None):
    """Call the proposal component analysis endpoint"""
    try:
        # Prepare JSON payload
        data = {
            "proposal_text": proposal_text
        }
        if extra_components:
             data["extra_components"] = extra_components

        response = requests.post(
            f'{BACKEND_URL}/analyze_proposal_components',
            headers={'Content-Type': 'application/json'},
            json=data # Using json= is often cleaner than json.dumps + data=
        )
        response.raise_for_status()
        result_data = response.json()
        if result_data.get('status') == 'success':
            # Return the analysis text and None for error
            return result_data.get('analyze_proposal'), None
        else:
            # Return None for result and the error message
            return None, f"API Error: {result_data.get('error', 'Unknown error during component analysis.')}"
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse API response: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error during component analysis: {str(e)}"

def analyze_pricing_api(proposal_text, ai_analysis_details):
    """Call the pricing analysis endpoint"""
    try:
        data = {
            "proposal_text": proposal_text,
            "ai_analysis_details": ai_analysis_details # Matches backend model now
            # historical_data is not sent by frontend and not required by backend model (after correction)
        }
        response = requests.post(
            f'{BACKEND_URL}/analyze/pricing',
            headers={'Content-Type': 'application/json'},
            json=data
        )
        response.raise_for_status()
        result_data = response.json()
        if result_data.get('status') == 'success':
            return result_data.get('result'), None
        else:
            return None, f"API Error: {result_data.get('error', 'Unknown error during pricing analysis.')}"
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse API response: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error during pricing analysis: {str(e)}"

# --- Helper Functions (Potentially used later) ---
# Placeholder for other analysis functions - implement as needed
# def analyze_cost_realism_api(proposal_text, ai_analysis_details):
#     # Implement call to /analyze/cost-realism
#     pass
# def technical_analysis_api(proposal_text):
#     # Implement call to /analyze/technical
#     pass
# def compliance_analysis_api(proposal_text):
#     # Implement call to /analyze/compliance
#     pass
# def generate_summary_api(summary_request_data):
#     # Implement call to /generate/summary
#     # summary_request_data should be a dict matching summaryAnalysisRequest model
#     pass

def analyze_proposal_components(proposal_text, extra_component):
    """Orchestrates the component analysis and simulates component list"""
    try:
        with st.spinner("Analyzing proposal with AI"):
            ai_analysis_text, error = analyze_proposal(proposal_text, extra_component)
            if error:
                 st.error(f"Component Analysis Error: {error}")
                 return None, None

        # Simulate component list as backend doesn't return this structure directly
        # In a full implementation, the backend might return this or you parse it from ai_analysis_text
        components = {
            "Executive Summary": "✅",
            "Scope of Work": "✅",
            "Out of Scope": "✅",
            "Prerequisites": "✅",
            "Deliverables": "✅",
            "Timeline": "✅",
            "Technology Stack": "✅",
            "Budget": "✅",
            "Team Structure": "✅",
            "Risk Assessment": "✅",
            "Success Criteria": "✅",
        }
        return components, ai_analysis_text # Return the detailed text from AI
    except Exception as e:
        st.error(f"Error analyzing proposal: {str(e)}")
        return None, None

# --- UI and Logic ---
def reset_process_proposal():
    """Resets session state for a new analysis"""
    keys_to_reset = [
        'step',
        'proposal_text',
        'proposal_analysis',
        'ai_analysis_details', # Stores the detailed text from component analysis
        'proposal_summary',
        'extra_component',
        'current_filename',
        'price_analysis',
        'cost_realism',
        'unbalanced_pricing',
        'technical_analysis',
        'compliance_assessment',
        'processing'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    # Re-initialize defaults
    st.session_state.step = 1
    st.session_state.proposal_text = ""
    st.session_state.proposal_analysis = None
    st.session_state.ai_analysis_details = None
    st.session_state.proposal_summary = None
    st.session_state.extra_component = ""
    st.session_state.current_filename = None
    st.session_state.price_analysis = None
    st.session_state.cost_realism = None
    st.session_state.unbalanced_pricing = None
    st.session_state.technical_analysis = None
    st.session_state.compliance_assessment = None
    st.session_state.processing = False

# --- Initialize Session State ---
if 'mode' not in st.session_state:
    st.session_state.mode = "with_proposal"
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'proposal_text' not in st.session_state:
    st.session_state.proposal_text = ""
if 'proposal_analysis' not in st.session_state:
    st.session_state.proposal_analysis = None
if 'ai_analysis_details' not in st.session_state: # Key correction: was 'ai_analysis_details'
    st.session_state.ai_analysis_details = None
if 'proposal_summary' not in st.session_state:
    st.session_state.proposal_summary = None
if 'extra_component' not in st.session_state:
    st.session_state.extra_component = ""
if 'current_filename' not in st.session_state:
    st.session_state.current_filename = None
if 'price_analysis' not in st.session_state:
    st.session_state.price_analysis = None
# Add other state vars if needed for later steps

# --- Basic UI Setup ---
st.set_page_config(
    page_title="RFP Proposal Analyzer",
    page_icon="📄",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 1rem 0;
    background: linear-gradient(90deg, #1f77b4, #17becf);
    color: white;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.component-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 0.5rem 0;
}
.component-card.missing {
    border-left-color: #dc3545;
}
.progress-step {
    padding: 0.5rem;
    margin: 0.25rem 0;
    border-radius: 5px;
    background: #f1f3f4;
}
.progress-step.completed {
    background: #d4edda;
    border-left: 3px solid #28a745;
}
.progress-step.current {
    background: #fff3cd;
    border-left: 3px solid #ffc107;
}
.create-proposal-btn {
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 1000;
}
.analysis-section {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border: 1px solid #dee2e6;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1> RFP Proposal Analyzer</h1><p>Intelligent Proposal Analysis & RFP Management</p></div>', unsafe_allow_html=True)

# --- Mode Switching (Top Right) ---
col1, col2, col3 = st.columns([4, 1, 1])
with col3:
    # Simplified mode switching logic (commented out for now as Create Proposal is not active)
    # if st.session_state.mode == "with_proposal":
    #     if st.button("Create Proposal", key="create_proposal_btn", help="Switch to proposal creation mode"):
    #         st.session_state.mode = "create_proposal"
    #         reset_process_proposal()
    #         st.rerun()
    # else:
    #     if st.button("Go To Main Page", key="analysis_btn", help="Switch to proposal analysis mode"):
    #         st.session_state.mode = "with_proposal"
    #         reset_process_proposal()
    #         st.rerun()
    pass # Placeholder for mode switching buttons if needed later

# --- Main Analysis Mode ---
if st.session_state.mode == "with_proposal":
    # --- Sidebar ---
    with st.sidebar:
        st.image("./images/yashphoto.PNG", width=200) # Make sure this path exists
        st.title("Proposal Analysis Progress")
        analysis_steps = [
            "Flight Check",
            "Price Analysis",
            # Add more steps here as backend endpoints are implemented
        ]
        total_steps = len(analysis_steps)
        current_step = st.session_state.step

        # Calculate progress based on completed steps in session state
        completed_steps = 0
        if st.session_state.proposal_text and st.session_state.proposal_analysis:
            completed_steps = 1
        if st.session_state.price_analysis:
            completed_steps = 2
        # Add conditions for other steps if implemented

        completion = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
        st.progress(completion / 100)
        st.write(f"**{completion}%** completed")
        add_vertical_space(1)

        for i, step_name in enumerate(analysis_steps, 1):
            status_class = "completed" if i <= completed_steps else "current" if i == current_step else ""
            icon = "✅" if i <= completed_steps else "🔄" if i == current_step else "⏳"
            st.markdown(f'<div class="progress-step {status_class}"><strong>{icon} Step {i}: {step_name}</strong></div>', unsafe_allow_html=True)

        add_vertical_space(2)
        if st.button("🔄 Reset Analysis", use_container_width=True):
            reset_process_proposal()
            st.rerun()

        with st.expander("ℹ️ Help & Tips"):
            st.write("""
            **Enhanced AI Analysis Features:**
            - 🤖 AI-powered component detection
            - ✅ Component completeness check
            - 💡 Detailed improvement recommendations
            **Supported Formats:**
            - PDF documents
            - Word documents (.docx)
            - Text files (.txt)
            """)

    # --- Main Content Area ---
    colored_header(
        label="AI-Powered Proposal Analysis Dashboard",
        description="Upload and analyze your proposal document with advanced AI analysis",
        color_name="blue-green-70"
    )

    # --- Step 1: Flight Check ---
    if st.session_state.step == 1:
        with st.container():
            st.subheader("Step 1: Flight Check")
            st.write("Upload your proposal document and get instant AI-powered component analysis")
            col1, col2 = st.columns([2, 1])
            with col1:
                uploaded_file = st.file_uploader(
                    "Choose a file",
                    type=["pdf", "docx", "txt"],
                    accept_multiple_files=False,
                    key="file_uploader_step1"
                )
                if uploaded_file is not None:
                    st.session_state.current_filename = uploaded_file.name
                    with st.spinner("Processing and analyzing document..."):
                        extracted_text = upload_and_extract_text(uploaded_file)
                        if extracted_text:
                            st.session_state.proposal_text = extracted_text
                            # Automatically analyze components after successful extraction
                            components, ai_details = analyze_proposal_components(
                                st.session_state.proposal_text,
                                st.session_state.extra_component
                            )
                            st.session_state.proposal_analysis = components
                            st.session_state.ai_analysis_details = ai_details # Store the detailed text

            with col2:
                st.subheader("Additional Features")
                extra_component = st.text_area(
                    "Additional components to analyze:",
                    placeholder="Enter any additional features you want to analyze",
                    height=100,
                    key="extra_component_input_step1" # Unique key
                )
                if extra_component:
                    st.session_state.extra_component = extra_component

            if st.session_state.current_filename:
                st.info(f"📄 Document: **{st.session_state.current_filename}** | Length: **{len(st.session_state.proposal_text):,} characters**")

            if st.session_state.proposal_analysis and st.session_state.ai_analysis_details:
                st.success("✅ Document processed and analyzed successfully!")
                st.markdown("### 📋 Proposal Component Analysis")
                components = st.session_state.proposal_analysis
                component_list = list(components.items())
                # Display components in a grid
                for i in range(0, len(component_list), 2):
                    col1, col2 = st.columns(2)
                    with col1:
                        if i < len(component_list):
                            component_name, present = component_list[i]
                            card_class = "component-card"
                            st.markdown(f'<div class="{card_class}"><strong>{present} {component_name}</strong></div>',
                                        unsafe_allow_html=True)
                    with col2:
                        if i + 1 < len(component_list):
                            component_name, present = component_list[i + 1]
                            st.markdown(f'<div class="{card_class}"><strong>{present} {component_name}</strong></div>',
                                        unsafe_allow_html=True)

                if st.session_state.ai_analysis_details:
                    with st.expander("🔍 View Detailed Component Analysis", expanded=True):
                         # Use st.markdown to render potential markdown from backend
                        st.markdown(st.session_state.ai_analysis_details)
                        # If it's plain text, st.text(st.session_state.ai_analysis_details) might be better

                if st.button("Proceed to Price Analysis ➡️", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()

            elif st.session_state.proposal_text and not st.session_state.proposal_analysis:
                # Case where text is extracted but analysis hasn't run or failed initially
                if st.button("🔍 Analyze Proposal Components", type="primary", use_container_width=True):
                    with st.spinner("Analyzing proposal components..."):
                        components, ai_details = analyze_proposal_components(
                            st.session_state.proposal_text,
                            st.session_state.extra_component
                        )
                        st.session_state.proposal_analysis = components
                        st.session_state.ai_analysis_details = ai_details
                        st.rerun()

    # --- Step 2: Price Analysis ---
    elif st.session_state.step == 2:
        with st.container():
            st.subheader("Step 2: Price Analysis")
            st.write("Analyzing pricing fairness using AI...")

            if not st.session_state.price_analysis and st.session_state.proposal_text and st.session_state.ai_analysis_details:
                with st.spinner("Performing price analysis..."):
                    price_result, price_error = analyze_pricing_api(st.session_state.proposal_text, st.session_state.ai_analysis_details)
                    if price_error:
                        st.error(f"Price Analysis Error: {price_error}")
                    else:
                        st.session_state.price_analysis = price_result

            if st.session_state.price_analysis:
                with st.expander("💰 Price Analysis Results", expanded=True):
                    st.markdown(st.session_state.price_analysis)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back to Component Analysis"):
                        # Optional: Clear price analysis if going back
                        # st.session_state.price_analysis = None
                        st.session_state.step = 1
                        st.rerun()
                with col2:
                    # Placeholder for next step button - adjust endpoint/path as needed
                    # if st.button("Proceed to Cost Realism ➡️"): # Assuming /analyze/cost-realism exists
                    #     st.session_state.step = 3
                    #     st.rerun()
                    st.info("Further analysis steps (Cost Realism, Technical, Compliance, Summary) can be added by implementing calls to the corresponding backend endpoints.")

            else:
                # Handle case where we don't have the prerequisites or analysis failed
                if not st.session_state.proposal_text:
                    st.warning("Please complete Step 1 (Flight Check) first.")
                elif not st.session_state.ai_analysis_details:
                     st.warning("Component analysis details are missing. Please re-run Step 1.")
                # If price_analysis is None but text/details exist, it means analysis failed or is pending user action

# --- Style Metric Cards ---
style_metric_cards()
