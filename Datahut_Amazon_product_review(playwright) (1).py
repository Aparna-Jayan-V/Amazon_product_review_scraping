#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[1]:


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
async def extract_review_title(review_element):
    try:
        title = await review_element.evaluate("(element) => element.querySelector('[data-hook=\"review-title\"]').innerText")
        title = title.replace("\n", "")
        title = title.strip()
    except:
        title = "not available"
    return title

# Extract the body of a review from a review element
async def extract_review_body(review_element):
    try:
        body = await review_element.evaluate("(element) => element.querySelector('[data-hook=\"review-body\"]').innerText")
        body = body.replace("\n", "")
        body = body.strip()
    except:
        body = "not available"
    return body

# Extract the colour of the product reviewed from a review element
async def extract_product_colour(review_element):
    try:
        colour = await review_element.evaluate("(element) => element.querySelector('[data-hook=\"format-strip\"]').innerText")
        colour = colour.replace("Colour: ", "")
    except:
        colour = "not available"
    return colour

# Extract the date of a review from a review element
async def extract_review_date(review_element):
    try:
        date = await review_element.evaluate("(element) => element.querySelector('[data-hook=\"review-date\"]').innerText")
        date = date.split()[-3:]
        date = " ".join(date)
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%d %B %Y')
    except:
        date = "not available"
    return date

# Extract the rating of a review from a review element
async def extract_rating(review_element):
    try:
        ratings = await review_element.evaluate("(element) => element.querySelector('[data-hook=\"review-star-rating\"]').innerText")
    except:
        ratings="not available"
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
            review_title = await extract_review_title(review_element)
            review_body = await extract_review_body(review_element)
            product_colour = await extract_product_colour(review_element)
            review_date = await extract_review_date(review_element)
            rating = await extract_rating(review_element)
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
        data.to_csv('amazon_product_reviews15.csv', index=False)

# # Asynchronous Web Scraping of Amazon Product Reviews using Playwright
async def main():
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url="https://www.amazon.in/boAt-Airdopes-191G-Wireless-Appealing/product-reviews/B09X76VL5L/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
        await perform_request_with_retry(page, url)

        review = await extract_reviews(page)
        await save_reviews_to_csv(review)
        await browser.close()

# Execute the scraping and saving of Amazon product reviews
await main()


# In[2]:


data=pd.read_csv('amazon_product_reviews15.csv')
data


# In[ ]:




