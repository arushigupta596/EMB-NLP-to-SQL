"""Main Streamlit application for NL-to-SQL chat interface."""
import streamlit as st
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Import custom modules
from config import *
from data_loader import DataLoader
from database_handler import DatabaseHandler
from llm_handler import SQLAgentHandler, ChartRequestParser
from chart_generator import ChartGenerator
from report_generator import ReportGenerator
from advanced_report_generator import AdvancedReportGenerator
from sample_questions import get_all_sample_questions, get_categories
from cache_manager import CacheManager
from cache_warmer import warm_cache_on_startup
from query_templates import get_template_sql, has_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="",
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark Theme
st.markdown("""
    <style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* ========================================
       DARK THEME COLOR TOKENS
       ======================================== */
    :root {
        /* Backgrounds */
        --bg-base: #0c2114;
        --bg-surface: #102a1c;
        --bg-surface-2: #0f2419;
        --bg-info: #123524;

        /* Borders */
        --border: #1f3d2b;

        /* Colors */
        --primary-green: #47bf72;
        --secondary-green: #346948;

        /* Text */
        --text-primary: #ffffff;
        --text-secondary: #cfe7db;
        --text-muted: #8fb3a2;
        --text-link: #47bf72;

        /* Typography */
        --font-family: 'Inter', 'Segoe UI', 'Roboto', system-ui, sans-serif;
        --weight-normal: 400;
        --weight-medium: 500;
        --weight-semibold: 600;
    }

    /* Base Typography */
    * {
        font-family: var(--font-family);
    }

    body {
        color: var(--text-primary);
        background-color: var(--bg-base);
    }

    /* ========================================
       GLOBAL LAYOUT & BACKGROUNDS
       ======================================== */

    /* App Canvas Background */
    .stApp {
        background-color: var(--bg-base);
    }

    /* Main Content Area */
    .main .block-container {
        background-color: var(--bg-base);
    }

    /* ========================================
       HEADER & TITLE
       ======================================== */

    /* App Subtitle */
    .app-subtitle {
        text-align: center;
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: var(--weight-semibold);
        margin-bottom: 2rem;
        margin-top: 1.5rem;
        letter-spacing: -0.02em;
    }

    /* ========================================
       SIDEBAR
       ======================================== */

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: var(--bg-base);
    }

    /* Sidebar Containers */
    [data-testid="stSidebar"] > div {
        background-color: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        margin: 0.5rem 0;
        padding: 1rem;
    }

    /* Sidebar Section Headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-secondary);
        text-transform: uppercase;
        font-size: 1rem;
        letter-spacing: 0.08em;
        font-weight: var(--weight-medium);
        background-color: transparent;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Sidebar Body Text */
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-muted);
    }

    /* Sidebar Metric Numbers */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--primary-green);
        font-weight: var(--weight-semibold);
    }

    /* Sidebar Sample Question Buttons */
    [data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(90deg, #0c2114 0%, #346948 100%);
        border: none;
        color: #ffffff;
        font-weight: 500;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        transition: all 150ms ease-out;
    }

    [data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(90deg, #102a1c 0%, #47bf72 100%);
        color: #ffffff;
    }

    /* ========================================
       MAIN CONTENT CARDS
       ======================================== */

    /* Card/Panel Styling */
    .element-container {
        background-color: transparent;
        border: none;
        border-radius: 0;
    }

    /* ========================================
       INFO BANNER
       ======================================== */

    .info-box {
        padding: 1rem 1.2rem;
        border-radius: 8px;
        background-color: var(--bg-info);
        border-left: 4px solid var(--primary-green);
        margin: 1.5rem 0;
    }

    .info-box ul li {
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* ========================================
       BUTTONS
       ======================================== */

    .stButton>button {
        width: 100%;
        background-color: var(--primary-green);
        color: var(--bg-base);
        border: none;
        border-radius: 8px;
        font-weight: var(--weight-medium);
        padding: 0.6rem 1.5rem;
        transition: opacity 0.2s ease;
    }

    .stButton>button:hover {
        opacity: 0.85;
    }

    /* ========================================
       CHAT INPUT
       ======================================== */

    .stChatInputContainer {
        border-radius: 8px;
    }

    .stChatInput {
        background-color: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 8px;
    }

    .stChatInput:focus-within {
        border-color: var(--primary-green);
        outline: none;
        box-shadow: none;
    }

    /* Input Text Color */
    .stChatInput input {
        color: var(--text-primary);
        background-color: var(--bg-surface);
    }

    /* Input Placeholder */
    .stChatInput input::placeholder {
        color: var(--text-muted);
    }

    /* Send Icon */
    .stChatInput button {
        color: var(--primary-green);
    }

    /* ========================================
       CHAT MESSAGES
       ======================================== */

    .stChatMessage {
        border-radius: 8px;
        margin: 1rem 0;
        padding: 1rem;
    }

    /* User Message Bubble */
    .stChatMessage[data-testid="user-message"],
    .stChatMessage:has([data-testid*="user"]) {
        background-color: var(--bg-surface);
        border-left: 4px solid var(--primary-green);
        border: 1px solid var(--border);
    }

    .stChatMessage[data-testid="user-message"] p,
    .stChatMessage:has([data-testid*="user"]) p {
        color: var(--text-primary);
    }

    /* System/Assistant Message Bubble */
    .stChatMessage[data-testid="assistant-message"],
    .stChatMessage:not(:has([data-testid*="user"])) {
        background-color: var(--bg-surface-2);
        border-left: 4px solid var(--secondary-green);
        border: 1px solid var(--border);
    }

    .stChatMessage[data-testid="assistant-message"] p,
    .stChatMessage:not(:has([data-testid*="user"])) p {
        color: var(--text-secondary);
    }

    /* ========================================
       EXPANDERS (View SQL Query, View Data)
       ======================================== */

    .streamlit-expanderHeader {
        background-color: transparent;
        border: none;
        font-weight: var(--weight-normal);
        color: var(--text-link);
        padding: 0.5rem 0;
    }

    .streamlit-expanderHeader:hover {
        color: var(--primary-green);
    }

    /* Expander Chevron Icon */
    .streamlit-expanderHeader svg {
        color: var(--text-link);
    }

    /* Expander Content */
    .streamlit-expanderContent {
        border: 1px solid var(--border);
        background-color: var(--bg-surface);
        border-radius: 4px;
        padding: 0.5rem;
    }

    /* ========================================
       CODE BLOCKS
       ======================================== */

    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid var(--border);
        background-color: var(--bg-surface);
    }

    code {
        color: var(--text-secondary);
    }

    /* ========================================
       DATA TABLES
       ======================================== */

    .stDataFrame {
        background-color: var(--bg-surface);
        border: 1px solid var(--border);
    }

    [data-testid="stDataFrameResizable"] {
        background-color: var(--bg-surface);
    }

    /* ========================================
       METRICS
       ======================================== */

    [data-testid="stMetricValue"] {
        color: var(--primary-green);
        font-weight: var(--weight-semibold);
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: var(--weight-normal);
    }

    /* ========================================
       TYPOGRAPHY & HEADINGS
       ======================================== */

    /* Section Headers */
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: var(--weight-semibold);
        letter-spacing: -0.02em;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Main Title */
    h1 {
        color: var(--text-primary);
        font-weight: var(--weight-semibold);
    }

    /* Section Title */
    h2 {
        padding-bottom: 0.5rem;
        font-weight: var(--weight-medium);
        border-bottom: none !important;
        font-size: 0.9rem;
        text-align: center;
    }

    /* Remove default Streamlit header underline */
    [data-testid="stHeader"],
    .stHeader,
    header {
        border-bottom: none !important;
    }

    /* Sub-section Title */
    h3 {
        font-weight: var(--weight-medium);
    }

    /* Body Paragraphs */
    p {
        color: var(--text-primary);
        line-height: 1.6;
    }

    /* ========================================
       REPORTS
       ======================================== */

    /* Report Containers */
    .report-container {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-primary);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
    }

    .report-header {
        color: var(--text-primary);
        font-weight: var(--weight-semibold);
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-primary);
    }

    .report-metadata {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: var(--weight-normal);
    }

    /* ========================================
       DIVIDERS & SEPARATORS
       ======================================== */

    .section-divider {
        height: 1px;
        background-color: var(--border-primary);
        margin: 2rem 0;
        border: none;
    }

    hr {
        border: none;
        height: 1px;
        background-color: var(--border-primary);
        margin: 2rem 0;
    }

    /* ========================================
       DATA TABLES
       ======================================== */

    .dataframe {
        border: 1px solid var(--border-secondary);
        border-radius: 10px;
        background-color: var(--bg-surface);
    }

    /* Table Headers */
    .dataframe thead th {
        background-color: var(--bg-canvas);
        color: var(--text-primary);
        font-weight: var(--weight-medium);
    }

    /* Table Body */
    .dataframe tbody td {
        color: var(--text-primary);
    }

    /* ========================================
       LINKS & INTERACTIVE TEXT
       ======================================== */

    /* Text Selection */
    ::selection {
        background-color: var(--emb-primary);
        color: var(--text-on-primary);
    }

    /* Links */
    a {
        color: var(--text-link);
        text-decoration: none;
        font-weight: var(--weight-normal);
    }

    a:hover {
        color: var(--text-link);
        text-decoration: underline;
    }

    /* ========================================
       UTILITY CLASSES
       ======================================== */

    /* Icon Colors */
    .icon-primary {
        color: var(--emb-primary);
    }

    .icon-info {
        color: var(--text-secondary);
    }

    /* No Shadows - Enterprise Clean */
    * {
        box-shadow: none !important;
    }

    /* Remove Focus Glow */
    *:focus {
        outline: none;
        box-shadow: none !important;
    }

    /* Consistent Border Radius */
    .stButton, .stChatInput, .stExpander, .dataframe {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the system components."""
    try:
        logger.info("Initializing system...")

        # Check for API key
        if not OPENROUTER_API_KEY:
            st.error("OpenRouter API key not found. Please set it in your .env file.")
            st.stop()

        # Load data
        loader = DataLoader(EXCEL_DIR)
        dataframes = loader.load_all_files()

        # Initialize database
        db_handler = DatabaseHandler(DB_URL)
        db_handler.create_tables_from_dataframes(dataframes)

        # Initialize SQL agent
        try:
            sql_agent = SQLAgentHandler(
                db_url=DB_URL,
                api_key=OPENROUTER_API_KEY,
                model=OPENROUTER_MODEL
            )
        except ValueError as e:
            # Handle API key validation errors
            st.error("❌ OpenRouter API Configuration Error")
            st.error(str(e))
            st.info("📝 Steps to fix:\n1. Visit https://openrouter.ai/keys\n2. Sign up/login and create an API key\n3. Copy your API key (starts with 'sk-or-v1-')\n4. Update your .env file:\n   ```\n   OPENROUTER_API_KEY=sk-or-v1-your-actual-key\n   ```\n5. Restart the application")
            st.stop()

        # Initialize chart generator
        chart_gen = ChartGenerator(theme=CHART_THEMES['plotly'])

        # Initialize report generators
        report_gen = ReportGenerator(PROCESSED_DIR)
        advanced_report_gen = AdvancedReportGenerator(PROCESSED_DIR, llm_handler=sql_agent)

        # Initialize cache manager
        cache_manager = None
        if CACHE_ENABLED:
            try:
                cache_manager = CacheManager(
                    cache_db_path=str(CACHE_DB_PATH),
                    default_ttl_seconds=CACHE_DEFAULT_TTL,
                    max_cache_size_mb=CACHE_MAX_SIZE_MB,
                    max_result_size_bytes=CACHE_MAX_RESULT_SIZE_MB * 1024 * 1024
                )
                logger.info("Cache manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize cache manager: {e}")
                logger.info("Continuing without caching...")

        logger.info("System initialized successfully")

        return {
            'loader': loader,
            'db_handler': db_handler,
            'sql_agent': sql_agent,
            'chart_gen': chart_gen,
            'report_gen': report_gen,
            'advanced_report_gen': advanced_report_gen,
            'cache_manager': cache_manager
        }

    except ValueError as e:
        # Catch validation errors (already handled above, but just in case)
        logger.error(f"Validation error: {str(e)}")
        st.error(f"❌ Configuration Error: {str(e)}")
        st.stop()
    except Exception as e:
        logger.error(f"System initialization error: {str(e)}")
        error_msg = str(e).lower()

        # Check for authentication-related errors
        if "401" in error_msg or "unauthorized" in error_msg or "cookie auth" in error_msg:
            st.error("❌ OpenRouter API Authentication Failed")
            st.error("Your API key appears to be invalid or has expired.")
            st.info("📝 Steps to fix:\n1. Visit https://openrouter.ai/keys\n2. Check if your API key is still valid\n3. Generate a new key if needed\n4. Update your .env file with the new key\n5. Restart the application")
        else:
            st.error(f"❌ Error initializing system: {str(e)}")
            st.info("Please check the error message above and ensure all dependencies are installed correctly.")
        st.stop()


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'current_chart' not in st.session_state:
        st.session_state.current_chart = None
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = OPENROUTER_MODEL
    if 'model_display_name' not in st.session_state:
        # Find the display name for the default model
        for display_name, model_id in AVAILABLE_MODELS.items():
            if model_id == OPENROUTER_MODEL:
                st.session_state.model_display_name = display_name
                break
        else:
            st.session_state.model_display_name = "GPT-4 Turbo"


def display_sidebar(components):
    """Display sidebar with database info and sample questions."""
    with st.sidebar:
        st.header("Database Information")

        # Get database info
        db_info = components['db_handler'].get_database_info()

        st.metric("Total Tables", db_info['table_count'])

        with st.expander("Table Details"):
            for table_name, info in db_info['tables'].items():
                st.write(f"**{table_name}**")
                st.write(f"- Rows: {info['row_count']}")
                st.write(f"- Columns: {info['column_count']}")
                st.write(f"- Fields: {', '.join([col['name'] for col in info['columns'][:5]])}")
                if info['column_count'] > 5:
                    st.write(f"  ... and {info['column_count'] - 5} more")
                st.divider()

        st.header("Model Selection")

        # Model selector dropdown
        model_options = list(AVAILABLE_MODELS.keys())
        selected_display_name = st.selectbox(
            "Choose Language Model",
            options=model_options,
            index=model_options.index(st.session_state.model_display_name) if st.session_state.model_display_name in model_options else 0,
            key="model_selector",
            help="Select the OpenRouter model to use for generating SQL queries and answers"
        )

        # Update session state if model changed
        if selected_display_name != st.session_state.model_display_name:
            st.session_state.model_display_name = selected_display_name
            st.session_state.selected_model = AVAILABLE_MODELS[selected_display_name]

            # Reinitialize the SQL agent with new model
            try:
                components['sql_agent'] = SQLAgentHandler(
                    db_url=DB_URL,
                    api_key=OPENROUTER_API_KEY,
                    model=st.session_state.selected_model
                )
                st.success(f"✓ Switched to {selected_display_name}")
                logger.info(f"Model changed to: {st.session_state.selected_model}")
            except Exception as e:
                st.error(f"Error switching model: {str(e)}")
                logger.error(f"Error switching model: {str(e)}")

        st.header("Sample Questions")

        sample_questions = get_all_sample_questions()

        for category in get_categories():
            with st.expander(category):
                for question in sample_questions[category]:
                    if st.button(question, key=f"sample_{category}_{question}"):
                        st.session_state.selected_question = question


def process_user_query(question: str, components):
    """Process user query and return response."""
    try:
        # ALWAYS use free Llama model in backend (regardless of UI selection)
        current_model = "meta-llama/llama-3.1-8b-instruct:free"

        # CHECK CACHE FIRST (if cache manager is available)
        cache_manager = components.get('cache_manager')
        if cache_manager and CACHE_ENABLED:
            try:
                cached_result = cache_manager.get(question, current_model)
                if cached_result:
                    # VALIDATE: Don't return cached errors
                    answer = cached_result.get('answer', '')
                    if 'Error code:' in answer or answer.startswith('Error'):
                        logger.warning(f"Cached result contains error, deleting and re-executing: {answer[:100]}")
                        # Delete this cached error immediately
                        try:
                            conn = cache_manager._get_connection()
                            cursor = conn.cursor()
                            cache_key, _ = cache_manager._generate_cache_key(question, current_model)
                            cursor.execute("DELETE FROM query_cache WHERE cache_key = ?", (cache_key,))
                            conn.commit()
                            logger.info(f"Deleted cached error for question: {question[:50]}...")
                        except Exception as del_error:
                            logger.error(f"Failed to delete cached error: {del_error}")
                        # Don't return error - let it re-execute
                    # If answer is empty, don't return cache - let chart/report generation run
                    elif answer and answer.strip():
                        logger.info("Cache HIT - returning valid cached result with answer")
                        return cached_result
                    else:
                        logger.info("Cache HIT but answer is empty - continuing to generate chart/report")
            except Exception as e:
                logger.error(f"Cache retrieval failed: {e}")
                # Continue with normal query execution

        # CACHE MISS - proceed with normal flow
        if cache_manager:
            logger.info("Cache MISS - querying LLM")

        # Track execution time for caching
        start_time = datetime.now()

        # Check if it's a report request
        is_report_request = ChartRequestParser.detect_report_request(question)

        # Detect professional report keywords
        is_professional_report = any(keyword in question.lower() for keyword in [
            'professional report', 'detailed report', 'comprehensive report',
            'executive summary', 'financial report', 'analysis report'
        ])

        # Check if it's a chart request
        chart_type = ChartRequestParser.detect_chart_request(question)

        # Try template first (no API call!) - same as cache warming
        template_data = None  # Store DataFrame from template execution
        if has_template(question):
            logger.info("Using SQL template (no API call)")
            sql_query = get_template_sql(question)

            # Execute template SQL directly
            try:
                result_data = components['db_handler'].execute_query(sql_query)
                template_data = result_data  # Store for reuse

                # For chart/report requests, generate minimal answer - let chart/report code handle display
                if chart_type or is_report_request or is_professional_report:
                    # Minimal answer for chart/report requests
                    answer = f"Query returned {len(result_data)} result(s)."
                    logger.info(f"Chart/report request detected - will generate visualization/report below")
                else:
                    # Generate detailed answer for regular queries
                    if result_data.empty:
                        answer = "No data found for the specified criteria."
                    elif len(result_data) == 1 and len(result_data.columns) == 1:
                        value = result_data.iloc[0, 0]
                        col_name = result_data.columns[0].replace('_', ' ').title()
                        if isinstance(value, (int, float)):
                            if any(keyword in col_name.lower() for keyword in ['price', 'amount', 'value', 'total', 'cost', 'revenue', 'sales', 'payment']):
                                answer = f"The {col_name} is ${value:,.2f}"
                            else:
                                answer = f"The {col_name} is {value:,}"
                        else:
                            answer = f"The {col_name} is {value}"
                    elif len(result_data) <= 10:
                        answer = f"Query returned {len(result_data)} result(s)."
                    else:
                        answer = f"Found {len(result_data)} result(s)."

                # Create result dict matching LLM format
                result = {
                    'answer': answer,
                    'sql_query': sql_query
                }
            except Exception as e:
                logger.error(f"Template SQL failed: {e}")
                result = {
                    'answer': f"Error executing query: {str(e)}",
                    'sql_query': None
                }
                template_data = None
        else:
            # Fallback to LLM for non-template questions
            logger.info("No template found, calling LLM API...")
            result = components['sql_agent'].query(question)

        response = {
            'question': question,
            'answer': result['answer'],
            'sql_query': result.get('sql_query'),
            'data': None,
            'chart': None,
            'report_path': None
        }

        # Debug logging
        logger.info(f"Is report request: {is_report_request}")
        logger.info(f"Chart type detected: {chart_type}")
        logger.info(f"SQL query from result: {result.get('sql_query')}")
        logger.info(f"Answer from LLM: {result.get('answer')[:200]}")

        # If we have a SQL query, get the data
        if result.get('sql_query'):
            try:
                # Reuse template data if available (avoid re-executing query)
                if template_data is not None:
                    df = template_data
                    logger.info("Reusing DataFrame from template execution (no re-query)")
                else:
                    df = components['db_handler'].execute_query(result['sql_query'])
                    logger.info("Executed SQL query to get DataFrame")

                response['data'] = df
                st.session_state.current_data = df

                # For non-chart, non-report queries: Keep the LLM's natural language answer
                # Only generate simple answers if LLM didn't provide one
                if not chart_type and not is_report_request:
                    # CRITICAL: If dataframe is empty, always override with clear message
                    if df.empty:
                        response['answer'] = "No data found for the specified criteria. The database may not contain records matching your query parameters."
                        logger.info("DataFrame is empty - generated 'no data' message")
                    # Keep LLM answer if it exists and is meaningful (and we have data)
                    elif response.get('answer') and response['answer'].strip():
                        # Check if the answer is overly verbose/generic (> 500 chars suggests generic filler)
                        if len(response['answer']) > 500:
                            logger.warning(f"LLM answer is verbose ({len(response['answer'])} chars), may be generic filler - generating data-driven answer")
                            # Generate concise data-driven answer instead
                            if len(df) == 1 and len(df.columns) == 1:
                                # Single value result (like COUNT, AVG, etc.)
                                value = df.iloc[0, 0]
                                column_name = df.columns[0].replace('_', ' ').title()

                                # Format the value based on column name
                                if isinstance(value, (int, float)):
                                    # Check if it's likely a currency value
                                    if any(keyword in column_name.lower() for keyword in ['price', 'amount', 'value', 'total', 'cost', 'revenue', 'sales']):
                                        response['answer'] = f"The {column_name} is ${value:,.2f}"
                                    else:
                                        response['answer'] = f"The {column_name} is {value:,.2f}"
                                else:
                                    response['answer'] = f"The {column_name} is {value}"
                                logger.info(f"Generated data-driven answer from single value: {response['answer']}")
                            elif len(df) <= 10:
                                # Small result set - provide summary
                                response['answer'] = f"Query returned {len(df)} result(s). Please see the data table below for details."
                                logger.info(f"Generated data-driven answer for small result set: {response['answer']}")
                            else:
                                # Large result set - just mention count
                                response['answer'] = f"Found {len(df)} result(s). Please see the data table below for details."
                                logger.info(f"Generated data-driven answer for large result set: {response['answer']}")
                        else:
                            logger.info(f"Keeping concise LLM-generated answer: {response['answer'][:100]}")
                    else:
                        # LLM didn't provide an answer - generate fallback
                        if len(df) == 1 and len(df.columns) == 1:
                            # Single value result (like COUNT, AVG, etc.)
                            value = df.iloc[0, 0]
                            column_name = df.columns[0].replace('_', ' ').title()

                            # Format the value based on column name
                            if isinstance(value, (int, float)):
                                # Check if it's likely a currency value
                                if any(keyword in column_name.lower() for keyword in ['price', 'amount', 'value', 'total', 'cost', 'revenue', 'sales']):
                                    response['answer'] = f"The {column_name} is ${value:,.2f}"
                                else:
                                    response['answer'] = f"The {column_name} is {value:,.2f}"
                            else:
                                response['answer'] = f"The {column_name} is {value}"
                            logger.info(f"Generated fallback answer from single value: {response['answer']}")
                        elif len(df) <= 10:
                            # Small result set - provide summary
                            response['answer'] = f"Query returned {len(df)} result(s)."
                            logger.info(f"Generated fallback answer for small result set: {response['answer']}")
                        else:
                            # Large result set - just mention count
                            response['answer'] = f"Found {len(df)} result(s)."
                            logger.info(f"Generated fallback answer for large result set: {response['answer']}")

                # Generate chart ONLY if explicitly requested
                if chart_type and not df.empty:
                    chart = components['chart_gen'].generate_chart(
                        df,
                        chart_type=chart_type,
                        title=f"{chart_type.title()} Chart"
                    )
                    response['chart'] = chart
                    st.session_state.current_chart = chart
                    # Clear the generic answer text - the chart speaks for itself
                    response['answer'] = ''
                    logger.info(f"Chart generated successfully, cleared generic answer text")

                # DO NOT auto-generate charts for regular queries
                # Charts are only generated when:
                # 1. User explicitly requests a chart (chart_type is set)
                # 2. User requests a report (handled separately below)

                # Generate report if requested - ALWAYS use professional format
                if is_report_request:
                    if df.empty:
                        logger.warning(f"Cannot generate report: DataFrame is empty")
                        response['answer'] += "\n\n⚠️ Note: The query returned no data, so the report cannot be generated."
                    else:
                        logger.info(f"Generating professional report for {len(df)} rows x {len(df.columns)} columns")
                        try:
                            # Always use advanced report generator with AI summary for chat display
                            charts_for_report = [response['chart']] if response['chart'] else []

                            # Generate professional report content for chat
                            report_content = components['advanced_report_gen'].generate_report_content(
                                company_name=COMPANY_NAME,
                                report_title=f"Analysis Report: {question[:60]}",
                                data=df,
                                query_context=question,
                                charts=charts_for_report if charts_for_report else None,
                                include_kpis=True,
                                include_executive_summary=True,
                                auto_generate_charts=True  # Enable auto chart generation
                            )
                            response['report_content'] = report_content

                            # CRITICAL: Clear the LLM's answer so the structured report is displayed instead
                            # The LLM generates its own text report, but we want the formatted professional report
                            response['answer'] = ''
                            logger.info(f"✅ Report generated with {len(report_content.get('sections', {}))} sections, LLM answer cleared")
                        except Exception as report_error:
                            logger.error(f"Error generating report: {str(report_error)}", exc_info=True)
                            response['answer'] += f"\n\n⚠️ Error generating report: {str(report_error)}"

            except Exception as e:
                logger.error(f"Error processing query results: {str(e)}", exc_info=True)

        # STORE IN CACHE before returning (if cache manager available and query was successful)
        if cache_manager and CACHE_ENABLED and result.get('sql_query'):
            # CRITICAL: Never cache error responses
            answer = response['answer']
            if 'Error code:' not in answer and not answer.startswith('Error'):
                try:
                    execution_time = (datetime.now() - start_time).total_microseconds / 1000
                    cache_manager.set(
                        question=question,
                        model_name=current_model,
                        sql_query=result.get('sql_query'),
                        answer=answer,
                        result_data=response.get('data'),
                        execution_time_ms=execution_time
                    )
                    logger.info(f"Successfully cached result for: {question[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to cache result: {e}")
                    # Continue anyway - caching failure shouldn't break the app
            else:
                logger.warning(f"Skipping cache for error response: {answer[:100]}")

        return response

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {
            'question': question,
            'answer': f"Error: {str(e)}",
            'sql_query': None,
            'data': None,
            'chart': None,
            'report_path': None
        }


def display_chat_message(message):
    """Display a chat message."""
    role = message['role']
    content = message['content']

    with st.chat_message(role):
        # Cache indicator removed per user request
        # answer_text = content.get('answer', '')
        # is_error = answer_text.startswith('Error') or 'Error code:' in answer_text
        # if content.get('cached') and not is_error:
        #     st.info("⚡ Result from cache", icon="⚡")

        # Display professional report if available
        if content.get('report_content'):
            display_report_in_chat(content['report_content'])
        else:
            st.write(content['answer'])

        # Display SQL query if available
        if content.get('sql_query'):
            with st.expander("View SQL Query"):
                st.code(content['sql_query'], language='sql')

        # Display data table if available
        if content.get('data') is not None and not content['data'].empty:
            with st.expander(f"View Data ({len(content['data'])} rows)"):
                st.dataframe(content['data'], use_container_width=True)

        # Display chart if available (not part of report)
        if content.get('chart') and not content.get('report_content'):
            st.plotly_chart(content['chart'], use_container_width=True)

        # Display report link if available (old basic reports)
        if content.get('report_path'):
            st.success(f"Report generated successfully!")
            with open(content['report_path'], 'rb') as f:
                st.download_button(
                    label="Download Report (PDF)",
                    data=f,
                    file_name=Path(content['report_path']).name,
                    mime='application/pdf'
                )


def display_report_in_chat(report_content):
    """Display professional report content in chat."""
    # Executive Summary
    if 'executive_summary' in report_content['sections']:
        st.markdown("### Executive Summary")
        st.write(report_content['sections']['executive_summary'])
        st.markdown("")

    # KPIs
    if 'kpis' in report_content['sections']:
        st.markdown("### Key Performance Metrics")
        kpis = report_content['sections']['kpis']

        # Display KPIs in columns
        cols = st.columns(2)
        for i, kpi in enumerate(kpis):
            with cols[i % 2]:
                st.metric(label=kpi['label'], value=kpi['value'])
        st.markdown("")

    # Insights
    if 'insights' in report_content['sections']:
        st.markdown("### Key Insights & Analysis")
        insights_text = report_content['sections']['insights']

        # Parse numbered insights
        import re
        if re.search(r'^\d+\.', insights_text.strip(), re.MULTILINE):
            # Split by numbered pattern to get all insights
            insights_list = []
            lines = insights_text.split('\n')
            current_insight = ""
            current_number = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line starts with a number
                match = re.match(r'^(\d+)\.\s*(.+)', line)
                if match:
                    # Save previous insight if exists
                    if current_number is not None and current_insight:
                        insights_list.append((current_number, current_insight.strip()))

                    # Start new insight
                    current_number = int(match.group(1))
                    current_insight = match.group(2)
                else:
                    # Continuation of current insight
                    if current_number is not None:
                        current_insight += " " + line

            # Add last insight
            if current_number is not None and current_insight:
                insights_list.append((current_number, current_insight.strip()))

            # Display all insights in order
            for num, insight in insights_list:
                st.markdown(f"**{num}.** {insight}")
                st.markdown("")
        else:
            st.write(insights_text)

    # Charts
    if report_content.get('charts'):
        st.markdown("### Visual Analysis & Trends")
        for chart in report_content['charts']:
            st.plotly_chart(chart, use_container_width=True)


def main():
    """Main application function."""
    # Initialize
    initialize_session_state()
    components = initialize_system()

    # Clear any cached errors on EVERY startup (before session check)
    if CACHE_ENABLED and components.get('cache_manager'):
        cache_manager = components.get('cache_manager')
        if cache_manager and 'cache_cleared' not in st.session_state:
            try:
                logger.info("Clearing cached errors and generic chart/report answers on startup...")
                # Clear ALL cache entries that contain error responses OR generic answers for chart/report questions
                conn = cache_manager._get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM query_cache
                    WHERE answer LIKE '%Error code:%'
                       OR answer LIKE 'Error%'
                       OR answer LIKE '%404%'
                       OR answer LIKE '%402%'
                       OR (
                           (question LIKE '%chart%' OR question LIKE '%report%' OR question LIKE '%graph%')
                           AND (answer LIKE 'Found % result(s)%' OR answer LIKE 'Query returned % result(s)%')
                       )
                """)
                deleted_count = cursor.rowcount
                conn.commit()
                if deleted_count > 0:
                    logger.info(f"Cleared {deleted_count} cached error(s) and generic chart/report answer(s) on startup")
                st.session_state.cache_cleared = True
            except Exception as e:
                logger.warning(f"Failed to clear cached errors: {e}")

    # Warm cache with suggested questions (only on first run)
    if CACHE_ENABLED and components.get('cache_manager'):
        if 'cache_warmed' not in st.session_state:
            with st.spinner('Preparing suggested questions...'):
                try:
                    # ALWAYS use free Llama model for cache warming
                    current_model = "meta-llama/llama-3.1-8b-instruct:free"
                    stats = warm_cache_on_startup(components, current_model)
                    if stats.get('success'):
                        logger.info(f"Cache warming successful: {stats.get('cached_count')} questions cached")
                        st.session_state.cache_warmed = True
                    else:
                        logger.warning(f"Cache warming failed: {stats.get('reason', 'Unknown')}")
                        st.session_state.cache_warmed = False
                except Exception as e:
                    logger.error(f"Cache warming error: {e}")
                    st.session_state.cache_warmed = False

    # Header
    st.markdown('<div class="app-subtitle">NL to SQL Intelligence Platform</div>', unsafe_allow_html=True)

    # Display sidebar
    display_sidebar(components)

    # Chat interface
    st.header("Chat with Your Data")

    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message)

    # Handle selected sample question
    if 'selected_question' in st.session_state:
        question = st.session_state.selected_question
        del st.session_state.selected_question

        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': {'answer': question}
        })

        # Process query
        with st.spinner('Processing your question...'):
            response = process_user_query(question, components)

        # Add assistant message
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response
        })

        st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': {'answer': prompt}
        })

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Process query
        with st.chat_message("assistant"):
            with st.spinner('Processing your question...'):
                response = process_user_query(prompt, components)

            # Display professional report if available
            if response.get('report_content'):
                display_report_in_chat(response['report_content'])
            else:
                # Display response
                st.write(response['answer'])

            # Display SQL query if available
            if response.get('sql_query'):
                with st.expander("View SQL Query"):
                    st.code(response['sql_query'], language='sql')

            # Display data table if available
            if response.get('data') is not None and not response['data'].empty:
                with st.expander(f"View Data ({len(response['data'])} rows)"):
                    st.dataframe(response['data'], use_container_width=True)

            # Display chart if available (not part of report)
            if response.get('chart') and not response.get('report_content'):
                st.plotly_chart(response['chart'], use_container_width=True)

            # Display report link if available (old basic reports)
            if response.get('report_path'):
                st.success(f"Report generated successfully!")
                with open(response['report_path'], 'rb') as f:
                    st.download_button(
                        label="Download Report (PDF)",
                        data=f,
                        file_name=Path(response['report_path']).name,
                        mime='application/pdf'
                    )

        # Add assistant message to history
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response
        })

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.current_data = None
            st.session_state.current_chart = None
            st.rerun()

    with col2:
        if st.session_state.current_data is not None:
            csv = st.session_state.current_data.to_csv(index=False)
            st.download_button(
                label="Download Last Result (CSV)",
                data=csv,
                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )

    with col3:
        st.write(f"Messages: {len(st.session_state.messages)}")


if __name__ == "__main__":
    main()
