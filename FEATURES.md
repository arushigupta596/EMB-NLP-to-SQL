# Features Overview

## Core Capabilities

### 1. Natural Language to SQL Conversion

Convert plain English questions into SQL queries automatically.

**Examples:**
- "How many customers are in France?" → `SELECT COUNT(*) FROM customers WHERE country = 'France'`
- "What are the top 5 products by price?" → `SELECT * FROM products ORDER BY price DESC LIMIT 5`
- "Show me total sales by month" → Complex aggregation query with date grouping

**Powered by:**
- LangChain SQL Agent
- OpenRouter LLM (configurable models)
- Intelligent query generation and validation

---

### 2. Automatic Data Normalization

Your data files are automatically cleaned and normalized when loaded.

**Normalization includes:**
- ✓ Column name standardization (lowercase, underscores)
- ✓ Duplicate removal (rows and columns)
- ✓ Missing value handling (intelligent fill strategies)
- ✓ Data type detection and conversion
- ✓ Date/time parsing
- ✓ Whitespace trimming
- ✓ Index reset

**Supported formats:**
- CSV (.csv)
- Excel (.xlsx, .xls)

---

### 3. Interactive Chat Interface

User-friendly Streamlit interface with conversational interactions.

**Features:**
- 💬 Chat-based question/answer format
- 📊 Inline data tables (expandable)
- 📈 Automatic chart generation
- 📋 SQL query display (expandable)
- 🔄 Chat history preservation
- ⬇️ Export results to CSV
- 🗑️ Clear chat history option

---

### 4. Intelligent Visualization

Automatically generate appropriate charts based on your data and question.

**Chart Types:**

| Chart Type | Use Case | Example Question |
|------------|----------|------------------|
| Bar Chart | Categorical comparisons | "Show sales by region" |
| Line Chart | Trends over time | "Revenue trend by month" |
| Pie Chart | Proportional distribution | "Customer distribution by country" |
| Scatter Plot | Correlation analysis | "Price vs quantity relationship" |
| Histogram | Frequency distribution | "Distribution of order values" |
| Box Plot | Statistical distribution | "Product price ranges" |
| Heatmap | Correlation matrix | "Correlation between metrics" |

**Auto-detection:**
- Analyzes data structure
- Chooses optimal visualization
- Customizable chart themes
- Interactive Plotly charts

---

### 5. Report Generation

Create comprehensive PDF reports with charts and insights.

**Report includes:**
- 📄 Executive title and timestamp
- 🔍 Auto-generated insights
- 📊 Data tables (formatted)
- 📈 Visualizations
- 📉 Statistical summaries

**Request examples:**
- "Generate a sales report"
- "Create a customer analysis report with charts"
- "Generate a detailed product performance report"
---

### 6. Sample Questions Library

Pre-built question templates organized by category.

**Categories:**

1. **Basic Queries**
   - Simple data retrieval
   - Table exploration
   - Record counting

2. **Aggregation Queries**
   - Sum, average, count
   - Group by operations
   - Statistical calculations

3. **Analysis Queries**
   - Top/bottom N queries
   - Trend analysis
   - Comparative analysis

4. **Chart Requests**
   - Specific visualization types
   - Multi-series charts
   - Custom chart parameters

5. **Report Requests**
   - Comprehensive reports
   - Domain-specific analysis
   - Multi-chart reports

6. **Complex Queries**
   - Joins across tables
   - Subqueries
   - Advanced filtering

**Access:**
- Click any sample question in sidebar
- Auto-populated in chat
- Customizable templates

---

### 7. Multi-Table Support

Work with multiple related tables simultaneously.

**Features:**
- Auto-detect table relationships
- Join tables intelligently
- Cross-table queries
- Foreign key understanding

**Example:**
"Show me customers and their orders" → Automatically joins customers and orders tables

---

### 8. Database Schema Explorer

View and understand your database structure.

**Sidebar shows:**
- Total table count
- Table names
- Row counts
- Column names and types
- Sample data preview

**Benefits:**
- Quick reference
- Data exploration
- Schema understanding
- Query planning

---

### 9. Export Capabilities

Download and share your analysis results.

**Export formats:**

| Format | Content | Use Case |
|--------|---------|----------|
| CSV | Query results | Data analysis in Excel/Python |
| PNG | Individual charts | Presentations |

**Features:**
- One-click download
- Timestamped filenames
- Preserves formatting

---

## Advanced Features

### Smart Query Understanding

The system understands:
- Table name variations ("customer" vs "customers")
- Column name inference
- Date range queries
- Numeric comparisons
- Text pattern matching
- Aggregate functions
- Sorting and limiting

### Error Handling

Graceful error management:
- Invalid queries are caught
- Helpful error messages
- Suggestions for correction
- No system crashes

### Performance Optimization

- Efficient SQL generation
- Query result caching
- Lazy loading for large datasets
- Optimized chart rendering

### Security

- SQL injection prevention
- Read-only database access
- Local data processing
- Secure API key handling

---

## Use Cases

### Business Analysis
- Sales performance tracking
- Customer segmentation
- Revenue analysis
- Product performance

### Data Exploration
- Quick data insights
- Pattern discovery
- Anomaly detection
- Statistical analysis

### Reporting
- Monthly/quarterly reports
- Executive summaries
- Department-specific reports
- Custom analysis reports

### Education & Learning
- SQL learning tool
- Data analysis practice
- Visualization techniques
- Database concepts

---

## Coming Soon (Potential Enhancements)

- [ ] Multi-database support (PostgreSQL, MySQL)
- [ ] Real-time data refresh
- [ ] Scheduled reports
- [ ] Email report delivery
- [ ] Advanced filters and parameters
- [ ] Custom chart styling
- [ ] Dashboard creation
- [ ] User authentication
- [ ] Query history search
- [ ] Natural language insights

---

## Technical Specifications

**Frontend:** Streamlit 1.31.0
**Database:** SQLite (local)
**ORM:** SQLAlchemy 2.0
**LLM Framework:** LangChain 0.1.6
**Visualization:** Plotly 5.18.0
**Reports:** ReportLab 4.0.9
**Data Processing:** Pandas 2.2.0

**LLM Support:**
- OpenRouter API gateway
- Any OpenRouter-supported model
- Configurable model selection
- Temperature and parameter control

---

For detailed usage instructions, see README.md
For quick start, see QUICKSTART.md

