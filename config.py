"""Configuration module for NL-to-SQL application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXCEL_DIR = DATA_DIR / "excel_files"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = BASE_DIR / "database"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Database configuration
DB_PATH = DB_DIR / "normalized_data.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Cache configuration
CACHE_DB_PATH = DB_DIR / "query_cache.db"
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24 hours
CACHE_MAX_SIZE_MB = int(os.getenv("CACHE_MAX_SIZE_MB", "500"))
CACHE_MAX_RESULT_SIZE_MB = int(os.getenv("CACHE_MAX_RESULT_SIZE_MB", "10"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Available OpenRouter models
AVAILABLE_MODELS = {
    "GPT-4 Turbo": "openai/gpt-4-turbo",
    "GPT-4": "openai/gpt-4",
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Claude 3 Haiku": "anthropic/claude-3-haiku",
    "Gemini Pro": "google/gemini-pro",
    "Llama 3 70B": "meta-llama/llama-3-70b-instruct",
    "Mixtral 8x7B": "mistralai/mixtral-8x7b-instruct"
}

# LangSmith configuration
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "nlp-to-sql-app")

# Streamlit configuration
PAGE_TITLE = "EMB Global - NL to SQL Intelligence"
PAGE_ICON = "🌿"  # Leaf icon matching EMB Global's green logo
LAYOUT = "wide"

# Chart configuration
CHART_THEMES = {
    "plotly": "plotly_white",
    "colors": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]
}

# Supported file formats
SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls"]

# LLM parameters
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 2000

# Report configuration
COMPANY_NAME = os.getenv("COMPANY_NAME", "EMB Global")
