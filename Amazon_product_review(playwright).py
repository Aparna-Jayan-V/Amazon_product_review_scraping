
# importing necessary libraries
import random
import asyncio
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

# Perform a request and retries the request if it fails
async def perform_request_with_retry(page, link):
    MAX_RETRIES = 5
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            await page.goto(link)
            break
        except:
            retry_count += 1
            if retry_count == MAX_RETRIES:
                raise Exception("Request timed out")
            await asyncio.sleep(random.uniform(1, 5))

# Extract the title of a review from a review element
async def extract_review_title(page,review_element):
    title = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-title\"]').innerText", review_element)
    title = title.replace("\n", "")
    return title.strip()

# Extract the body of a review from a review element
async def extract_review_body(page,review_element):
    body = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-body\"]').innerText", review_element)
    body = body.replace("\n", "")
    return body.strip()

# Extract the colour of the product reviewed from a review element
async def extract_product_colour(page,review_element):
    colour = await page.evaluate("(element) => element.querySelector('[data-hook=\"format-strip\"]').innerText", review_element)
    return colour.replace("Colour: ", "")

# Extract the date of a review from a review element
async def extract_review_date(page,review_element):
    date = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-date\"]').innerText", review_element)
    date = date.split()[-3:]
    date = " ".join(date)
    date = datetime.strptime(date, '%d %B %Y')
    return date.strftime('%d %B %Y')

# Extract the rating of a review from a review element
async def extract_rating(page,review_element):
    ratings = await page.evaluate("(element) => element.querySelector('[data-hook=\"review-star-rating\"]').innerText", review_element)
    return ratings.split()[0]

# Extract all reviews from multiple pages of the URL
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

# Save the extracted reviews to a csv file
async def save_reviews_to_csv(reviews):
        data = pd.DataFrame(reviews, columns=['product_colour','review_title','review_body','review_date','rating'])
        data.to_csv('amazon_product_reviews13.csv', index=False)

# Asynchronous Web Scraping of Amazon Product Reviews using Playwright
async def main():
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        url="https://www.amazon.in/boAt-Airdopes-191G-Wireless-Appealing/product-reviews/B09X76VL5L/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
        await perform_request_with_retry(page, url)

        review = await extract_reviews(page)
        await save_reviews_to_csv(review)
        await browser.close()

# Execute the scraping and saving of Amazon product reviews
await main()


