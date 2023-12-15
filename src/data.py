from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

import spacy
import requests
import time 
import os

URL = "https://www.vesti.ru/news"
NLP = spacy.load('ru_core_news_md')


def _scroll_page(driver):
	footer = driver.find_element(By.TAG_NAME, "footer")
	delta_y = int(footer.rect['y'])
	ActionChains(driver).scroll_by_amount(0, delta_y).perform()


def _get_news_objects(driver):
	return driver.find_element(By.XPATH, "/html/body/div[6]/div/div/div[1]/div").find_elements(By.CLASS_NAME, "list__title")


def get_news(url, count):
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')
	driver = webdriver.Chrome(options=chrome_options)
	driver.get(url)

	while len(news_objects := _get_news_objects(driver)) < count:
		_scroll_page(driver)

	news_list = []
	for news in news_objects:
		title = news.text
		url = news.find_element(By.TAG_NAME, "a").get_attribute('href')
		news_list.append((title, url))
		
	driver.close()
	return news_list


def filter_text(text):
	tokens = []
	for token in NLP(text):
		if token.is_stop or token.is_punct or (token.lemma_.replace(' ', '') == ''):
			continue
		tokens.append(token.lemma_.lower())
	return tokens


def get_tags(url):
	tags_objects = BeautifulSoup(requests.get(url).text, "html.parser").find_all('a', class_='tags__item')
	tags_string = " ".join([el.text for el in tags_objects])
	return filter_text(tags_string)


def update_database(count):
	print("Обновление базы данных...")
	old_tags = []
	new_tags = []

	for current_title, current_url in get_news(URL, count):
		new_tags.extend(get_tags(current_url))

	with open("database.txt", 'r+') as file: 
		old_tags = file.read().splitlines()

	with open("database.txt", 'a+') as file:
		new_tags = list(filter(lambda tag: tag not in old_tags, new_tags))
		file.writelines(tag + "\n" for tag in new_tags)
		print("Добавлены новые теги: ", new_tags)
