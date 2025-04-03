"""
Created on Thu Apr  3 08:42:03 2025

Another attempt to get all the BP podcast episodes to load
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                      NoSuchElementException,
                                      StaleElementReferenceException)
from webdriver_manager.chrome import ChromeDriverManager
import time

def safe_click_load_more(driver, attempts=3):
    """Attempt to click using multiple strategies with retries"""
    for _ in range(attempts):
        try:
            # Strategy 1: Wait for button to be clickable
            button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Load more episodes')]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", button)
            return True
        except (NoSuchElementException, TimeoutException):
            # Strategy 2: Alternative CSS selector
            try:
                button = driver.find_element(By.CSS_SELECTOR, "button.load-more-button")
                driver.execute_script("arguments[0].click();", button)
                return True
            except NoSuchElementException:
                pass
        except StaleElementReferenceException:
            time.sleep(2)
            continue
    return False

def load_bible_project_episodes():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Bypass automation detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://bibleproject.com/podcasts/the-bible-project-podcast/")
        print("Page loading started...")
        
        # Initial page load wait
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Cookie consent handling (if present)
        try:
            cookie_accept = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "cookie-accept"))
            )
            cookie_accept.click()
            print("Cookie consent accepted")
        except TimeoutException:
            pass
        
        clicks_achieved = 0
        max_clicks = 46
        failed_attempts = 0
        
        while clicks_achieved < max_clicks and failed_attempts < 3:
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500)")
            time.sleep(1.5)
            
            if safe_click_load_more(driver):
                clicks_achieved += 1
                failed_attempts = 0
                print(f"Successful click {clicks_achieved}/{max_clicks}")
                
                # Dynamic wait for content load
                WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, "div.loading-indicator")
                    )
                )
                time.sleep(2)  # Buffer time
            else:
                failed_attempts += 1
                print(f"Button not found attempt {failed_attempts}/3")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)
                
            # Periodic scroll updates
            if clicks_achieved % 5 == 0:
                driver.execute_script("window.scrollBy(0, -300)")
                time.sleep(0.5)
        
        print(f"Completed {clicks_achieved} clicks")
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        print("Screenshot saved to error_screenshot.png")
    finally:
        driver.quit()
        print("Browser closed")

load_bible_project_episodes()
