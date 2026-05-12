"""
Nxlebot Universal Scraper Agent
Handle Static, Dynamic (SPA), Infinite Scroll, & Interaction
"""

import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path

OUTPUT_DIR = Path("scraped_data")
OUTPUT_DIR.mkdir(exist_ok=True)

class UniversalScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        self.page = await self.context.new_page()
        # Anti-detection script
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

    async def scrape(self, url, wait_for_selector=None, scroll=False, clicks=[]):
        """
        url: Target URL
        wait_for_selector: Wait for specific element to load (for SPA)
        scroll: True if need to scroll to bottom (infinite scroll)
        clicks: List of selectors to click before scraping
        """
        print(f"🕷️  Scraping: {url}")
        await self.page.goto(url, wait_until="networkidle")
        
        # Handle clicks (interactions)
        for selector in clicks:
            try:
                await self.page.click(selector)
                await self.page.wait_for_timeout(1000)
            except:
                print(f"⚠️  Click failed: {selector}")

        # Wait for dynamic content
        if wait_for_selector:
            try:
                await self.page.wait_for_selector(wait_for_selector, timeout=10000)
            except:
                print(f"⚠️  Selector not found: {wait_for_selector}")

        # Handle infinite scroll
        if scroll:
            await self.auto_scroll()

        # Extract Data
        data = await self.extract_content()
        
        # Save
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_")
        output_file = OUTPUT_DIR / f"{filename}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved to {output_file}")
        return data

    async def auto_scroll(self, steps=5, delay=1000):
        """Scroll down to load more content"""
        for _ in range(steps):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(delay)

    async def extract_content(self):
        """Extract main content, headings, links, and images"""
        content = await self.page.evaluate("""() => {
            return {
                title: document.title,
                h1: Array.from(document.querySelectorAll('h1')).map(e => e.innerText),
                h2: Array.from(document.querySelectorAll('h2')).map(e => e.innerText),
                h3: Array.from(document.querySelectorAll('h3')).map(e => e.innerText),
                p: Array.from(document.querySelectorAll('p')).map(e => e.innerText).filter(t => t.length > 20),
                links: Array.from(document.querySelectorAll('a')).map(e => ({ text: e.innerText, href: e.href })),
                images: Array.from(document.querySelectorAll('img')).map(e => e.src)
            }
        }""")
        return content

    async def close(self):
        if self.browser:
            await self.browser.close()

async def main():
    scraper = UniversalScraper(headless=False) # Set True kalau mau silent
    await scraper.start()
    
    # Example: Scrape AI Black Magic (Dynamic Site)
    # await scraper.scrape(
    #     url="https://aiblackmagic.com/", 
    #     wait_for_selector=".prompt-card", # Contoh selector
    #     scroll=True
    # )

    print("🚀 Scraper Ready. Edit 'main()' to start scraping.")
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
