from splinter import Browser, browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    img_urls_titles = hemisphere(browser)

    data = {
        'news_title' : news_title,
        'news_paragraph' : news_paragraph,
        'featured_image' : featured_image(browser),
        'facts' : mars_facts(),
        'hemispheres' : img_urls_titles,
        'last_modified' : dt.datetime.now()
    }
    browser.quit()
    return data

def mars_news(browser):
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        news_title = slide_elem.find('div', class_='content_title').get_text()
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None 

    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    df.columns = ['Description','Mars','Earth']
    df.set_index('Description', inplace=True)

    return df.to_html()
    
def hemisphere(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    hemisphere_image_urls = []

    img_links = browser.find_by_css("a.product-item h3")

    for x in range(len(img_links)):
        hemisphere={}

        # Find elements going to click link 
        browser.find_by_css("a.product-item h3")[x].click()

        # Find sample Image link
        sample_img= browser.find_link_by_text("Sample").first
        hemisphere['img_url']=sample_img['href']

        # Get hemisphere Title
        hemisphere['title']=browser.find_by_css("h2.title").text

        #Add Objects to hemisphere_img_urls list
        hemisphere_image_urls.append(hemisphere)

        # Go Back
        browser.back()
    return hemisphere_image_urls

if __name__ == "__main__":
    print(scrape_all())