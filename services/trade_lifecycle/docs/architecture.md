# Project Architecture

This document describes the high-level architecture of the Lifecycle Backend project.

## Structure
- **api/**: FastAPI route definitions
- **core/**: Business logic modules
- **services/**: Orchestration and runners
- **utils/**: Utility functions and helpers
- **db/**: Data storage and repositories
- **frontend/templates/**: Jinja2 HTML templates
- **docs/**: Project documentation

## Overview
The backend is organized for clarity, maintainability, and separation of concerns. Each module has a clear responsibility. 

lifecycle_backend/
├── app.py
├── main.py
├── requirements.txt
├── api/
│   ├── __init__.py
│   └── routes.py
├── core/
│   ├── __init__.py
│   ├── coupon_logic.py
│   ├── early_redemption_logic.py
│   └── maturity_logic.py
├── db/
│   ├── trade_repository.py
│   ├── coupon_approvals.json
│   ├── coupon_payments.json
│   ├── maturity_approvals.json
│   ├── redeemed_status.json
│   ├── redeemed_trades.json
│   ├── raw/
│   │   └── trades.csv
│   └── output/
│       ├── Maturity.csv
│       ├── Coupon_Rate.csv
│       ├── Barrier-Monitoring.csv
│       ├── Early-Redemption.csv
│       ├── early_redemption_download_*.csv
│       ├── coupon_download_*.csv
│       └── maturity_download_*.csv
├── frontend/
│   └── templates/
│       ├── event_page.html
│       └── overview.html
├── services/
│   ├── __init__.py
│   └── lifecycle_runner.py
└── utils/
    ├── __init__.py
    └── datetime_utils.py
