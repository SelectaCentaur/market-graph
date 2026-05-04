import re
from playwright.sync_api import Page, expect

# We'll use the absolute file path to load the local html file
HTML_PATH = "file:///Users/claw/.openclaw/workspace/robotics_graph/index.html"

def test_dashboard_loads(page: Page):
    page.goto(HTML_PATH)
    
    # Check that the main title exists
    expect(page).to_have_title(re.compile("Physical AI & Humanoid Robotics Market Graph"))
    
    # Check left panel is visible
    expect(page.locator("#left-panel")).to_be_visible()
    
    # Check right panel is visible
    expect(page.locator("#right-panel")).to_be_visible()

    # Ensure graph container is present
    expect(page.locator("#graph-container")).to_be_visible()

    def test_timeframe_buttons(page: Page):
        page.goto(HTML_PATH)
    
        # Default should be "Today's News"
        expect(page.locator("#news-feed-title")).to_have_text("Today's News")
    
        # Wait for button to be interactive
        page.locator("#btn-time-week").wait_for(state="visible")
        
        # Click "Week" button and verify title change (force click in case of overlapping z-index)
        page.locator("#btn-time-week").click(force=True)
        expect(page.locator("#news-feed-title")).to_have_text("Top News (This Week)")
    
        # Click "Month" button and verify title change
        page.locator("#btn-time-month").click(force=True)
        expect(page.locator("#news-feed-title")).to_have_text("Top News (This Month)")
    
        # Click "Summary" button and verify title change
        page.locator("#btn-time-summary").click(force=True)
        expect(page.locator("#news-feed-title")).to_have_text("Daily Summary")

def test_legend_toggle(page: Page):
    page.goto(HTML_PATH)
    
    # Wait for the first legend item to be populated by JS
    legend_item = page.locator(".legend-item").first
    legend_item.wait_for(state="visible")
    
    # Click to toggle off
    legend_item.click()
    # Should get the hidden-type class
    expect(legend_item).to_have_class(re.compile("hidden-type"))
    
    # Click to toggle back on
    legend_item.click()
    # Should no longer have the hidden-type class
    expect(legend_item).not_to_have_class(re.compile("hidden-type"))

def test_mode_buttons(page: Page):
    page.goto(HTML_PATH)
    
    # Check default "all" mode is active
    expect(page.locator("#btn-mode-all")).to_have_class(re.compile("active"))
    expect(page.locator("#btn-mode-deployment")).not_to_have_class(re.compile("active"))
    
    # Click "deployment" mode
    page.locator("#btn-mode-deployment").click()
    expect(page.locator("#btn-mode-deployment")).to_have_class(re.compile("active"))
    expect(page.locator("#btn-mode-all")).not_to_have_class(re.compile("active"))