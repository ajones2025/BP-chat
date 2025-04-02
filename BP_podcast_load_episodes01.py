"""
Spyder Editor

Script to open BibleProject podcast page and click the "Load more episodes"
button until all episodes are displayed.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

def load_bible_project_episodes():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start with browser maximized
    #chrome_options.add_argument("--disable-notifications")  # Disable notifications
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the Bible Project podcast page
        url = "https://bibleproject.com/podcasts/the-bible-project-podcast/"
        print(f"Navigating to {url}")
        driver.get(url)
        
        # Give page time to fully load initially
        time.sleep(5)
        
        # Click "Load more episodes" 46 times
        clicks_completed = 0
        max_attempts = 46
        
        print(f"Attempting to click 'Load more episodes' button {max_attempts} times...")
        
        for i in range(max_attempts):
            try:
                # Scroll to bottom of page to ensure button is visible
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for scroll to complete
                
                # Wait for button to be clickable
                load_more_button = WebDriverWait(driver, 10).until(                    
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more-button"))
                )
                
                # Click the button
                load_more_button.click()
                clicks_completed += 1
                
                print(f"Successfully clicked 'Load more episodes' button ({clicks_completed}/{max_attempts})")
                
                # Wait for new content to load
                time.sleep(5)  # Adjust this delay as needed
                
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Could not find or click the button: {str(e)}")
                print("This might happen if all episodes are already loaded or if the button has a different structure.")
                break
                
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                break
        
        print(f"Completed {clicks_completed} out of {max_attempts} requested clicks.")
        
        # Keep browser open for review (optional)
        input("Press Enter to close the browser...")
        
    finally:
        # Close the browser
        driver.quit()
        print("Browser closed.")

load_bible_project_episodes()



# Alternative selectors if the default one doesn't work
# load_more_button = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'load-more')]"))
# )
# OR
# load_more_button = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more-button"))
# )
