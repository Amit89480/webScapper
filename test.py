import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
import datetime


class Article:
    def __init__(self, url, headline, author, date):
        self.url = url
        self.headline = headline
        self.author = author
        self.date = date

    def to_csv_row(self):
        return [self.url, self.headline, self.author, self.date]

    def to_sql_values(self):
        return (self.url, self.headline, self.author, self.date)


class VergeScraper:
    def __init__(self, url):
        self.url = url
        self.articles = []

    def scrape(self):

        response = requests.get(self.url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')

        article_elements = soup.find_all('article')

        for article_element in article_elements:
            try:

                url = article_element.find('a')['href']
                headline = article_element.find(
                    'h2', {'class': 'c-entry-box--compact__title'}).text.strip()
                author = article_element.find(
                    'span', {'class': 'c-byline__item'}).text.strip()
                date = article_element.find('time')['datetime']

                article = Article(url, headline, author, date)
                self.articles.append(article)

            except Exception as e:
                print(e)
                continue

    def save_to_csv(self, file):
        with open(file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['URL', 'Headline', 'Author', 'Date'])

            for article in self.articles:
                csv_writer.writerow(article.to_csv_row())

    def save_to_sqlite(self, database):
        conn = sqlite3.connect(database)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS articles
                     (url TEXT PRIMARY KEY,
                      headline TEXT,
                      author TEXT,
                      date TEXT)''')

        for article in self.articles:
            try:
                c.execute('INSERT INTO articles (url, headline, author, date) VALUES (?, ?, ?, ?)',
                          article.to_sql_values())

            except sqlite3.IntegrityError:

                continue

        conn.commit()
        conn.close()


if __name__ == '__main__':

    url = 'https://www.theverge.com'

    scraper = VergeScraper(url)
    scraper.scrape()

    now = datetime.datetime.now().strftime('%d%m%Y')

    csv_filename = f'{now}_verge.csv'
    scraper.save_to_csv(csv_filename)

    db_filename = 'verge.db'
    scraper.save_to_sqlite(db_filename)
