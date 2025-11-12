import os
import asyncio
import json
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.scraper import FullPageScraper
from src.test_bot2 import agent_executor, process_input

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memory storage for scraped data per domain
SCRAPED_DATA = {}

class URLBody(BaseModel):
    domain: str

class MessageBody(BaseModel):
    domain: str
    message: str

def run_scraper(domain: str):
    """Run the scraper in the background."""
    print(f"🕷️ Starting scrape for {domain}...")
    scraper = FullPageScraper(f"https://{domain}")
    scraper.start()
    scraper.close()
    print(f"✅ Finished scraping {domain}")

@app.post("/scrape")
async def scrape_website(data: URLBody, background_tasks: BackgroundTasks):
    """Endpoint to start scraping a domain."""
    domain = data.domain.strip().replace("https://", "").replace("http://", "")
    background_tasks.add_task(run_scraper, domain)
    return {"message": f"Scraping for {domain} has started in the background."}

@app.post("/get_response")
async def get_response(data: MessageBody):
    """Chat endpoint where agent uses scraped data via tools."""
    domain = data.domain.strip()
    user_message = data.message

    # Load scraped data if available
    scraped_file = "scraped_data_from_pal.json"
    if os.path.exists(scraped_file):
        with open(scraped_file, "r", encoding="utf-8") as f:
            SCRAPED_DATA[domain] = json.load(f)

    # Inject scraped data into ret_tool context (if needed)
    # This assumes ret_tool internally knows where to look for scraped JSON
    print(f"🤖 Processing message for {domain}: {user_message}")

    try:
        response = await process_input(user_message)
    except Exception as e:
        print("Error:", e)
        response = "⚙️ Setting things up for you... please try again shortly."

    return {"response": response}
