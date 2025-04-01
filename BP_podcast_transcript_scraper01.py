"""
Allen Jones
2025.04.01

This script loads all podcast episodes from bibleproject.com, clicks into each
episode, and, if there is a transcript button, clicks into the transcript and
downloads the PDF.
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests

# Set up headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def scroll_and_load_all_episodes():
    """ Clicks 'Load More Episodes' button until all episodes are visible."""
    driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")
    time.sleep(5)
    
    while True:
        try:
            load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load More Episodes')]")
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(6)  # Small delay to allow content to load
            print("done")
        except:
            break  # No more episodes to load

def download_transcript(pdf_url, episode_title):
    """ Downloads the transcript PDF."""
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = f"transcripts/{episode_title}.pdf"
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {episode_title}")

def scrape_transcripts():
    """ Scrapes all episodes for transcript PDFs."""
    os.makedirs("transcripts", exist_ok=True)
    episodes = driver.find_elements(By.CSS_SELECTOR, "a.episode-card")
    
    for episode in episodes:
        episode_title = episode.text.split('\n')[0]
        episode_url = episode.get_attribute("href")
        driver.get(episode_url)
        time.sleep(6)
        
        try:
            transcript_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Transcript')]")
            print(transcript_button)
            pdf_url = transcript_button.get_attribute("href")
            download_transcript(pdf_url, episode_title)
        except:
            print(f"No transcript found for: {episode_title}")
        
        driver.back()
        time.sleep(6)

# Run the scraping process
scroll_and_load_all_episodes()
scrape_transcripts()
driver.quit()

