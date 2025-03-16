# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 07:50:11 2025

@author: AJones
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import fitz  # PyMuPDF for PDF text extraction
import json
import os

# Initialize Selenium WebDriver (ensure you have the correct driver installed)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode

# Step 1: Load all episodes dynamically
driver = webdriver.Chrome(options=options)
driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")

def load_all_episodes():
    while True:
        try:
            load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load More Episodes')]")
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(2)  # Wait for content to load
        except:
            break  # No more episodes to load

load_all_episodes()

# Step 2: Extract episode links
episode_links = []
elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/podcasts/')]" )
for elem in elements:
    link = elem.get_attribute("href")
    if link and link not in episode_links:
        episode_links.append(link)

driver.quit()

# Step 3: Download and extract PDF transcripts
def download_and_extract_text(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        pdf_path = "temp_transcript.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        
        # Extract text from PDF
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        os.remove(pdf_path)  # Clean up temp file
        return text
    return ""

transcripts = []

for episode_url in episode_links:
    driver = webdriver.Chrome(options=options)
    driver.get(episode_url)
    time.sleep(2)
    
    try:
        transcript_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Transcript')]")
        pdf_url = transcript_button.get_attribute("href")
        if pdf_url:
            text = download_and_extract_text(pdf_url)
            
            # Process transcript text into structured format
            structured_transcript = []
            for line in text.split("\n"):
                if line.startswith("Tim:"):
                    structured_transcript.append({"speaker": "Tim", "text": line.replace("Tim:", "").strip()})
                elif line.startswith("Jon:"):
                    structured_transcript.append({"speaker": "Jon", "text": line.replace("Jon:", "").strip()})
            
            transcripts.append({
                "episode_url": episode_url,
                "transcript": structured_transcript
            })
    except:
        pass  # Skip if no transcript found
    
    driver.quit()

# Step 4: Save structured transcripts to JSON
with open("bibleproject_transcripts.json", "w", encoding="utf-8") as f:
    json.dump(transcripts, f, ensure_ascii=False, indent=4)
