# README

## Overview

This repository contains a Python-based front-end application built with Dash, Plotly, and Dash Bootstrap Components. It provides a sleek, responsive, and modern interface for visualizing and interacting with stock market data, including real-time trades, analytics, and a multi-panel dashboard layout inspired by advanced trading platforms.

### Key Features

- **Main Dashboard Page** (default route `/`):
  - **Top Navbar**: Links for navigation (Extended hours, Stock Trading, Monitoring, Options Trading) and a "Market Open" status indicator.
  - **Left Panel**: Account details, a small overview chart of account value, and a table of market movers.
  - **Center Panel**: Main candlestick chart with volume bars and user-selectable ticker and time intervals.
  - **Right Panel**: Positions list and recent orders table.
  
- **Real-time Trading Page** (`/realtime`):
  - Displays real-time price charts for selected tickers, updating every 2 seconds.
  - Shows key metrics (current price, total trades in the last 10 seconds).
  
- **Analytics Page** (`/analytics`):
  - Provides multiple charts (average trade volume, most traded tickers, price trend, latest events, and trade distribution by exchange).
  - Allows downloading aggregated analytics data as a CSV file.

### Technology Stack

- **Dash & Plotly**: For building interactive and real-time web applications in Python.
- **Dash Bootstrap Components**: For responsive and modern UI layout.
- **Tailwind CSS**: For additional styling (imported via CDN).
- **SinglestoreDB (s2)**: For database connectivity to fetch real-time and historical trade data.
- **Pandas & NumPy**: For data manipulation, indicator computations, and analytics.

### Project Structure

```
neonExchange/
    frontend_app/
        app.py
        config.py
        db_handler.py
        requirements.txt
        .env
        assets/
            tailwind.css
        components/
            __init__.py
            layout.py
            navbar.py
        pages/
            __init__.py
            main_dashboard.py
            realtime_trading.py
            analytics.py
        tests/
            __init__.py
            test_app.py
```

- `frontend_app/app.py`: The main entry point that initializes the Dash app and handles page routing.
- `frontend_app/config.py`: Loads environment variables and configuration (e.g., `SINGLESTORE_DB_URL`).
- `frontend_app/db_handler.py`: Manages database connections and queries against SingleStoreDB. Also provides sample fallback data.
- `frontend_app/pages/`: Contains separate pages for the application (`main_dashboard.py`, `realtime_trading.py`, `analytics.py`).
- `frontend_app/components/`: Reusable UI components (`layout.py` for the main layout, `navbar.py` for the top navigation bar).
- `frontend_app/assets/`: Contains `tailwind.css` and can hold additional static resources.
- `frontend_app/tests/`: Basic unit tests to ensure database queries and logic run as expected.

### Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd neonExchange
   ```
   
2. **Create the Project Structure**:
   Run the setup script:
   ```bash
   ./fe_setup.sh
   ```
   This will create the required directories and empty files. If you have already populated them with the provided code, you can skip this step.
   
3. **Create and Activate a Virtual Environment** (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r frontend_app/requirements.txt
   ```
   
5. **Set Environment Variables**:
   Ensure you have a `.env` file in `frontend_app` with the following:
   ```env
   SINGLESTORE_DB_URL=<your_singlestore_connection_string>
   ```
   Replace `<your_singlestore_connection_string>` with the actual database URL. Alternatively, set the `SINGLESTORE_DB_URL` environment variable in your shell.

### Running the Application

From the project root directory (`neonExchange`):

```bash
python3 -m frontend_app.app
```

This will start the Dash server at `http://0.0.0.0:8050`. Open your web browser and navigate to:

```
http://localhost:8050
```

You will see the main dashboard page. Use the navbar links (top navbar links may not be fully functional if they don't have associated pages, but `/realtime` and `/analytics` are available):

- `http://localhost:8050/` for the main dashboard.
- `http://localhost:8050/realtime` for the real-time trading page.
- `http://localhost:8050/analytics` for the analytics page.

### Running Tests

To run the unit tests:

```bash
python3 -m unittest discover frontend_app/tests
```

This will execute the tests located in `frontend_app/tests/test_app.py`.

### Customization

- **Styling**:  
  Modify `frontend_app/assets/tailwind.css` or add additional CSS files to adjust the styling.  
  The layout and components can be adjusted in the `pages/` or `components/` directories as needed.

- **Data and Queries**:  
  `db_handler.py` can be updated to run real queries against a SingleStore database or another source. Currently, fallback/sample data is provided if the queries return no results.

- **Additional Pages**:  
  Add new Dash pages in `frontend_app/pages/` and update `app.py` for routing.  
  Use the established structure for consistent look and feel.

### Performance and Deployment

- For production deployment, consider running with a production-ready WSGI server (e.g., `gunicorn`) and enabling caching layers.
- Ensure that the `SINGLESTORE_DB_URL` points to a high-performance SingleStore cluster.
- Optimize query logic in `db_handler.py` for large datasets and ensure proper indexing in the database.