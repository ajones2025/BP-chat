# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 14:24:42 2025

@author: Allen Jones
"""

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
import re


# Set up Chrome options (headless or visible)
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280x720")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def sanitize_filename(title):
    """Clean episode titles for safe filenames"""
    return re.sub(r'[<>:"/\\|?*]', '', title)[:150]  # Trim long titles

def scroll_and_load_all_episodes(driver):
    """Fixed loading with case-insensitive search and scrolling"""
    driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")
    time.sleep(5)
    loaded_count = 0
    
    while True:
        # Find button using case-insensitive XPath
        buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more episodes')]")
        
        if not buttons:
            print("No more 'Load More' buttons found")
            break
            
        button = buttons[0]
        
        # Scroll to button using JavaScript
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
        
        # Wait for button to be clickable
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more episodes')]"))
        )
        
        # Click using JavaScript to bypass visibility issues
        driver.execute_script("arguments[0].click();", button)
        
        # Wait for new content to load
        time.sleep(2)  # Initial pause for DOM update
        try:
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "a.episode-card")) > loaded_count
            )
            loaded_count = len(driver.find_elements(By.CSS_SELECTOR, "a.episode-card"))
            print(f"Loaded {loaded_count} episodes so far")
        except TimeoutException:
            print("No new episodes loaded - stopping")
            break

"""
def scroll_and_load_all_episodes(driver):
    Clicks 'Load More Episodes' until all episodes are visible
    driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")
    time.sleep(5)
    
    while True:
        try:
            # Wait for the "Load More Episodes" button to appear and be clickable
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More Episodes')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_button)
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(3)  # Allow new episodes to load
        except Exception as e:
            print("No more 'Load More Episodes' buttons found or error:", str(e))
            break
"""

def download_transcript(pdf_url, episode_title):
    """Downloads the transcript PDF."""
    response = requests.get(pdf_url)
    if response.status_code == 200:
        filename = os.path.join("transcripts", f"{episode_title}.pdf")
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download transcript for {episode_title}")

def scrape_transcripts(driver):
    """Scrapes all episodes for transcript PDFs."""
    os.makedirs("transcripts", exist_ok=True)
    
    # Get all episode links after loading all episodes
    episodes = driver.find_elements(By.CSS_SELECTOR, "a.episode-card")
    
    for episode in episodes:
        episode_title = episode.text.split('\n')[0].strip()
        episode_url = episode.get_attribute("href")
        
        # Navigate to the episode page
        driver.get(episode_url)
        time.sleep(5)  # Allow page to fully load
        
        try:
            # Wait for and find the transcript button
            transcript_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Transcript')]"))
            )
            pdf_url = transcript_button.get_attribute("href")
            download_transcript(pdf_url, episode_title)
        except Exception as e:
            print(f"No transcript found for {episode_title} or error:", str(e))
        
        # Return to the main podcast page (re-fetch elements if necessary)
        driver.back()
        time.sleep(3)

# Run the scraping process
try:
    scroll_and_load_all_episodes(driver)
    scrape_transcripts(driver)
finally:
    driver.quit()
