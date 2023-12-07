from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService 
from bs4 import BeautifulSoup
import requests
import time 
import csv

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
 
# load target website 
URL = "https://www.vesti.ru/news"
 
# get website content 
driver.get(URL) 
 
# instantiate height of webpage 
last_height = driver.execute_script('return document.body.scrollHeight') 
 
header = ['title', 'url', 'tags']
news_target_count = 1000
news_current_count = 0

def get_news(id):
	try:
		return driver.find_element(By.XPATH, f"/html/body/div[6]/div/div/div[1]/div/div[{news_current_count + 1}]/div/h3/a")
	except:
		return None

with open("./dataset.tsv", 'w') as file:
	writer = csv.writer(file, delimiter='\t')
	writer.writerow(header)

	while news_current_count < news_target_count: 

		# scroll
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') 
		time.sleep(2) 
		new_height = driver.execute_script('return document.body.scrollHeight') 
		if new_height == last_height: 
			break 
		last_height = new_height 

		while ((element := get_news(news_current_count)) != None):
			
			title = element.text
			url = element.get_attribute('href')

			tags = BeautifulSoup(requests.get(url).text, "html.parser").findAll('a', class_='tags__item')
			tags = ",".join([el.text for el in tags])

			writer.writerow([title, url, tags])
			print([title, url, tags])
			news_current_count += 1