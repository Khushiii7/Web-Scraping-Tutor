# Web Scraping Tutor

A simple and reliable Python project that collects issue data from **Apache’s public Jira instance** (like HDFS, SPARK, HADOOP) and converts it into a **clean JSONL format** — ready for use in **Large Language Model (LLM)** training.

---

## Overview

This project builds a **data scraping and transformation pipeline** that:

* Fetches issues and comments from Apache Jira
* Handles errors, timeouts, and network problems smoothly
* Automatically **resumes from where it stopped** if interrupted
* Converts raw data into **structured, machine-readable JSONL format**

It’s designed to be **efficient, fault-tolerant**, and easy to extend.

---

## Features

* **Error Handling:** Retries on network or server issues
* **Auto Resume:** Saves progress with checkpoints
* **Rate Limit Handling:** Waits automatically when hitting limits
* **Clean Data Output:** Converts to structured JSONL for ML use
* **Lightweight:** Uses Jira’s REST API (no HTML scraping)

---

## ⚙️ Setup Instructions

### Requirements
* Python **3.7 or higher**
* pip (Python package manager)

### Installation Steps

1.  **Clone this repository**
    ```bash
    git clone [https://github.com/Khushiii7/Web-Scraping-Tutor.git](https://github.com/Khushiii7/Web-Scraping-Tutor.git)
    cd Web-Scraping-Tutor
    ```

2.  **(Recommended) Create and activate a virtual environment**
    ```bash
    # Create the venv
    python -m venv venv
    
    # Activate it (Windows Git Bash / macOS / Linux)
    source venv/bin/activate
    # (or on Windows CMD: .\venv\Scripts\activate)
    ```

3.  **Install the required packages**
    This command reads the `requirements.txt` file and installs all the necessary libraries.
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 How to Run

To run the scraper and fetch data for all projects, run the following command from the project's root directory:

```bash
python -m scraper.run all