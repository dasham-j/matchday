from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import random
import re

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

def get_match_details():
    url = "https://www.google.com/search?client=firefox-b-d&q=ipl"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = context.new_page()
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")

        team_elements = page.query_selector_all('span[aria-hidden="true"]')
        teams = [team.inner_text().strip() for team in team_elements if team.inner_text().strip()]
        
        match_info_element = page.query_selector('div.imso_mh__lg-st-srs span[aria-hidden="true"]')
        match_info = match_info_element.inner_text().strip() if match_info_element else "Match info not found"

        match_number = None
        match_number_match = re.search(r'T20\s(\d+)\s+of', match_info)
        if match_number_match:
            match_number = match_number_match.group(1)

        browser.close()

        if len(teams) >= 2 and match_number:
            return {"team1": teams[0], "team2": teams[1], "match_number": match_number}
        
    return {"error": "Match details not found"}

@app.route('/match-details', methods=['GET'])
def match_details():
    return jsonify(get_match_details())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
