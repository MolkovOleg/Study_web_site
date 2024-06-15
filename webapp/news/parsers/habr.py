from datetime import datetime

from bs4 import BeautifulSoup as bf

from webapp.news.parsers.utils import get_html, save_news
from webapp.news.models import News
from webapp import db

def get_habr_snippets():
    html = get_html('https://habr.com/ru/search/?q=python&target_type=posts&order=date')
    if html:
        soup = bf(html, 'html.parser')
        all_posts = soup.find('div', class_='tm-articles-list').find_all('article', class_='tm-articles-list__item')
        for post in all_posts:
            title = post.find('h2', class_='tm-title tm-title_h2').text
            url = 'http://habr.com' + post.find('h2').find('a', class_='tm-title__link')['href']
            published = post.find('span', class_='tm-user-info__user tm-user-info__user_appearance-default').find('time')['title']

            try:
                published = datetime.strptime(published, '%Y-%m-%d, %H:%M')
            except ValueError:
                published = datetime.now()

            save_news(title, url, published)

def get_habr_news_text():
    news_without_text = News.query.filter(News.text.is_(None))
    for news in news_without_text:
        html = get_html(news.url)
        if html:
            soup = bf(html, 'html.parser')
            article = soup.find('div', id='post-content-body').decode_contents()
            if article:
                news.text = article
                db.session.add(news)
                db.session.commit()
