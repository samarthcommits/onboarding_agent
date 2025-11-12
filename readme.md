# 🤖 Onboarding Agent

The **Onboarding Agent** is an AI-powered assistant that automatically learns about a company's website and interacts with users to provide onboarding, guidance, and follow-ups — all powered by LangChain, Gemini, and NeMo Guardrails.

This project combines **automated web scraping**, **retrieval-augmented conversations**, and **multi-tool agent orchestration** into one pipeline.

---

## 🚀 Features

- 🌐 **Domain-Based Onboarding**  
  Users can input their company’s website URL, which is automatically scraped for information.

- 🧠 **Intelligent Agent with Tools**  
  The agent can:
  - Retrieve insights from scraped website data (`ret_tool`)
  - Send follow-up emails (`e_tool`)
  - Redirect or open company pages dynamically using Selenium (`b_tool`)

- 🦾 **LLM + Guardrails Integration**  
  Uses **LangChain agents** with **Gemini 2.0 Flash** or **Ollama Gemma** for reasoning, combined with **NeMo Guardrails** for safe and policy-aligned responses.

- ⚙️ **FastAPI Backend + Simple Frontend**  
  Includes a lightweight REST API backend and a minimal HTML interface for chat interaction.


## 🧩 Project Structure

```bash
project/
│
├── src/
│   ├── test_bot2.py              # Defines the onboarding agent and tools
│   ├── scraper.py                # Web scraper that collects data from a given domain
│   ├── tools/
│   │   ├── ret_tool.py           # Retrieves data from scraped info
│   │   ├── e_tool.py             # Handles email-related automation
│   │   └── b_tool.py             # Redirects or opens relevant URLs
│
├── main.py                       # FastAPI backend for scrape and chat endpoints
├── index.html                    # Simple frontend UI for domain input and chat
├── README.md                     # Project documentation
```

---

## ⚙️ Setup Instructions

### 1️⃣ Prerequisites
- Python 3.9+
- Node not required — simple HTML frontend
- Chrome browser installed (for Selenium)
- ChromeDriver managed via `webdriver_manager`

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

🧠 Environment Variables

- Create a .env file (or export directly in your shell) with:
```bash
GEMINI_API_KEY = ''
OLLAMA_API_ADDRESS = ''
COHERE_API_KEY = ''
DOMAIN_EMAIL = 'address_the_agent_will_use_to_send_emails_from'
DOMAIN_PASSWORD = "password_to_the_email"
```

## 🚦 How to Run

### 1️⃣ Start the Backend

```bash
uvicorn main:app --reload
```

This launches the FastAPI server at http://localhost:8000

2️⃣ Open the Frontend

- Simply open the index.html file in your browser.

3️⃣ Start Using

- Enter your company’s domain (e.g., pal.tech)

- Click “Start Onboarding” — scraping begins in the background

- Once scraping finishes, start chatting with the agent!

### The agent will:

- 🧠 Extract details from the scraped site using ret_tool

- 🌐 Redirect or open relevant pages using b_tool

- 📧 Send follow-up emails with e_tool

