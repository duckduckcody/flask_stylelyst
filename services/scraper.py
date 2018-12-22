#find the javascript map equvialent to make this better
from bs4 import BeautifulSoup
import requests
import time

def scrape_websites(user_settings, websites):
    hot_clothes = []
    for website in websites:
        if website.get('id') in user_settings.websites:
            hot_clothes = hot_clothes + update_website_data(user_settings, website)
    return hot_clothes

def update_website_data(user_settings, website):
    url_info = find_url_info(user_settings, website)
    page = find_page(url_info, user_settings)
    print(page)
    if page.get('time_stamp') is None or time.time() - page.get('time_stamp') > 86400: # if clothes data over 1 day old
        scrape_wesbite(user_settings, website.get('base_url'), website.get('scraper_config'), url_info)
    return url_info.get('clothes')

def find_url_info(user_settings, website):
    return next((url for url in website.get('urls') if url['gender'] == user_settings.gender and url['category'] == user_settings.category), None)

def find_page(url_info, user_settings):
    return next((page for page in url_info.get('pages') if page.get('page') == user_settings.current_page), None)

def get_html(url, current_page):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'}
    return BeautifulSoup(requests.get(url + current_page, headers=headers).text, 'lxml')

def scrape_wesbite(user_settings, base_url, config, url_info):
    url_info['clothes'] = []
    url_info['time_stamp'] = time.time()
    for product in get_html(url_info.get('url'), user_settings.current_page).find_all(config['container']['tag'], class_=config['container']['class']):
        url_info['clothes'].append({
            'price': product.span.text if config.get('price') is None else product.find(config['price']['tag'], class_=config['price']['class']).text,
            'img': product.img['src'] if config.get('img') is None else product.find(config['img']['tag'], class_=config['img']['class']).img['data-src'],
            'name': product.h2.text if config.get('name') is None else product.find(config['name']['tag'], class_=config['name']['class']).a.text,
            'link': base_url + product.find('a')['href'] if config.get('link') is None else base_url + product.find(config['link']['tag'], class_=config['link']['class'])['href']
        })
    return url_info.get('clothes')