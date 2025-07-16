# AI-Based Secure Code Review Tool

This project is a Python-based tool designed to detect **security vulnerabilities** in source code using **static analysis**. It integrates two powerful security analyzers — **SonarQube** and **Bandit** — to identify OWASP Top 10 issues like injection flaws, insecure deserialization, and insecure APIs in Python applications.

Developed as part of my academic project for **Secure Coding Practices** under the Cybersecurity program at FAST NUCES.

---

## Project Objective

To develop an automated static code analysis system for Python projects that:
- Detects security vulnerabilities
- Flags risky coding practices
- Maps results to OWASP Top 10 categories
- Provides remediation advice or warnings

---

## Tools & Technologies

- **Python**
- **SonarQube** – for deep code analysis, rule enforcement, and dashboard metrics
- **Bandit** – lightweight static analyzer for Python code security
- **OWASP Guidelines** – for vulnerability reference
- **Docker** (optional) – for hosting SonarQube locally
- **VSCode / PyCharm** – for local code editing

---

## How It Works

1. **Bandit** scans Python files and reports:
   - High/medium/low severity issues
   - Insecure function usage (e.g., `eval()`, `exec()`)
   - Hardcoded passwords or API keys
2. **SonarQube** performs in-depth static code analysis with quality gates, custom rules, and a user-friendly dashboard
3. **Reports are combined** to give a comprehensive view of vulnerabilities and code quality issues

---

## Features

- Static code scanning
- OWASP-aware rule mapping
- Consolidated vulnerability reports
- SonarQube dashboard for visual metrics
- Works on multiple `.py` files and full repos
