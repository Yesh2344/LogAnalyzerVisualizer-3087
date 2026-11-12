# Log Analyzer & Visualizer

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3.2-green.svg)](https://flask.palletsprojects.com/)

## Overview

`Log Analyzer & Visualizer` is a lightweight web application that parses web server logs (Apache/Nginx common format), exposes a JSON API, and visualizes key metrics (requests per hour, status code distribution) in the browser.

Features:

- **Robust log parsing** with error handling.
- **REST API** (`/api/logs`) for filtered log data.
- **Interactive charts** using Chart.js.
- **Configurable via environment variables** (`.env`).
- **Unit tests** with pytest.

## Project Structure