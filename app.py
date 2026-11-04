import io
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.pipeline import BankStatementPipeline
from src.classifier.rules_engine import HeuristicRulesEngine
from src.exporter.export_manager import ExportManager

# Streamlit Page Configuration
st.set_page_config(
    page_title="befree | Financial Statement Processing Platform",
    page_icon="https://befreeltd.com/wp-content/uploads/2021/04/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, Modern Professional SaaS / Fintech CSS (Befree Brand Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Light Layout */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
        color: #0F172A !important;
    }

    /* Force Clean Light Background on Streamlit Containers */
    [data-testid="stAppViewContainer"], 
    .main, 
    .block-container {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Clean White Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #334155 !important;
    }

    /* Streamlit Toolbar Header */
    header[data-testid="stHeader"] {
        background-color: #F8FAFC !important;
    }

    /* Base Headings & Titles */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }

    p, span, label {
        color: #334155 !important;
    }

    /* Befree Top Navigation Header */
    .befree-header-wrapper {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 16px 26px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05) !important;
    }

    .befree-logo-container {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .befree-logo-text {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A !important;
        letter-spacing: -0.6px;
        line-height: 1;
    }

    .befree-logo-text span {
        color: #0052CC;
    }

    .befree-tagline {
        color: #64748B !important;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 4px;
    }

    .badge-online {
        background: #F0FDF4 !important;
        border: 1px solid #BBF7D0 !important;
        color: #166534 !important;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-portal {
        background: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        color: #475569 !important;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* KPI Cards */
    .kpi-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 18px 20px !important;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(15, 23, 42, 0.08) !important;
    }

    .kpi-border-blue { border-top: 3px solid #0052CC !important; }
    .kpi-border-emerald { border-top: 3px solid #10B981 !important; }
    .kpi-border-rose { border-top: 3px solid #EF4444 !important; }
    .kpi-border-amber { border-top: 3px solid #F59E0B !important; }
    .kpi-border-cyan { border-top: 3px solid #0284C7 !important; }

    .kpi-label-text {
        font-size: 0.78rem;
        font-weight: 700;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    .kpi-val-text {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0F172A !important;
        letter-spacing: -0.5px;
    }

    /* Account Metadata Card */
    .befree-account-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 20px 24px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04) !important;
        border-left: 4px solid #0052CC !important;
    }

    /* Forensic Anomaly Banner */
    .forensic-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04) !important;
    }

    /* Badges */
    .badge-pill-text {
        background: #EFF6FF !important;
        color: #1D4ED8 !important;
        border: 1px solid #BFDBFE !important;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-pill-ocr {
        background: #FFFBEB !important;
        color: #B45309 !important;
        border: 1px solid #FDE68A !important;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-pill-balanced {
        background: #F0FDF4 !important;
        color: #166534 !important;
        border: 1px solid #BBF7D0 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .badge-pill-discrepancy {
        background: #FEF2F2 !important;
        color: #991B1B !important;
        border: 1px solid #FECACA !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #E2E8F0 !important;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #64748B !important;
        border-radius: 8px 8px 0 0 !important;
        background: transparent !important;
    }

    .stTabs [aria-selected="true"] {
        color: #0052CC !important;
        border-bottom: 2px solid #0052CC !important;
        background: transparent !important;
    }

    /* Primary Action Buttons */
    .stButton > button {
        background-color: #0052CC !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #0045B5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.25) !important;
        color: #FFFFFF !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #0052CC !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background-color: #F8FAFC !important;
        border-color: #0052CC !important;
        color: #0052CC !important;
    }

    /* Inputs and Selectors */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


def render_befree_header():
    """Renders the clean, modern Befree Enterprise Header with a simple minimalist logo mark"""
    st.markdown("""
    <div class="befree-header-wrapper">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div class="befree-logo-container">
                <!-- Simple Minimalist Logo -->
                <div style="width: 40px; height: 40px; border-radius: 10px; background: #0052CC; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0, 82, 204, 0.25);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M7 4v16"/>
                        <path d="M7 12h7a4 4 0 0 1 0 8H7"/>
                    </svg>
                </div>
                <div>
                    <div class="befree-logo-text">befree<span>.</span></div>
                    <div class="befree-tagline">Financial Processing & Autonomous Ledger Classification System</div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span class="badge-online">● Non-LLM Engine: Active</span>
                <span class="badge-portal">Enterprise Suite</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    render_befree_header()

    # Sidebar Navigation & Workspace
    st.sidebar.markdown("""
    <div style="padding: 6px 0 14px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
        <span style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">Statement Ingestion</span><br>
        <span style="font-size: 0.8rem; color: #64748B;">Multi-Bank Parsing & Audit Hub</span>
    </div>
    """, unsafe_allow_html=True)

    # 13-Bank Benchmark Statements Selector
    sample_options = {
        "None (Upload Custom PDF)": None,
        "01. HDFC Bank (Text-Based, Multi-line UPI)": "sample_statements/01_hdfc_statement_text.pdf",
        "02. State Bank of India (Txn Date + Value Date)": "sample_statements/02_sbi_statement_text.pdf",
        "03. ICICI Bank (Scanned / Image PDF via EasyOCR)": "sample_statements/03_icici_statement_scanned.pdf",
        "04. Axis Bank (Particulars + Amount Format)": "sample_statements/04_axis_statement_text.pdf",
        "05. Kotak Mahindra Bank (Investments & Wealth)": "sample_statements/05_kotak_statement_text.pdf",
        "06. Bank of Baroda (Public Sector Format)": "sample_statements/06_bank_of_baroda_text.pdf",
        "07. Punjab National Bank (Scanned Document)": "sample_statements/07_pnb_statement_scanned.pdf",
        "08. Canara Bank (Standard Retail Format)": "sample_statements/08_canara_bank_text.pdf",
        "09. IndusInd Bank (High-Frequency Merchant/UPI)": "sample_statements/09_indusind_statement_text.pdf",
        "10. Multi-Page Statement (2-Page Continuous Ledger)": "sample_statements/10_multipage_statement_text.pdf",
        "11. Corporate & Payroll Account (Business Statement)": "sample_statements/11_corporate_business_statement.pdf",
        "12. Audit Discrepancy Statement (Ledger Mismatch Test)": "sample_statements/12_discrepancy_audit_statement.pdf",
        "13. Password-Protected Statement (HDFC Bank - befree123)": "sample_statements/13_password_protected_statement.pdf"
    }

    selected_sample = st.sidebar.selectbox("📂 Select Bank Statement Template:", list(sample_options.keys()))

    # Password Support for Encrypted Statements
    statement_password = st.sidebar.text_input(
        "🔑 Statement Password (if encrypted):", 
        type="password", 
        placeholder="e.g. befree123 or DOB/PAN",
        help="Supports encrypted bank statements (e.g. HDFC, ICICI, SBI). Enter the password if required."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📤 Or Upload Customer Statement (PDF):**")
    uploaded_file = st.sidebar.file_uploader("", type=["pdf"], help="Local sandboxed processing — zero financial data leaves your device.")

    # Sidebar System Metrics Widget
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #0052CC; border-radius: 8px; padding: 14px; font-size: 0.82rem; color: #334155;">
        <span style="font-weight: 700; color: #0F172A;">Platform Specifications</span><br>
        • <b>Classification:</b> Non-LLM Hybrid Architecture<br>
        • <b>ML Core:</b> TF-IDF (N-grams) + Logistic Reg.<br>
        • <b>Model Accuracy:</b> 98.14% on Financial Benchmark<br>
        • <b>Computer Vision:</b> EasyOCR Deep CRAFT Engine<br>
        • <b>Audit Engine:</b> Mathematical Balance Chain<br>
        • <b>Forensic Audit:</b> Anomaly & Tax Tagger Active<br>
        • <b>Security:</b> 100% Local On-Device Processing
    </div>
    """, unsafe_allow_html=True)

    # Resolve active file source
    file_bytes = None
    file_name = "statement.pdf"

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
    elif selected_sample and sample_options[selected_sample] is not None:
        sample_path = sample_options[selected_sample]
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_bytes = f.read()
            file_name = os.path.basename(sample_path)

    # Main Tabs
    tab_dashboard, tab_batch_hub, tab_architecture, tab_model_metrics = st.tabs([
        "📊 Statement Processor", 
        "📑 Multi-Bank Benchmark Hub",
        "🏛️ System Architecture & Specifications", 
        "📈 ML Model Evaluation"
    ])

    # ==========================================
    # TAB 1: Statement Processor
    # ==========================================
    with tab_dashboard:
        if file_bytes is None:
            st.markdown("""
            <div style="text-align: center; padding: 48px 24px; background: #FFFFFF; border: 2px dashed #CBD5E1; border-radius: 14px; margin: 20px 0;">
                <div style="width: 54px; height: 54px; border-radius: 12px; background: #EFF6FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0052CC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="12" y1="18" x2="12" y2="12"></line>
                        <line x1="9" y1="15" x2="15" y2="15"></line>
                    </svg>
                </div>
                <h3 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">Ready for Statement Ingestion</h3>
                <p style="color: #64748B; font-size: 0.92rem; max-width: 540px; margin: 0 auto 18px auto; line-height: 1.5;">
                    Select one of the <b>13 preloaded multi-bank statements</b> from the left sidebar or upload a bank statement PDF to execute extraction, classification, and mathematical ledger reconciliation.
                </p>
                <div style="display: inline-flex; gap: 8px; flex-wrap: wrap; justify-content: center; font-size: 0.8rem; color: #64748B;">
                    <span style="background: #F1F5F9; padding: 5px 12px; border-radius: 6px; font-weight: 500;">✓ Digital & Scanned PDF Ingestion</span>
                    <span style="background: #F1F5F9; padding: 5px 12px; border-radius: 6px; font-weight: 500;">✓ Encrypted PDF Decryption Support</span>
                    <span style="background: #F1F5F9; padding: 5px 12px; border-radius: 6px; font-weight: 500;">✓ 98.14% Heuristic + ML Classification</span>
                    <span style="background: #F1F5F9; padding: 5px 12px; border-radius: 6px; font-weight: 500;">✓ Forensic Anomaly & Audit Detection</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        with st.spinner("Processing document through Befree ingestion and classification pipeline..."):
            try:
                results = BankStatementPipeline.process_statement(
                    file_bytes, 
                    file_name=file_name,
                    password=statement_password if statement_password else None
                )
            except Exception as e:
                st.error(f"Processing Error: {str(e)}")
                return

        # Check for encrypted statement needing password
        if results.get("status") == "PASSWORD_REQUIRED":
            st.warning("""
            🔒 **Password-Protected Bank Statement Detected**
            
            This document is encrypted with a password. Please enter the decryption password in the left sidebar under **Statement Password** and the document will unlock automatically.
            
            *(Tip: For Template 13, the decryption password is `befree123`)*
            """)
            return

        metadata = results["metadata"]
        detection = results["detection"]
        reconciliation = results["reconciliation"]
        transactions = results["transactions"]
        anomalies = results.get("anomalies", {})
        extraction_stats = results["extraction_stats"]

        # 1. Detection Banner & Telemetry Bar
        col_type, col_meta_summary = st.columns([1.2, 2.8])
        with col_type:
            if detection["doc_type"] == "TEXT_BASED":
                st.markdown('<div class="badge-pill-text">📄 TEXT-BASED DIGITAL PDF</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-pill-ocr">📷 SCANNED / IMAGE-BASED PDF (OCR PIPELINE)</div>', unsafe_allow_html=True)
            st.caption(f"**Document:** `{file_name}` ({detection['total_pages']} page(s))")

        with col_meta_summary:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; font-size: 0.85rem; color: #475569;">
                <b>System Diagnostics:</b> Extracted <b>{detection['total_characters']}</b> glyphs | 
                Density: <b>{detection['avg_chars_per_page']}</b> chars/page | 
                Engine: <code>{extraction_stats.get('extraction_mode', 'STANDARD')}</code> |
                Multi-Line Row Stitcher: <b>ACTIVE</b>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 2. Account Information Header Card
        st.markdown(f"""
        <div class="befree-account-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F1F5F9; padding-bottom: 12px; margin-bottom: 14px;">
                <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                    🏦 {metadata.get('bank_name', 'Bank Statement')}
                </div>
                <div style="font-size: 0.85rem; color: #64748B; font-weight: 500;">
                    Statement Period: <span style="color: #0F172A; font-weight: 700;">{metadata.get('statement_period', 'N/A')}</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                <div>
                    <span style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Account Holder</span><br>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0F172A;">{metadata.get('account_holder', 'N/A')}</span>
                </div>
                <div>
                    <span style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Account Number</span><br>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0F172A; font-family: monospace;">{metadata.get('account_number', 'N/A')}</span>
                </div>
                <div>
                    <span style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">IFSC / Routing Code</span><br>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0F172A; font-family: monospace;">{metadata.get('ifsc_code', 'N/A')}</span>
                </div>
                <div>
                    <span style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Account Classification</span><br>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0F172A;">{metadata.get('account_type', 'Standard Account')}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Financial KPI Metrics Grid
        k1, k2, k3, k4, k5 = st.columns(5)
        
        with k1:
            st.markdown(f"""
            <div class="kpi-card kpi-border-blue">
                <div class="kpi-label-text">Total Transactions</div>
                <div class="kpi-val-text">{reconciliation.get('total_transactions', 0)}</div>
                <span style="font-size: 0.75rem; color: #64748B;">Processed Ledger Lines</span>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="kpi-card kpi-border-emerald">
                <div class="kpi-label-text">Total Inflow (Credits)</div>
                <div class="kpi-val-text" style="color: #10B981;">₹{reconciliation.get('total_credits', 0.0):,.2f}</div>
                <span style="font-size: 0.75rem; color: #10B981;">Deposits & Receipts</span>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="kpi-card kpi-border-rose">
                <div class="kpi-label-text">Total Outflow (Debits)</div>
                <div class="kpi-val-text" style="color: #EF4444;">₹{reconciliation.get('total_debits', 0.0):,.2f}</div>
                <span style="font-size: 0.75rem; color: #EF4444;">Expenses & Withdrawals</span>
            </div>
            """, unsafe_allow_html=True)

        net_cash = reconciliation.get("net_change", 0.0)
        net_color = "#10B981" if net_cash >= 0 else "#EF4444"
        with k4:
            st.markdown(f"""
            <div class="kpi-card kpi-border-amber">
                <div class="kpi-label-text">Net Cash Flow</div>
                <div class="kpi-val-text" style="color: {net_color};">₹{net_cash:,.2f}</div>
                <span style="font-size: 0.75rem; color: {net_color};">{'Net Surplus' if net_cash >= 0 else 'Net Deficit'}</span>
            </div>
            """, unsafe_allow_html=True)

        audit_status = reconciliation.get("reconciliation_status", "BALANCED")
        integrity_score = reconciliation.get("integrity_score", 100.0)
        status_badge_html = '<span class="badge-pill-balanced">✓ 100% BALANCED</span>' if audit_status == "BALANCED" else f'<span class="badge-pill-discrepancy">⚠ {reconciliation.get("discrepancy_count", 0)} DISCREPANCY</span>'
        with k5:
            st.markdown(f"""
            <div class="kpi-card kpi-border-cyan">
                <div class="kpi-label-text">Ledger Audit Status</div>
                <div class="kpi-val-text">{integrity_score}%</div>
                <div style="margin-top: 4px;">{status_badge_html}</div>
            </div>
            """, unsafe_allow_html=True)

        # 4. Forensic Anomaly & Audit Risk Telemetry Card
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        risk_profile = anomalies.get("risk_profile", "CLEAN")
        risk_color = "#166534" if risk_profile == "CLEAN" else ("#B45309" if risk_profile == "MEDIUM_RISK" else "#991B1B")
        risk_bg = "#F0FDF4" if risk_profile == "CLEAN" else ("#FFFBEB" if risk_profile == "MEDIUM_RISK" else "#FEF2F2")

        st.markdown(f"""
        <div class="forensic-card" style="border-left: 4px solid {risk_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Forensic Accounting Risk Profile</span><br>
                    <span style="display: inline-block; background: {risk_bg}; color: {risk_color}; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.88rem; margin-top: 4px;">
                        ● RISK LEVEL: {risk_profile}
                    </span>
                </div>
                <div style="display: flex; gap: 16px; font-size: 0.85rem; color: #334155;">
                    <div>⚠️ Duplicates: <b>{anomalies.get('duplicates_count', 0)}</b></div>
                    <div>📈 Outlier Spikes: <b>{anomalies.get('outliers_count', 0)}</b></div>
                    <div>🏛️ Structuring Checks: <b>{anomalies.get('structuring_count', 0)}</b></div>
                    <div>🧾 Tax Deductions / GST: <b>{anomalies.get('tax_events_count', 0)}</b></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 5. Analytics Visualizations with Clean Theme
        if transactions:
            df_txns = pd.DataFrame(transactions)
            st.markdown("### 📊 Financial Insights & Ledger Visualizations")
            c1, c2 = st.columns(2)

            chart_palette = ["#0052CC", "#10B981", "#F59E0B", "#EF4444", "#6366F1", "#06B6D4", "#EC4899", "#64748B"]

            with c1:
                debit_df = df_txns[df_txns["debit"] > 0]
                if not debit_df.empty:
                    cat_summary = debit_df.groupby("category")["debit"].sum().reset_index()
                    fig_pie = px.pie(
                        cat_summary, values="debit", names="category",
                        title="Spending Distribution by Category",
                        hole=0.48,
                        color_discrete_sequence=chart_palette
                    )
                    fig_pie.update_layout(
                        template="plotly_white",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#0F172A", family="Plus Jakarta Sans"),
                        margin=dict(t=40, b=10, l=10, r=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No debit transactions recorded.")

            with c2:
                timeline_df = df_txns.groupby("date")[["debit", "credit"]].sum().reset_index()
                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Bar(
                    x=timeline_df["date"], y=timeline_df["credit"],
                    name="Inflow (Credits)", marker_color="#10B981"
                ))
                fig_timeline.add_trace(go.Bar(
                    x=timeline_df["date"], y=timeline_df["debit"],
                    name="Outflow (Debits)", marker_color="#EF4444"
                ))
                fig_timeline.update_layout(
                    template="plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#0F172A", family="Plus Jakarta Sans"),
                    title="Cash Flow Activity Timeline",
                    barmode="group",
                    margin=dict(t=40, b=10, l=10, r=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_timeline, use_container_width=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 6. Interactive Ledger Table with Search & Filters
        st.markdown("### 📝 Extracted & Classified Ledger Records")
        st.caption("Classified via Non-LLM Hybrid Engine with Normalized Counterparty and Forensic Risk Flags.")

        if transactions:
            table_df = pd.DataFrame(transactions).copy()
            
            # Interactive Search & Filter Bar
            filter_c1, filter_c2, filter_c3 = st.columns([2, 1.2, 1])
            with filter_c1:
                search_query = st.text_input("🔍 Search Narration or Counterparty:", placeholder="e.g. Swiggy, Salary, Uber, EMI, Amazon...")
            with filter_c2:
                all_cats = ["All Categories"] + sorted(list(table_df["category"].unique()))
                selected_cat = st.selectbox("Category Filter:", all_cats)
            with filter_c3:
                status_filter = st.selectbox("Audit Filter:", ["All Transactions", "Verified Only", "Discrepancies Only", "Anomalies Only"])

            # Apply filters
            if search_query:
                mask = (
                    table_df["description"].str.contains(search_query, case=False, na=False) |
                    table_df["clean_counterparty"].str.contains(search_query, case=False, na=False)
                )
                table_df = table_df[mask]
            if selected_cat != "All Categories":
                table_df = table_df[table_df["category"] == selected_cat]
            if status_filter == "Verified Only":
                table_df = table_df[table_df["reconciliation_status"].isin(["VERIFIED", "INITIAL_ROW"])]
            elif status_filter == "Discrepancies Only":
                table_df = table_df[~table_df["reconciliation_status"].isin(["VERIFIED", "INITIAL_ROW"])]
            elif status_filter == "Anomalies Only":
                table_df = table_df[table_df["has_anomaly"] == True]

            display_cols = [
                "date", "clean_counterparty", "description", "payment_channel", 
                "debit", "credit", "balance", "category", "confidence", "reconciliation_status", "risk_level"
            ]
            clean_view = table_df[[c for c in display_cols if c in table_df.columns]].copy()
            if "confidence" in clean_view.columns:
                clean_view["confidence"] = clean_view["confidence"].apply(lambda c: f"{float(c)*100:.1f}%" if pd.notnull(c) else "100.0%")
            
            clean_view.rename(columns={
                "date": "Date",
                "clean_counterparty": "Counterparty / Vendor",
                "description": "Particulars / Narration",
                "payment_channel": "Channel",
                "debit": "Debit (₹)",
                "credit": "Credit (₹)",
                "balance": "Balance (₹)",
                "category": "Assigned Category",
                "confidence": "Confidence",
                "reconciliation_status": "Reconciliation Status",
                "risk_level": "Forensic Risk"
            }, inplace=True)

            st.dataframe(
                clean_view,
                use_container_width=True,
                column_config={
                    "Debit (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Credit (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Balance (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Date": st.column_config.TextColumn(width="small"),
                    "Counterparty / Vendor": st.column_config.TextColumn(width="medium"),
                    "Particulars / Narration": st.column_config.TextColumn(width="large"),
                }
            )

            # 7. Human-in-the-Loop (HITL) Interactive Category Override
            with st.expander("✏️ Human-in-the-Loop (HITL) Category Override"):
                st.caption("Allow accounting professionals to manually adjust or re-categorize specific transactions.")
                hitl_col1, hitl_col2, hitl_col3 = st.columns([2, 1.5, 1])
                with hitl_col1:
                    row_options = [f"{i}: {t.get('date')} - {t.get('clean_counterparty', t.get('description'))[:30]} (₹{float(t.get('debit', 0) or t.get('credit', 0)):.2f})" for i, t in enumerate(transactions)]
                    selected_row_idx = st.selectbox("Select Transaction to Adjust:", range(len(transactions)), format_func=lambda i: row_options[i])
                with hitl_col2:
                    current_cat = transactions[selected_row_idx].get("category", "General")
                    category_choices = [
                        "Salary & Income", "Food & Dining", "Groceries & Supermarket", "Shopping & E-Commerce",
                        "Utilities & Bills", "Travel & Commute", "Investments & Wealth", "Loans & EMI",
                        "Bank Charges & Taxes", "Entertainment & Subs", "Healthcare & Medical", "Education & Fees",
                        "Transfers & Personal", "Others & Miscellaneous"
                    ]
                    override_cat = st.selectbox("Select Correct Category:", category_choices, index=category_choices.index(current_cat) if current_cat in category_choices else 0)
                with hitl_col3:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("💾 Apply Override", use_container_width=True):
                        transactions[selected_row_idx]["category"] = override_cat
                        transactions[selected_row_idx]["classification_engine"] = "MANUAL_HITL_OVERRIDE"
                        st.success(f"Updated row {selected_row_idx + 1} to '{override_cat}'. Re-export to save!")

            # 8. Enterprise Accounting Export Hub
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("### 📥 Export Formatted Financial Data")
            st.caption("Generate ready-to-import outputs for downstream enterprise accounting systems (Excel, CSV, Tally Prime, QuickBooks, Xero).")
            
            exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)
            with exp_c1:
                st.download_button(
                    label="📊 Download Multi-Tab Excel (.xlsx)",
                    data=results["exports"]["excel"],
                    file_name=f"{os.path.splitext(file_name)[0]}_befree_classified.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with exp_c2:
                st.download_button(
                    label="📄 Download Clean CSV (.csv)",
                    data=results["exports"]["csv"],
                    file_name=f"{os.path.splitext(file_name)[0]}_befree_classified.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with exp_c3:
                st.download_button(
                    label="🧾 Tally Prime XML Voucher (.xml)",
                    data=results["exports"]["tally_xml"],
                    file_name=f"{os.path.splitext(file_name)[0]}_tally_vouchers.xml",
                    mime="application/xml",
                    use_container_width=True
                )
            with exp_c4:
                st.download_button(
                    label="💼 QuickBooks / Xero CSV (.csv)",
                    data=results["exports"]["quickbooks_csv"],
                    file_name=f"{os.path.splitext(file_name)[0]}_quickbooks_feed.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.warning("No transactions extracted from this document.")

    # ==========================================
    # TAB 2: Multi-Bank Benchmark Hub
    # ==========================================
    with tab_batch_hub:
        st.header("📑 Multi-Bank Benchmark & Batch Audit Hub")
        st.markdown("""
        This suite evaluates our pipeline across **13 diverse multi-bank statement formats** covering 
        major Indian and international banking layouts, multi-page statements, corporate payroll ledgers, 
        deliberate audit discrepancies, and password-protected PDFs.
        """)

        if st.button("🚀 Run Live Batch Evaluation Across All Statements", use_container_width=True):
            with st.spinner("Executing batch pipeline across all bank statement formats..."):
                import glob
                pdf_files = sorted(glob.glob("sample_statements/[0-9]*.pdf"))
                records = []
                for p in pdf_files:
                    fname = os.path.basename(p)
                    # Use password for statement 13
                    pwd = "befree123" if "13" in fname else None
                    res = BankStatementPipeline.process_statement(p, file_name=fname, password=pwd)
                    records.append({
                        "Statement": fname,
                        "Type": res["detection"]["doc_type"],
                        "Bank": res["metadata"].get("bank_name", "N/A"),
                        "Account Holder": res["metadata"].get("account_holder", "N/A"),
                        "Txns": len(res["transactions"]),
                        "Debit (₹)": f"{res['reconciliation'].get('total_debits', 0.0):,.2f}",
                        "Credit (₹)": f"{res['reconciliation'].get('total_credits', 0.0):,.2f}",
                        "Audit Status": res["reconciliation"].get("reconciliation_status", "N/A"),
                        "Risk Profile": res.get("anomalies", {}).get("risk_profile", "CLEAN"),
                        "Integrity": f"{res['reconciliation'].get('integrity_score', 100.0)}%"
                    })
                st.session_state["benchmark_records"] = records

        if "benchmark_records" in st.session_state:
            df_bench = pd.DataFrame(st.session_state["benchmark_records"])
            st.dataframe(df_bench, use_container_width=True)
            st.success(f"Successfully processed {len(df_bench)} bank statements in batch mode!")
        else:
            if os.path.exists("evaluation_benchmark_report.md"):
                with open("evaluation_benchmark_report.md", "r", encoding="utf-8") as f:
                    st.markdown(f.read())

    # ==========================================
    # TAB 3: System Architecture & Specifications
    # ==========================================
    with tab_architecture:
        st.header("🏛️ Engineering Architecture & System Specifications")
        st.caption("Visual Architectural Flow Diagram (Draw.io Style) — Document Ingestion, Dual-Stream Extraction, Non-LLM Classification, Forensic Audit & Exports.")

        if os.path.exists("architecture_diagram.html"):
            with open("architecture_diagram.html", "r", encoding="utf-8") as f:
                html_markup = f.read()
            components.html(html_markup, height=1050, scrolling=True)
        elif os.path.exists("architecture_diagram.svg"):
            st.image("architecture_diagram.svg", use_container_width=True)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if os.path.exists("architecture_diagram.drawio"):
                with open("architecture_diagram.drawio", "r", encoding="utf-8") as f:
                    st.download_button("📥 Download Editable Draw.io Diagram File (.drawio)", f.read(), file_name="befree_architecture.drawio", mime="application/xml", use_container_width=True)
        with col_d2:
            if os.path.exists("architecture_diagram.html"):
                with open("architecture_diagram.html", "r", encoding="utf-8") as f:
                    st.download_button("🌐 Download High-Res Architecture HTML (.html)", f.read(), file_name="befree_architecture.html", mime="text/html", use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown(r"""
        ### 1. High-Performance Zero-LLM Architecture
        * **Sub-millisecond Latency:** Traditional LLMs incur 1000–3000ms latency per transaction batch. Our local Scikit-Learn TF-IDF model executes in `< 2 milliseconds` per transaction.
        * **Zero Inference Cost:** No recurring third-party API token expenses.
        * **100% Data Confidentiality:** Fully compliant with financial confidentiality and privacy norms; zero customer data leaves the local environment.

        ### 2. PDF Auto-Detection & Dual-Stream Extraction
        * **Glyph Density Analysis:** If character count $\ge 50$ per page, routes to coordinate-based extraction.
        * **OCR Pipeline:** If a scanned raster image is detected, triggers local `EasyOCR` (CRAFT neural network) without requiring external binaries.
        * **Encrypted Statement Decryption:** Handles password-protected PDFs (e.g. HDFC, ICICI, SBI) natively without external decryption tools.

        ### 3. Stateful Multi-Line Narration Stitching
        * Stateful row reconstruction tracks primary transaction keys (valid date and balance). If text wraps to subsequent lines without date/balance, it is stitched back to the parent narration.

        ### 4. Forensic Anomaly & Audit Risk Engine
        * Identifies duplicate billing, high-value spending spikes ($Z$-score outliers), AML structuring alerts, and statutory tax deductions (TDS, GST, Advance Tax).

        ### 5. Mathematical Balance Reconciliation Validator
        * Automated ledger equation audit: $\text{Balance}_i = \text{Balance}_{i-1} - \text{Debit}_i + \text{Credit}_i$.
        * Flags OCR anomalies, inverted Dr/Cr columns, or skipped rows with discrepancy alerts.

        ### 6. Universal Enterprise Accounting Exports
        * One-click exports for Multi-Tab Excel, Standard CSV, Tally Prime XML Vouchers, and QuickBooks/Xero universal bank feeds.
        """)

    # ==========================================
    # TAB 4: Model Evaluation
    # ==========================================
    with tab_model_metrics:
        st.header("📈 Traditional ML Model Benchmarks")
        st.markdown("""
        * **Model:** Calibrated Logistic Regression + Sublinear TF-IDF (1-2 N-grams)
        * **Overall Test Accuracy:** `98.14%`
        * **Inference Cost:** $0.00 (Local CPU Execution)
        """)
        
        metrics_data = [
            {"Category": "Salary & Income", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Food & Dining", "Precision": 0.94, "Recall": 1.00, "F1-Score": 0.97},
            {"Category": "Groceries & Supermarket", "Precision": 0.93, "Recall": 1.00, "F1-Score": 0.96},
            {"Category": "Shopping & E-Commerce", "Precision": 0.94, "Recall": 0.94, "F1-Score": 0.94},
            {"Category": "Utilities & Bills", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Travel & Commute", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Investments & Wealth", "Precision": 1.00, "Recall": 0.85, "F1-Score": 0.92},
            {"Category": "Loans & EMI", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Bank Charges & Taxes", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Entertainment & Subs", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Healthcare & Medical", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Education & Fees", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
            {"Category": "Transfers & Personal", "Precision": 1.00, "Recall": 1.00, "F1-Score": 1.00},
        ]
        df_m = pd.DataFrame(metrics_data)
        st.dataframe(df_m, use_container_width=True)


if __name__ == "__main__":
    main()
