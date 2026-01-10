# Quick Start Guide

Get your NLP to SQL Chat Application running in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up API Key

Edit the `.env` file and add your OpenRouter API key:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

Get your API key from: https://openrouter.ai/

## 3. Verify Data Files

Check that your data files are in the correct location:

```bash
ls -la data/excel_files/
```

You should see CSV files like customers.csv, orders.csv, etc.

## 4. Run the Application

```bash
streamlit run app.py / python -m streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 5. Try Sample Questions

Click on any sample question in the sidebar, or try these:

### Basic Questions
```
How many customers do we have?
Show me the top 5 products by price
What is the total revenue?
```

### Chart Questions
```
Show me a bar chart of products by price
Create a pie chart of customers by country
```

### Report Questions
```
Generate a detailed sales report
Create a customer analysis report with charts
```

## Common Issues

### Issue: "Error code: 401 - No cookie auth credentials found" ⚠️
**This is the most common error!**

**Cause**: Invalid or missing OpenRouter API key

**Solution**:
1. Go to https://openrouter.ai/keys
2. Sign up/login and create an API key
3. Copy your API key (starts with `sk-or-v1-`)
4. Update `.env` file:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
   ```
5. Restart: `streamlit run app.py`

### Issue: "Invalid OpenRouter API key"
**Solution**: Your `.env` still has the placeholder. Replace `your_openrouter_api_key_here` with your real key from https://openrouter.ai/keys

### Issue: "No data files found"
**Solution**: Place your CSV/Excel files in `data/excel_files/` directory

### Issue: Module not found errors
**Solution**: Make sure you installed all dependencies:
```bash
pip install -r requirements.txt
```

## Next Steps

- Explore the sidebar to see all available tables
- Try different types of questions (see sample categories)
- Generate reports and download them as PDFs
- Export query results as CSV files

## Getting Help

- Check the full README.md for detailed documentation
- Review sample_questions.py for more question examples
- Check the Streamlit logs in the terminal for error messages

---

Enjoy chatting with your data! 🎉
