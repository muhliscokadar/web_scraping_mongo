from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
  executable_path = {'executable_path': 'chromedriver.exe'}
  browser = Browser('chrome', **executable_path, headless=True)

  news_title, news_paragraph = mars_news(browser)

  data = {
    'news_title':news_title,  
    'news_paragraph':news_paragraph,
    "featured_image": featured_image(browser),
    "weather": twitter_weather(browser),
    "facts": mars_facts(),
    "hemispheres": mars_hemispheres(browser),
    # "last_modified": dt.datetime.now()

  }
  browser.quit()
  return data

def mars_news(browser):
  # Visit the NASA news URL
  nasa_url = "https://mars.nasa.gov/news/"
  browser.visit(nasa_url)

  browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

  html = browser.html
  soup = BeautifulSoup(html,'html.parser')

  try:
    slide_elem = soup.select_one('ul.item_list li.slide')
    news_title = slide_elem.find("div", class_='content_title').get_text()
    news_paragraph =  slide_elem.find("div", class_='article_teaser_body').get_text()

  except AttributeError:
    return None, None
  
  return news_title, news_paragraph


def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image = browser.find_by_id("full_image")
    full_image.click()

    # Find the more info button and click that
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_elem = browser.find_link_by_partial_text("more info")
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    image_soup  = BeautifulSoup(html, "html.parser")

    # Find the relative image url
    image = image_soup.select_one("figure.lede a img")

    try:
        url_image = image.get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    image_url = f'https://www.jpl.nasa.gov{url_image}'

    return image_url



# def mars_hemispheres(browser):

#     # A way to break up long strings
#     url = (
#         'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
#     )

#     browser.visit(url)

#     # Click the link, find the sample anchor, return the href
#     hemisphere_image_urls = []
#     for i in range(4):

#         # Find the elements on each loop to avoid a stale element exception
#         browser.find_by_css("a.product-item h3")[i].click()

#         hemi_data = scrape_hemisphere(browser.html)

#         # Append hemisphere object to list
#         hemisphere_image_urls.append(hemi_data)

#         # Finally, we navigate backwards
#         browser.back()

#     return hemisphere_image_urls

def twitter_weather(browser):
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twitter_url)

    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')

    # First, find a tweet with the data-name `Mars Weather`
    tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_twitter = weather_soup.find("div", attrs=tweet_attrs)

    # Next, search within the tweet for the p tag containing the tweet text
    mars_weather = mars_weather_twitter.find("p", "tweet-text").get_text()

    return mars_weather


def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    df.columns = ['description', 'value']
    df.set_index('description', inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


def scrape_hemisphere(html_text):

    # Soupify the html text
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere




def mars_hemispheres(browser):

    # A way to break up long strings
    url = (
        'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    )

    browser.visit(url)

    # Click the link, find the sample anchor, return the href
    hemisphere_image_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemi_data)

        # Finally, we navigate backwards
        browser.back()

    return hemisphere_image_urls



if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())