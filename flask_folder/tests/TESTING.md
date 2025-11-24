# Testing Guide

## Python Tests

### Setup
```bash
# Install Python dependencies (if not already done)
pip install -r requirements.txt
```

### Run Tests
```bash
# Run all Python tests
pytest

# Run specific test file
pytest flask_folder/tests/test_side_panel.py

# Run with verbose output
pytest -v
```

## JavaScript Tests

### Setup (One-time)
```bash
# Install JavaScript dependencies
npm install
```

### Run Tests
```bash
# Run side-panel tests
node --test flask_folder/tests/side-panel.test.js
```

## What Gets Tested

**Python Tests** (`flask_folder/tests/`)
- Backend routes and API endpoints
- Spotify OAuth integration
- Template rendering
- Static file serving

**JavaScript Tests** (`flask_folder/tests/*.test.js`)
- Side-panel functionality (open/close)
- DOM manipulation
- Event handlers (clicks, escape key)
