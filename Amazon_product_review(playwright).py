
import asyncio
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

async def extract_review_title(page,review_element):
    title = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-title\"]').innerText", review_element)
    title = title.replace("\n", "")
    return title.strip()

async def extract_review_body(page,review_element):
    body = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-body\"]').innerText", review_element)
    body = body.replace("\n", "")
    return body.strip()

async def extract_product_colour(page,review_element):
    colour = await page.evaluate("(element) => element.querySelector('[data-hook=\"format-strip\"]').innerText", review_element)
    return colour.replace("Colour: ", "")

async def extract_review_date(page,review_element):
    date = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-date\"]').innerText", review_element)
    date = date.split()[-3:]
    date = " ".join(date)
    date = datetime.strptime(date, '%d %B %Y')
    return date.strftime('%d %B %Y')

async def extract_rating(page,review_element):
    ratings = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-star-rating\"]').innerText", review_element)
    return ratings.split()[0]

async def extract_reviews(page):
    reviews =[]
    while True:
        # Wait for the reviews to be loaded
        await page.wait_for_selector("[data-hook='review']")

        # Get the reviews
        review_elements = await page.query_selector_all("[data-hook='review']")
        for review_element in review_elements:
            review_title = await extract_review_title(page,review_element)
            review_body = await extract_review_body(page,review_element)
            product_colour = await extract_product_colour(page,review_element)
            review_date = await extract_review_date(page,review_element)
            rating = await extract_rating(page,review_element)

            reviews.append((product_colour,review_title,review_body,review_date,rating))

        # Find the next page button
        next_page_button = await page.query_selector("[class='a-last']")
        if not next_page_button:
            break

        # Click the next page button
        await page.click("[class='a-last']")
    return reviews


async def save_reviews_to_csv(reviews):
        data = pd.DataFrame(reviews, columns=['product_colour','review_title','review_body','review_date','rating'])
        data.to_csv('amazon_product_reviews.csv', index=False)

async def main():
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.amazon.in/boAt-Airdopes-191G-Wireless-Appealing/product-reviews/B09X76VL5L/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews")

        review = await extract_reviews(page)
        await save_reviews_to_csv(review)
        await browser.close()

await main()

