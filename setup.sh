#!/bin/bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers and system-level dependencies
# The --with-deps flag is critical for Linux servers to install missing libraries
python -m playwright install --with-deps chromium

# 3. Run Crawl4AI setup
crawl4ai-setup