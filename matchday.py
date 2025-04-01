from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import random
import re

def random_delay(min_time=3, max_time=7):
    time.sleep(random.uniform(min_time, max_time))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

url = "https://www.google.com/search?client=firefox-b-d&q=ipl"

def match():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={"width": 1280, "height": 720})
        page = context.new_page()

        # 🛡️ Enable Stealth Mode
        stealth_sync(page)

        # Navigate to Google IPL schedule
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        random_delay(1, 4)

        # 🎯 Extract short forms of teams (GT, MI, etc.)
        team_elements = page.query_selector_all('span[aria-hidden="true"]')
        teams = [team.inner_text().strip() for team in team_elements if team.inner_text().strip()]
        
        # 🎯 Extract match info with T20 match number
        match_info_element = page.query_selector('div.imso_mh__lg-st-srs span[aria-hidden="true"]')
        match_info = match_info_element.inner_text().strip() if match_info_element else "Match info not found"

        # Extract match number after "T20" and before "of"
        match_number = None
        match_number_match = re.search(r'T20\s(\d+)\s+of', match_info)
        if match_number_match:
            match_number = match_number_match.group(1)

        # 🎉 Display results
        if len(teams) >= 2 and match_number:
            return teams[0], teams[1], match_number
        
        # If no teams or match number found, return None
        return None

        # Close browser
        browser.close()

# Call the function
result = match()
if result:
    print(f"Teams: {result[0]} vs {result[1]}, Match Number: {result[2]}")
else:
    print("No match information found.")
