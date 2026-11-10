"""Take README screenshots of a running instance: python scripts/shots.py http://localhost:8000"""
import asyncio, sys
from playwright.async_api import async_playwright

async def main(base):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 430, "height": 900}, device_scale_factor=2)
        await pg.goto(base); await pg.wait_for_timeout(800)
        await pg.fill("#p_edu", "BCA"); await pg.fill("#p_age", "21"); await pg.fill("#p_int", "python, web")
        await pg.click("text=Find free internships for me"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path="docs/screenshots/chat.png")
        await pg.click("nav button[data-tab=resume]"); await pg.click("#sample"); await pg.click("#check"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path="docs/screenshots/resume.png", full_page=True)
        await pg.select_option("#lang", "kn"); await pg.wait_for_timeout(500)
        await pg.click("nav button[data-tab=opps]"); await pg.click("#find"); await pg.wait_for_timeout(1000)
        await pg.screenshot(path="docs/screenshots/opportunities-kannada.png")
        await pg.select_option("#lang", "hi"); await pg.wait_for_timeout(500)
        await pg.click("nav button[data-tab=interview]"); await pg.wait_for_timeout(500)
        await pg.fill("#ans", "I built a library website for my college with HTML and CSS. I made the pages and fixed bugs.")
        await pg.click("#submit_ans"); await pg.wait_for_timeout(1000)
        await pg.screenshot(path="docs/screenshots/interview-hindi.png")
        await b.close()

asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"))
