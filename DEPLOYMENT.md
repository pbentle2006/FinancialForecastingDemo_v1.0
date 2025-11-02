# 🚀 Financial Forecasting Platform - Deployment Guide

## 📋 Overview
This is a comprehensive Streamlit-based financial forecasting platform with advanced analytics, machine learning models, and dual perspective forecasting (Finance vs Sales).

## 🎯 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended)
1. **Upload to GitHub**: Create a GitHub repository and upload this folder
2. **Deploy on Streamlit Cloud**: 
   - Go to https://share.streamlit.io/
   - Connect your GitHub repository
   - Select `app_tabbed.py` as the main file
   - Deploy automatically

### Option 2: Heroku
1. **Install Heroku CLI**
2. **Create Heroku App**:
   ```bash
   heroku create your-forecasting-app
   ```
3. **Deploy**:
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   heroku git:remote -a your-forecasting-app
   git push heroku main
   ```

### Option 3: Railway
1. **Connect GitHub repository** to Railway
2. **Select Python template**
3. **Railway will auto-detect** the Streamlit app
4. **Deploy automatically**

### Option 4: Render
1. **Create new Web Service** on Render
2. **Connect GitHub repository**
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `streamlit run app_tabbed.py --server.port=$PORT --server.address=0.0.0.0`

## ⚠️ Important Notes for Netlify

**Netlify is NOT suitable for this Streamlit application** because:
- Netlify only supports static sites (HTML, CSS, JavaScript)
- Streamlit requires a Python server environment
- This app needs server-side processing for data analysis and ML models

## 📁 Files Included

### Core Application Files:
- `app_tabbed.py` - Main application entry point
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment configuration
- `runtime.txt` - Python version specification

### Feature Modules:
- `advanced_analytics.py` - ML models and trend analysis
- `advanced_analytics_tab.py` - Advanced analytics UI
- `master_assumptions.py` - Risk factors and dual forecasting
- `master_assumptions_tab.py` - Master assumptions UI
- `advanced_query_engine.py` - Data filtering and querying
- `validation_engine.py` - Data validation rules

### Configuration:
- `netlify.toml` - Netlify configuration (not applicable for this app)
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation

## 🔧 Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   streamlit run app_tabbed.py
   ```

3. **Access Application**:
   - Open browser to `http://localhost:8501`

## 🎯 Application Features

### 🔍 Data Integrity Tab
- CSV file upload and processing
- Data validation and quality checks
- Column mapping and data transformation

### 📊 Forecast Dashboard Tab
- Interactive revenue forecasting
- Business dimension filtering
- Trend analysis and visualizations

### 🤖 Advanced Analytics Tab
- Machine learning forecast models (Linear Regression, Random Forest, Seasonal Decomposition)
- Trend analysis and seasonality detection
- Portfolio concentration analysis
- AI-generated business insights

### ⚙️ Master Assumptions Tab
- Risk factor configuration and management
- Advanced data querying and filtering
- Finance vs Sales dual perspective forecasting
- Reconciliation dashboard with variance analysis

### 💾 Export & Reports Tab
- Excel export functionality
- Data download capabilities
- Report generation

## 📊 Sample Data Format

The application expects CSV files with columns:
- `project_id` - Unique project identifier
- `year` - Year (e.g., 2024)
- `month` - Month (1-12)
- `revenue` - Revenue amount
- `client` - Client name
- `offering` - Service offering
- `industry` - Industry sector
- `sales_org` - Sales organization
- `product_name` - Product name

## 🚀 Recommended Deployment: Streamlit Community Cloud

For the easiest deployment:
1. Create a GitHub repository
2. Upload all files from this folder
3. Go to https://share.streamlit.io/
4. Connect your GitHub repo
5. Deploy with `app_tabbed.py` as the main file

## 🔒 Environment Variables (Optional)

If using external APIs or databases, set these environment variables:
- `OPENAI_API_KEY` - For AI-powered insights (optional)
- `DATABASE_URL` - For database connections (optional)

## 📞 Support

For deployment issues or questions, refer to:
- Streamlit Documentation: https://docs.streamlit.io/
- Streamlit Community: https://discuss.streamlit.io/
