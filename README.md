#  Web Scraping Tutor

A simple and reliable Python project that collects issue data from **Apache’s public Jira instance** (like HDFS, SPARK, HADOOP) and converts it into a **clean JSONL format** — ready for use in **Large Language Model (LLM)** training.

---

##  Overview

This project builds a **data scraping and transformation pipeline** that:

- Fetches issues and comments from Apache Jira  
- Handles errors, timeouts, and network problems smoothly  
- Automatically **resumes from where it stopped** if interrupted  
- Converts raw data into **structured, machine-readable JSONL format**

It’s designed to be **efficient, fault-tolerant**, and easy to extend.

---

##  Features

-  **Error Handling:** Retries on network or server issues  
- **Auto Resume:** Saves progress with checkpoints  
-  **Rate Limit Handling:** Waits automatically when hitting limits  
-  **Clean Data Output:** Converts to structured JSONL for ML use  
-  **Lightweight:** Uses Jira’s REST API (no HTML scraping)  

---

## Architecture Overview

###  Components

1. **HTTP Client (`safe_get`)** — Handles API calls with retries and delays  
2. **Checkpoint System** — Remembers where the scraper last stopped  
3. **Data Extractor** — Pulls text from Jira’s nested JSON structures  
4. **Transformer** — Cleans and structures data for JSONL export  

### Design Choices

- Uses **Jira REST API** → cleaner and faster than HTML scraping  
- **Project-wise checkpoints** → avoid duplicates and data loss  
- **Streaming writes** → saves data continuously  
- **Session reuse** → improves speed with connection pooling  

---

##  Setup Instructions

###  Requirements
- Python **3.7 or higher**
- pip (Python package manager)

### Installation Steps

1. **Clone or download this repository**
   ```bash
   git clone <your_repo_url>
   cd <your_repo_name>
