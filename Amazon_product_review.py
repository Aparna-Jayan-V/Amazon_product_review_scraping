import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False)
    page = await browser.new_page()

    await page.goto("https://www.amazon.in/boAt-Airdopes-191G-Wireless-Appealing/product-reviews/B09X76VL5L/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")

    reviews =[]
    
    while True:
    
        # Wait for the reviews to be loaded
        await page.wait_for_selector("[data-hook='review']")

        # Get the reviews
        review_elements = await page.query_selector_all("[data-hook='review']")
        for review_element in review_elements:
            review_title = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-title\"]').innerText", review_element)
            review_body = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-body\"]').innerText", review_element)
            product_colour = await page.evaluate("(element) => element.querySelector('[data-hook=\"format-strip\"]').innerText", review_element)
            reviews.append((product_colour,review_title,review_body))

        # Find the next page button
        next_page_button = await page.query_selector("[class='a-last']")
        if not next_page_button:
            break

        # Click the next page button
        await page.click("[class='a-last']")
        
    data = pd.DataFrame(reviews, columns=['product_colour','review_title','review_body'])
    data.to_csv('amazon_product_reviews.csv', index=False)
    await browser.close()

await main()

