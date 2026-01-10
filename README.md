# NLP to SQL Chat Application

A powerful Streamlit-based application that allows users to chat with their data using natural language. The app automatically normalizes Excel/CSV data, converts natural language questions to SQL queries, generates visualizations, and creates detailed reports.

## Features

- **Natural Language to SQL**: Ask questions in plain English and get SQL queries automatically generated
- **Data Normalization**: Automatically cleans and normalizes CSV/Excel files
- **Interactive Chat Interface**: User-friendly chat interface powered by Streamlit
- **Visualizations**: Generate charts and graphs (bar, line, pie, scatter, histogram, etc.)
- **Professional Reports**: Generate advanced reports with AI-powered executive summaries and KPIs
- **Sample Questions**: Pre-built question templates to get started quickly
- **LangSmith Integration**: Track and monitor LLM interactions
- **OpenRouter LLM**: Uses OpenRouter API for flexible model selection

## Project Structure

```
NLP to SQL/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── data_loader.py              # Data loading and normalization
├── database_handler.py         # SQLite database operations
├── llm_handler.py              # LangChain SQL agent and LLM integration
├── chart_generator.py          # Chart and visualization generation
├── sample_questions.py         # Sample question templates
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment variables
├── data/
│   ├── excel_files/           # Source CSV/Excel files
│   └── processed/             # Generated reports
└── database/
    └── normalized_data.db     # SQLite database (auto-generated)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone or Download the Project

Navigate to the project directory:
```bash
cd "/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file and add your API keys:
```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=openai/gpt-4-turbo

# LangSmith Configuration (Optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=nlp-to-sql-app
```

### Step 5: Add Your Data Files

Place your CSV or Excel files in the `data/excel_files/` directory. The app currently has sample files:
- customers.csv
- employees.csv
- offices.csv
- orders.csv
- orderdetails.csv
- payments.csv
- products.csv
- productlines.csv

You can add your own files in supported formats: `.csv`, `.xlsx`, `.xls`

## Usage

### Start the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Using the Chat Interface

1. **View Database Information**: Check the sidebar to see all loaded tables and their schemas

2. **Ask Questions**: Type your question in the chat input or click on sample questions

3. **View Results**:
   - Natural language answer
   - Generated SQL query (expandable)
   - Data table (expandable)
   - Auto-generated charts (when applicable)

4. **Generate Charts**: Include chart keywords in your question:
   - "Show me a bar chart of..."
   - "Create a pie chart for..."
   - "Generate a line graph of..."

5. **Generate Reports**: Request detailed reports:
   - "Generate a detailed report on..."
   - "Create a sales report with charts"

### Sample Questions

#### Basic Queries
- "Show me all customers"
- "How many orders do we have?"
- "What are the top 5 products by price?"

#### Aggregation Queries
- "What is the total revenue from all orders?"
- "How many customers are in each country?"
- "What is the average order value?"

#### Analysis Queries
- "Which customers have spent the most?"
- "What are the top selling products?"
- "Show me monthly sales trends"

#### Chart Requests
- "Show me a bar chart of products by price"
- "Create a pie chart of customers by country"
- "Generate a line chart of orders over time"

#### Report Requests
- "Generate a detailed sales report"
- "Create a customer analysis report with charts"
- "Generate a product performance report"

#### Professional Report Requests (with AI Summaries & KPIs)
- "Generate a professional report on customer data"
- "Create a detailed report with executive summary on sales"
- "Generate a comprehensive analysis report on products"
- "Create a financial report with KPIs on orders"

## Features in Detail

### Data Normalization

The app automatically:
- Cleans column names (lowercase, underscores)
- Handles missing values (median for numeric, mode for categorical)
- Removes duplicates
- Detects and converts date columns
- Strips whitespace from strings

### Chart Types Supported

- **Bar Chart**: Categorical comparisons
- **Line Chart**: Trends over time
- **Pie Chart**: Proportional distributions
- **Scatter Plot**: Correlations between variables
- **Histogram**: Frequency distributions
- **Box Plot**: Statistical distributions
- **Heatmap**: Correlation matrices

### Report Generation

The application offers two types of reports:

#### Basic Reports
- Quick data summaries
- Key insights
- Data tables
- Visualizations
- Timestamp and metadata

#### Professional Reports (Advanced)
- **Header Section**: Company name, report title, date, timestamp
- **AI-Powered Executive Summary**: 2-3 paragraph summary generated by LLM, grounded in actual data
- **Key Performance Indicators (KPIs)**: Auto-extracted metrics in professional 2-column layout
- **AI-Powered Key Insights**: 3-4 intelligent findings and business implications (no raw data tables)
- **Visual Analysis**: Embedded charts and visualizations
- **Professional Formatting**: A4 page size, consistent fonts and colors, proper number formatting

To generate a professional report, use keywords like:
- "professional report"
- "detailed report with executive summary"
- "comprehensive analysis report"
- "financial report with KPIs"

Reports are saved as PDF files in `data/processed/`

### LangSmith Integration

If configured, all LLM interactions are tracked in LangSmith for:
- Query performance monitoring
- Debugging SQL generation
- Cost tracking
- Quality assurance

## API Keys

### OpenRouter API Key

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Go to API Keys section
3. Create a new API key
4. Add to `.env` file

### LangSmith API Key (Optional)

1. Sign up at [LangSmith](https://smith.langchain.com/)
2. Create a new API key
3. Add to `.env` file

## Troubleshooting

### Common Issues

1. **"Error code: 401 - No cookie auth credentials found"** ⚠️ MOST COMMON
   - **Cause**: Invalid or missing OpenRouter API key
   - **Solution**:
     1. Visit https://openrouter.ai/keys
     2. Sign up/login and create an API key
     3. Copy your API key (format: `sk-or-v1-...`)
     4. Update `.env` file:
        ```
        OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
        ```
     5. Restart the application: `streamlit run app.py`

2. **"Invalid OpenRouter API key" error on startup**
   - **Cause**: Your `.env` file still contains the placeholder value
   - **Solution**: Replace `your_openrouter_api_key_here` with your actual API key from https://openrouter.ai/keys

3. **Pillow installation error (Python 3.11)**
   - **Cause**: Old Pillow version incompatible with Python 3.11
   - **Solution**: The `requirements.txt` has been updated. Run:
     ```bash
     pip install --upgrade -r requirements.txt
     ```

4. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

5. **"API key not found" error**
   - Check `.env` file exists and contains your API key
   - Ensure `.env` is in the project root directory

6. **"No data files found" error**
   - Verify CSV/Excel files are in `data/excel_files/`
   - Check file extensions are supported (.csv, .xlsx, .xls)

7. **Database errors**
   - Delete `database/normalized_data.db` and restart the app
   - The database will be recreated automatically

8. **Chart generation errors**
   - Ensure data has appropriate columns for the chart type
   - Check that numeric columns exist for numeric charts

## Advanced Configuration

### Changing the LLM Model

Edit `config.py` or set in `.env`:
```python
OPENROUTER_MODEL=anthropic/claude-3-sonnet  # or any OpenRouter model
```

### Customizing Chart Themes

Edit `config.py`:
```python
CHART_THEMES = {
    "plotly": "plotly_dark",  # or any Plotly theme
    "colors": ["#custom", "#colors"]
}
```

### Adding Custom Sample Questions

Edit `sample_questions.py` to add your own question categories and templates.

## Performance Tips

1. **For large datasets**:
   - Consider adding row limits to queries
   - Use aggregations instead of full table scans

2. **For faster responses**:
   - Use more specific questions
   - Include table names when known

3. **For better visualizations**:
   - Request specific chart types
   - Limit data to reasonable amounts (< 100 rows for scatter plots)

## Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment-specific `.env` files for different deployments
- The database is local SQLite - suitable for development and small datasets

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the sample questions for usage examples
- Consult the LangChain and Streamlit documentation

## Technologies Used

- **Streamlit**: Web interface
- **LangChain**: LLM orchestration and SQL chain
- **OpenRouter**: LLM API gateway
- **SQLAlchemy**: Database ORM
- **Plotly**: Interactive visualizations
- **ReportLab**: PDF generation
- **Pandas**: Data manipulation
- **LangSmith**: LLM observability (optional)

## Version History

- **v1.0.0**: Initial release
  - NLP to SQL conversion
  - Chart generation
  - Report generation
  - Sample questions
  - LangSmith integration

---

Built with ❤️ using Streamlit, LangChain, and OpenRouter

