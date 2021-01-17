from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pathlib import Path


class BaseParser(object):
    def __init__(self):
        self.PATH = "C:\Program Files (x86)\chromedriver.exe"
        self.driver = webdriver.Chrome(self.PATH)
        self.main_page = None

    def redirect_to_page(self, url):
        if url:
            self.driver.get(url)
        else:
            self.driver.get(self.main_page)

    @staticmethod
    def get_href_from_a_tag(x):
        return x.text, x.get_attribute("href")

    def main(self):
        pass


class RussianPoemsParser(BaseParser):
    def __init__(self):
        super(RussianPoemsParser, self).__init__()
        self.main_page = "https://rustih.ru/stihi-russkih-poetov-klassikov/"
        self.driver.get(self.main_page)
        self.WritePoemsToFile = WritePoemsToFile('ru')

    def parse_href(self, css_selector):
        main_div = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        return list(map(self.get_href_from_a_tag, main_div.find_elements(By.TAG_NAME, 'a')))

    def parse_poem(self):
        poem = self.driver.find_element(By.CSS_SELECTOR, 'div.entry-content.poem-text').text
        split_text = [
            "\n__________",
            "__________",
            "\nАнализ «",
            "\nАнализ ",
            "\nПримечания ",
            "Анализ стихотворения ",
            "Анализ поэмы ",
            "Анализ трагедии ",
            "Анализ элегии "]
        for s in split_text:
            poem = poem.split(s)[0]
        return poem

    def main(self):
        poets_href_list = self.parse_href('div.taxonomy-description')

        for key, poets_tag in enumerate(poets_href_list):
            name, href = poets_tag
            print(name)
            # if key < 17:
            #     continue
            writer_name = name.replace(" ", "_")
            href_poems = list()

            self.redirect_to_page(href)
            time.sleep(2)
            # get off ads
            title = self.driver.find_element(By.CSS_SELECTOR, 'h1.page-title').text
            if name.lower() not in title.lower():
                self.driver.refresh()
                time.sleep(2)

            temp_list_poems = self.parse_href('div.posts-container')
            href_poems += temp_list_poems

            page_number = "1"
            while True:
                try:
                    page = self.driver.find_element(By.CSS_SELECTOR, 'a.next.page-numbers')
                    page.click()
                    time.sleep(2)
                    # get off ads
                    current_page = self.driver.find_element(By.CSS_SELECTOR, 'span.page-numbers').text
                    print(f"{page_number} - {current_page}")
                    if current_page == "...":
                        current_page = self.driver.find_elements(By.CSS_SELECTOR, 'span.page-numbers')[1].text
                    if page_number == current_page:
                        self.driver.refresh()
                        time.sleep(2)
                        current_page = self.driver.find_element(By.CSS_SELECTOR, 'span.page-numbers').text
                        page = self.driver.find_element(By.CSS_SELECTOR, 'a.next.page-numbers')
                        page.click()
                        time.sleep(2)
                    page_number = current_page
                except:
                    break

                temp_list_poems = self.parse_href('div.posts-container')
                href_poems += temp_list_poems

            self.WritePoemsToFile.open_file(writer_name)
            for poem_key, href_poem in enumerate(href_poems):
                try:
                    self.redirect_to_page(href_poem[1])
                    poem = self.parse_poem()
                except:
                    continue
                print(f"{poem_key}/{len(href_poems)} {href_poem[0]}")
                self.WritePoemsToFile.save_poem(poem)
            self.WritePoemsToFile.close_file()
            del href_poems
            del temp_list_poems


class WritePoemsToFile(object):
    def __init__(self, local='ru'):
        self.base_dir = 'Poems'
        self.poems_dir = f".{self.base_dir}/{local}"
        Path(self.poems_dir).mkdir(parents=True, exist_ok=True)
        self.file = None

    def open_file(self, writer_name):
        self.file = open(f"{self.poems_dir}/{writer_name}.txt", "a")

    def save_poem(self, poem):
        try:
            self.file.write(f"\n{poem}")
            self.file.write(f"\n----------")
        except:
            pass

    def close_file(self):
        self.file.close()

    def save_poems(self, writer_name, poems):
        with open(f"{self.poems_dir}/{writer_name}.txt", "a") as poems_file:
            for poem in poems:
                poems_file.write(f"\n{poem}")

    def __del__(self):
        self.file.close()
