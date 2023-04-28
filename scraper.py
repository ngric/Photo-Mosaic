import argparse
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_image_urls(query: str, num_images: int = 400) -> list:
    """
    Gets urls directing to thumbnails for a google image search

    Args:
        query: The query string
        num_images: The number of urls to retreive. Note: Google probably won't return >400

    Returns:
        A list of urls to image thumbnails
    """
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}&tbm=isch"

    driver = webdriver.Chrome()
    driver.get(url)

    image_urls = set()
    image_count = 0
    page_count = 1
    last_image_count = -1
    show_more_clicks = 0
    max_show_more_clicks = 10

    while image_count < num_images and image_count != last_image_count:
        last_image_count = image_count
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = BeautifulSoup(html, 'html.parser')

        for img in soup.find_all('img', {'src': re.compile('^https://')}):
            # Thumbnails are in 'rg_i' class. This will probably get changed by the time you're using this script
            if 'rg_i' in img.get('class', []):
                img_url = img['src']
                image_urls.add(img_url)
                image_count = len(image_urls)

                if image_count >= num_images:
                    break

            # Every couple of pages, google requires a button press
            if show_more_clicks < max_show_more_clicks:
                try:
                    show_more_button = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@value="Show more results"]'))
                    )
                    show_more_button.click()
                    show_more_clicks += 1
                    time.sleep(2)
                except Exception as e:
                    pass
                    # print(f"Show more button not found: {type(e).__name__}")

        print(f"{query}: page {page_count}, {image_count}/{num_images} urls found")

        # Scroll down to load more images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        page_count += 1
        time.sleep(2)

    driver.quit()
    return list(image_urls)

def download_images(images: list, query: str):
    """
    Downloads images in passed list

    Args:
        images: The list of image urls to download
        query: The query string. Used for filenames
    """
    print(f"Downloading {query} images...")
    output_dir = "images"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, img_url in enumerate(images):
        img_data = requests.get(img_url).content

        with open(f"{output_dir}/{query}_{i}.jpg", "wb") as f:
            f.write(img_data)
    print("Done.")

def main():
    parser = argparse.ArgumentParser(description="Scrape/download images from Google Images")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-q", "--query", help="A single query to search for images")
    group.add_argument("-f", "--file", help="A file containing one query per line")

    args = parser.parse_args()

    if args.query:
        images = get_image_urls(args.query)
        download_images(images, args.query)
    elif args.file:
        with open(args.file, 'r') as file:
            queries = [line.strip() for line in file.readlines()]
            for query in queries:
                images = get_image_urls(query)
                download_images(images, query)

if __name__ == "__main__":
    main()
