"""
Allen Jones
2025.04.01

This script loads all podcast episodes from bibleproject.com, clicks into each
episode, and, if there is a transcript button, clicks into the transcript and
downloads the PDF.
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

# Configure with explicit waits and better options
chrome_options = Options()
# chrome_options.add_argument("--headless=new")  # Modern headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280x720")
chrome_options.add_argument("--log-level=3")  # Suppress console logs

def sanitize_filename(title):
    """Clean episode titles for safe filenames"""
    return re.sub(r'[<>:"/\\|?*]', '', title)[:150]  # Trim long titles


def scroll_and_load_all_episodes(driver):
    """Fixed loading with case-insensitive search and scrolling"""
    driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")
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
    Improved loading with explicit waits
    driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")
    
    while True:
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Load More Episodes')]"))
            ).click()
            time.sleep(3)  # Reduced wait time
        except Exception as e:
            print("Finished loading episodes")
            break
"""

def download_transcript(driver, pdf_url, episode_title):
    """Download through Selenium to maintain session cookies"""
    try:
        driver.get(pdf_url)
        time.sleep(2)  # Allow PDF to load
        
        # Get current PDF URL (handles potential redirects)
        final_pdf_url = driver.current_url
        if not final_pdf_url.lower().endswith('.pdf'):
            raise ValueError("Not a PDF file")
            
        response = requests.get(final_pdf_url)
        if response.status_code == 200:
            filename = os.path.join("transcripts", f"{sanitize_filename(episode_title)}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Success: {filename}")
        else:
            print(f"Failed: {episode_title} (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"Download failed for {episode_title}: {str(e)}")

def scrape_transcripts(driver):
    """Main scraping logic with improved element handling"""
    os.makedirs("transcripts", exist_ok=True)
    
    # Get all episode cards once after loading
    episodes = WebDriverWait(driver, 40).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.episode-card"))
    )
    
    for idx in range(len(episodes)):
        # Re-fetch elements to avoid staleness
        episode = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.episode-card"))
        )[idx]
        
        episode_title = episode.text.split('\n')[0].strip()
        episode_url = episode.get_attribute("href")
        
        # Open in new tab to maintain main page state
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(episode_url)
        
        try:
            transcript_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'transcript')]"))
            )
            pdf_url = transcript_link.get_attribute("href")
            download_transcript(driver, pdf_url, episode_title)
            
        except Exception as e:
            print(f"No transcript found for: {episode_title}")
        
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

# Execution flow
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
    scroll_and_load_all_episodes(driver)
    scrape_transcripts(driver)

