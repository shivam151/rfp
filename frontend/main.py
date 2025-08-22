import streamlit as st
import pandas as pd
import time
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_lottie import st_lottie
from fpdf import FPDF

load_dotenv()


BACKEND_URL="http://0.0.0.0:8501"

def upload_and_extract_text(file):
    """Send file to FastAPI backend for extraction"""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f'{BACKEND_URL}/upload/proposal', files=files)
        response.raise_for_status()
        data = response.json()
        
        if "text" in data:
            return data["text"]
        else:
            st.error("No text returned from API.")
            return None
    except Exception as e:
        st.error(f"Error calling API: {e}")
        return None



def analyze_proposal(proposal_text, extra_components):
    try:
        data = {
            "proposal_text": proposal_text,
            "extra_components": extra_components
        }
        
        response = requests.post(
            f'{BACKEND_URL}/analyze_proposal_components',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()

            if result['status'] == 'success':
                return result['analyze_proposal'], None
            else:
                return None, f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return None, f"HTTP Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"


def analyze_pricing_api(proposal_text, ai_analysis_details):
    try:
        data = {
            "proposal_text": proposal_text,
            "ai_analysis_details": ai_analysis_details
        }
        
        analyze_pricing_api_response = requests.post(
            f'{BACKEND_URL}/analyze/pricing',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if analyze_pricing_api_response.status_code == 200:
            result = analyze_pricing_api_response.json()
            
            if result.get('status') == 'success':
                return result.get('result'), None
            else:
                return None, f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return None, f"HTTP Error: {analyze_pricing_api_response.status_code} - {analyze_pricing_api_response.text}"
            
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse API response: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def analyze_cost_realism_api(proposal_text, ai_analysis_details):
    try:
        data = {
            "proposal_text": proposal_text,
            "ai_analysis_details": ai_analysis_details
        }
        
        response = requests.post(
            f'{BACKEND_URL}/analyze/cost-realism',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('result'), None
            else:
                return None, f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return None, f"HTTP Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"


def analyze_technical_api(proposal_text, ai_analysis_details):
    try:
        data = {
            "proposal_text": proposal_text,
            "ai_analysis_details": ai_analysis_details
        }
        
        response = requests.post(
            f'{BACKEND_URL}/analyze/technical',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('result'), None
            else:
                return None, f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return None, f"HTTP Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"


def analyze_compliance_api(proposal_text, ai_analysis_details):
    try:
        data = {
            "proposal_text": proposal_text,
            "ai_analysis_details": ai_analysis_details
        }
        
        response = requests.post(
            f'{BACKEND_URL}/analyze/compliance',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('result'), None
            else:
                return None, f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return None, f"HTTP Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"


def generate_summary_api(proposal_text, ai_analysis_details, component_analysis=None, price_analysis=None, cost_realism=None, technical_analysis=None, compliance_assessment=None):
    try:
        data = {
            "proposal_text": proposal_text,
            "ai_analysis_details": ai_analysis_details,
            "component_analysis": component_analysis,
            "price_analysis": price_analysis,
            "cost_realism": cost_realism,
            "technical_analysis": technical_analysis,
            "compliance_assessment": compliance_assessment
            
        }
        
        response = requests.post(
            f'{BACKEND_URL}/generate/summary',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                return result['result'], None
            else:
                return None, f"API Error: {result.get('error', 'Unknown error')}"
        else:
            return None, f"HTTP Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request failed: {str(e)}"


def analyze_proposal_components(proposal_text, extra_component):
    try:
        with st.spinner("Analyzing proposal with AI"):
            ai_analysis, error = analyze_proposal(proposal_text, extra_component)
            if error:
                st.error(f"Error in AI analysis: {error}")
                return None, None
        
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
        
        return components, ai_analysis
        
    except Exception as e:
        st.error(f"Error analyzing proposal: {str(e)}")
        return None, None


def generate_pdf_report(content, filename="report.pdf"):
    try:
        from fpdf import FPDF
        import re

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'Proposal Analysis Report', 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Arial', '', 12)

        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue

            if line.startswith('# '):
                pdf.set_font('Arial', 'B', 16)
                pdf.multi_cell(0, 10, line[2:], 0, 1)
                pdf.ln(5)
                pdf.set_font('Arial', '', 12)
            elif line.startswith('## '):
                pdf.set_font('Arial', 'B', 14)
                pdf.multi_cell(0, 8, line[3:], 0, 1)
                pdf.ln(3)
                pdf.set_font('Arial', '', 12)
            elif line.startswith('### '):
                pdf.set_font('Arial', 'B', 12)
                pdf.multi_cell(0, 6, line[4:], 0, 1)
                pdf.ln(2)
                pdf.set_font('Arial', '', 12)
            else:
                line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                line = re.sub(r'\*(.*?)\*', r'\1', line)
                line = re.sub(r'`(.*?)`', r'\1', line)

                try:
                    pdf.multi_cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
                except:
                    clean_line = ''.join(char if ord(char) < 128 else '?' for char in line)
                    pdf.multi_cell(0, 6, clean_line, 0, 1)
                pdf.ln(2)

        return pdf.output(dest='S').encode('latin-1')

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None


def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def next_step():
    st.session_state.step += 1
    st.session_state.processing = False


def reset_process_proposal():
    keys_to_reset = [
        'step',
        'proposal_text',
        'proposal_analysis',
        'ai_analysis_details',
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


def main():
    st.set_page_config(
        page_title="RFP Proposal Analyzer",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🚀 RFP Proposal Analyzer")
    st.markdown("### Comprehensive AI-Powered Proposal Analysis System")
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'proposal_text' not in st.session_state:
        st.session_state.proposal_text = None
    if 'new_feature' not in st.session_state:
        st.session_state.new_feature = ""


st.set_page_config(
    page_title="Project Management Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    load_css("assets/style.css")
except:
    pass

if 'mode' not in st.session_state:
    st.session_state.mode = "with_proposal" 
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'proposal_text' not in st.session_state:
    st.session_state.proposal_text = ""
if 'proposal_analysis' not in st.session_state:
    st.session_state.proposal_analysis = None
if 'ai_analysis_details' not in st.session_state:
    st.session_state.ai_analysis_details = None
if 'proposal_summary' not in st.session_state:
    st.session_state.proposal_summary = None
if 'extra_component' not in st.session_state:
    st.session_state.extra_component = ""
if 'current_filename' not in st.session_state:  
    st.session_state.current_filename = None 
if 'price_analysis' not in st.session_state:
    st.session_state.price_analysis = None
if 'cost_realism' not in st.session_state:
    st.session_state.cost_realism = None
if 'unbalanced_pricing' not in st.session_state:
    st.session_state.unbalanced_pricing = None
if 'technical_analysis' not in st.session_state:
    st.session_state.technical_analysis = None
if 'compliance_assessment' not in st.session_state:
    st.session_state.compliance_assessment = None
if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
if 'proposal_text' not in st.session_state:
        st.session_state.proposal_text = None
if 'new_feature' not in st.session_state:
        st.session_state.new_feature = ""

if 'pricing_file_text' not in st.session_state:
    st.session_state.pricing_file_text = None
if 'pricing_analysis_done' not in st.session_state:
    st.session_state.pricing_analysis_done = False

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

st.markdown('<div class="main-header"><h1> Project Management Tool</h1><p>Intelligent Proposal Analysis & RFP Management</p></div>', unsafe_allow_html=True)

if st.session_state.mode == "with_proposal":
    with st.sidebar:
        st.image("./images/yashphoto.PNG", width=200)  
        st.title("Proposal Analysis Progress")
        
        analysis_steps = [
            ("Flight Check", "✈️"),
            ("Price Analysis", "💰"),  
            ("Cost Realism Check", "📊"),             
            ("Technical Analysis Review", "🔧"),      
            ("Compliance Assessment", "📋"),         
            ("Generate Summary Report", "📄"),
        ]
        
        total_steps = len(analysis_steps)
        current_step = 1
        
        if st.session_state.proposal_text and st.session_state.proposal_analysis:
            current_step = 2
        if st.session_state.price_analysis:
            current_step = 3
        if st.session_state.cost_realism:
            current_step = 4
        if st.session_state.technical_analysis:
            current_step = 5
        if st.session_state.compliance_assessment:
            current_step = 6
        if st.session_state.proposal_summary:
            current_step = 7

        completion = int((current_step - 1) / total_steps * 100)
        st.progress(completion / 100)
        st.write(f"**{completion}%** completed")
        
        add_vertical_space(1)
        
        for i, (step_name, step_icon) in enumerate(analysis_steps, 1):
            if i < current_step:
                icon = "✅" 
                status_class = "completed"
            elif i == current_step:
                icon = step_icon 
                status_class = "current"
            else:
                icon = step_icon  
                status_class = ""
            
            st.markdown(f'<div class="progress-step {status_class}"><strong>{icon} Step {i}: {step_name}</strong></div>', unsafe_allow_html=True)
        
        add_vertical_space(2)
        
        if st.button("🔄 Reset Analysis", use_container_width=True):
            reset_process_proposal()
            st.rerun()
        
        with st.expander("ℹ️ Help & Tips"):
            st.write("""
            **Enhanced AI Analysis Features:**
            - 🤖 AI-powered component detection
            - ✅ 15+ component completeness check
            - 📊 Quality assessment scoring
            - 🎯 Compliance verification
            - 💡 Detailed improvement recommendations
            - 📋 Executive summary generation
            
            **Supported Formats:**
            - PDF documents
            - Word documents (.docx)
            - Text files (.txt)
            """)

    colored_header(
        label="AI-Powered Proposal Analysis Dashboard",
        description="Upload and analyze your proposal document with advanced AI analysis",
        color_name="blue-green-70"
    )
    
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
                            components, ai_details = analyze_proposal_components(
                                st.session_state.proposal_text, 
                                st.session_state.extra_component
                            )   
                            st.session_state.proposal_analysis = components
                            st.session_state.ai_analysis_details = ai_details
            
            with col2:
                st.subheader("Additional Features")
                extra_component = st.text_area(
                    "Additional components to analyze:",
                    placeholder="Enter any additional features you want to analyze",
                    height=100
                )
                
                if extra_component:
                    st.session_state.extra_component = extra_component
            
            if st.session_state.current_filename:
                st.info(f"📄 Document: **{st.session_state.current_filename}** | Length: **{len(st.session_state.proposal_text):,} characters**")
            
            if st.session_state.proposal_analysis:
                st.success("✅ Document processed and analyzed successfully!")
                
                st.markdown("### 📋 Proposal Component Analysis")
                components = st.session_state.proposal_analysis
                component_list = list(components.items())
                
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
                    with st.expander("🔍 View Detailed Component Analysis"):
                        st.markdown(st.session_state.ai_analysis_details)
                
                if st.button("Proceed to Price Analysis ➡️", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
            
            elif st.session_state.proposal_text:
                if st.button("🔍 Analyze Proposal Components", type="primary", use_container_width=True):
                    with st.spinner("Analyzing proposal components..."):
                        components, ai_details = analyze_proposal_components(
                            st.session_state.proposal_text, 
                            st.session_state.extra_component
                        )
                        st.session_state.proposal_analysis = components
                        st.session_state.ai_analysis_details = ai_details
                        st.rerun()
    
    elif st.session_state.step == 2:
        with st.container():
            st.subheader("Step 2: Price Analysis")
            st.write("Upload your cost breakdown or enter it manually to analyze pricing fairness.")

        # Initialize session state
        if 'costing_file_text' not in st.session_state:
            st.session_state.costing_file_text = None
        if 'manual_costing_text' not in st.session_state:
            st.session_state.manual_costing_text = ""
        if 'pricing_analysis_done' not in st.session_state:
            st.session_state.pricing_analysis_done = False
        if 'final_costing_text' not in st.session_state:
            st.session_state.final_costing_text = None

        # Two-column layout (same as Step 1)
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write("📁 Upload Costing File (PDF, DOCX, TXT)")
            costing_file = st.file_uploader(
                "Choose a costing file",
                type=["pdf", "docx", "txt"],
                key="costing_file_uploader_step2",
                label_visibility="collapsed"
            )

            if costing_file is not None and st.session_state.costing_file_text is None:
                with st.spinner("📄 Extracting text from costing file..."):
                    try:
                        files = {"file": (costing_file.name, costing_file, costing_file.type)}
                        response = requests.post(f'{BACKEND_URL}/coast/proposal', files=files)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.costing_file_text = data["text"]
                            st.success(" Costing file processed!")
                            st.session_state.final_costing_text = None
                            st.session_state.pricing_analysis_done = False
                        else:
                            st.error(f" Failed: {response.text}")
                    except Exception as e:
                        st.error(f" Error: {e}")

            # Show extracted file text
            if st.session_state.costing_file_text:
                with st.expander("📄 Preview Uploaded Costing Data", expanded=False):
                    st.text_area("", st.session_state.costing_file_text, height=200, disabled=True)

        with col2:
            st.write("📝 Manual Costing Input")
            manual_input = st.text_area(
                "Enter cost details",
                value=st.session_state.manual_costing_text,
                height=250,
                placeholder="Enter the price of proposal ",
                key="manual_costing_input"
            )
            if manual_input.strip() != st.session_state.manual_costing_text:
                st.session_state.manual_costing_text = manual_input
                st.session_state.final_costing_text = None
                st.session_state.pricing_analysis_done = False

            # Show manual input preview
            if st.session_state.manual_costing_text:
                with st.expander("✏️ Preview", expanded=False):
                    st.text_area("", st.session_state.manual_costing_text, height=100, disabled=True)

        # Determine final costing text
        final_costing_text = None
        if st.session_state.manual_costing_text.strip():
            final_costing_text = st.session_state.manual_costing_text
        elif st.session_state.costing_file_text:
            final_costing_text = st.session_state.costing_file_text

        if final_costing_text and final_costing_text != st.session_state.final_costing_text:
            st.session_state.final_costing_text = final_costing_text
            st.session_state.pricing_analysis_done = False

        if st.session_state.final_costing_text and not st.session_state.pricing_analysis_done:
            if st.button("🔍 Analyze Pricing", type="primary", use_container_width=True):
                with st.spinner("🔍 Running price fairness analysis..."):
                    try:
                        data = {
                            "proposal_text": st.session_state.proposal_text,
                            "ai_analysis_details":st.session_state.ai_analysis_details,
                            "costing_file_text": st.session_state.costing_file_text,
                            "manual_costing_text": st.session_state.manual_costing_text
                        }
                        response = requests.post(f'{BACKEND_URL}/analyze/pricing', json=data)
                        if response.status_code == 200:
                            result = response.json()["result"]
                            st.session_state.price_analysis = result
                            st.session_state.pricing_analysis_done = True
                            st.success("Price analysis completed!")
                        else:
                            st.error(f"Analysis failed: {response.text}")
                    except Exception as e:
                        st.error(f"API error: {str(e)}")

        if st.session_state.pricing_analysis_done and st.session_state.price_analysis:
            with st.expander("💰 Price Analysis Results", expanded=True):
                st.markdown(st.session_state.price_analysis)

        if st.session_state.pricing_analysis_done:
            if st.button("Proceed to Cost Realism Check", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
    

    elif st.session_state.step == 3:
        with st.container():
            st.subheader("Step 3: Cost Realism Analysis")
            st.write("Evaluating if proposed costs are realistic for the work scope...")
            
            if not st.session_state.cost_realism:
                with st.spinner("Analyzing cost realism per FAR 15.404-1(d)..."):
                    result, error = analyze_cost_realism_api(
                        st.session_state.proposal_text, 
                        st.session_state.ai_analysis_details
                    )
                    if error:
                        st.error(f"Error in cost realism analysis: {error}")
                    else:
                        st.session_state.cost_realism = result
            
            if st.session_state.cost_realism:
                with st.expander("💰 Cost Realism Analysis", expanded=True):
                    st.markdown(st.session_state.cost_realism)
                    
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back to Price Analysis"):
                        st.session_state.step = 2
                        st.rerun()
                with col2:
                    if st.button("Proceed to Technical Analysis ➡️", type="primary"):
                        st.session_state.step = 4
                        st.rerun()

    elif st.session_state.step == 4:
        with st.container():
            st.subheader("Step 4: Technical Analysis Review")
            st.write("Reviewing technical aspects and feasibility...")
            
            if not st.session_state.technical_analysis:
                with st.spinner("Performing technical analysis review..."):
                    result, error = analyze_technical_api(
                        st.session_state.proposal_text, 
                        st.session_state.ai_analysis_details
                    )
                    if error:
                        st.error(f"Error in technical analysis: {error}")
                    else:
                        st.session_state.technical_analysis = result
            
            if st.session_state.technical_analysis:
                with st.expander("🔧 Technical Analysis", expanded=True):
                    st.markdown(st.session_state.technical_analysis)
                    
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back to Cost Realism"):
                        st.session_state.step = 3
                        st.rerun()
                with col2:
                    if st.button("Proceed to Compliance Assessment ➡️", type="primary"):
                        st.session_state.step = 5
                        st.rerun()

    elif st.session_state.step == 5:
        with st.container():
            st.subheader("Step 5: Compliance Assessment")
            st.write("Assessing compliance with requirements and regulations...")
            
            if not st.session_state.compliance_assessment:
                with st.spinner("Performing compliance assessment..."):
                    result, error = analyze_compliance_api(
                        st.session_state.proposal_text, 
                        st.session_state.ai_analysis_details
                    )
                    if error:
                        st.error(f"Error in compliance assessment: {error}")
                    else:
                        st.session_state.compliance_assessment = result
            
            if st.session_state.compliance_assessment:
                with st.expander("⚖️ Compliance Assessment", expanded=True):
                    st.markdown(st.session_state.compliance_assessment)
                    
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("⬅️ Back to Technical Analysis"):
                        st.session_state.step = 4
                        st.rerun()
                with col2:
                    if st.button("Generate Summary Report ➡️", type="primary"):
                        st.session_state.step = 6
                        st.rerun()

    elif st.session_state.step == 6:
        with st.container():
            st.subheader("Step 6: Executive Summary Report")
            if not st.session_state.proposal_summary:
                with st.spinner("Generating comprehensive summary report..."):
                    component_analysis_for_api = json.dumps(st.session_state.proposal_analysis) if st.session_state.proposal_analysis else None

                    result, error = generate_summary_api(
                        st.session_state.proposal_text, 
                        st.session_state.ai_analysis_details,
                        component_analysis_for_api,
                        st.session_state.price_analysis,
                        st.session_state.cost_realism,
                        st.session_state.technical_analysis,
                        st.session_state.compliance_assessment
                    )
                    if error:
                        st.error(f"Error generating summary: {error}")
                    else:
                        st.session_state.proposal_summary = result
            
            if st.session_state.proposal_summary:
                st.success("✅ Summary report generated successfully!")
                st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
                st.markdown(st.session_state.proposal_summary)
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("⬅️ Back to Compliance Assessment"):
                        st.session_state.step = 5
                        st.rerun()
                with col2:
                    st.download_button(
                        label="📥 Download Summary Report (MD)",
                        data=st.session_state.proposal_summary,
                        file_name=f"proposal_summary_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
                with col3:
                    pdf_data = generate_pdf_report(
                        st.session_state.proposal_summary, 
                        f"proposal_summary_{datetime.now().strftime('%Y%m%d')}.pdf"
                    )
                    if pdf_data:
                        st.download_button(
                            label="📥 Download Summary Report (PDF)",
                            data=pdf_data,
                            file_name=f"proposal_summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.warning("PDF generation failed")

elif st.session_state.mode == "create_proposal":
    pass
style_metric_cards()




























