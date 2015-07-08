import re
import os
from lxml.html.clean import Cleaner
from beauty.settings import MEDIA_ROOT, MEDIA_URL
from bs4 import BeautifulSoup
from urlparse import urljoin
import requests
import hashlib

article_name_regex = re.compile(ur'(?<=article/)[^//]*', re.UNICODE)
tag_name_regex = re.compile(ur'(?<=article/tag/)[^//]*', re.UNICODE)


def get_article_from_url(url):
    return article_name_regex.search(url).group()


def get_tag_from_url(url):
    return tag_name_regex.search(url).group()

cleaner = Cleaner(style=True, page_structure=True, remove_tags=['a'], scripts=True)


def unique_name(link):
    i = link.rfind('.')
    return hashlib.md5(link[:i]).hexdigest()+'.'+link[i+1:]

#inputs a cut of a html document, downloads the links in the documet to the local host and returns the html document with replaced local image links
#base url is the url of the webpage in which the images are placed. This is for computing absolute path from relative path
def localize(document, download_folder=MEDIA_ROOT, base_url='http://'):
    chunk_size = 1024#TODO: is this a good size?
    soup = BeautifulSoup(document)
    for link in soup('img'):
        src = urljoin(base_url, link['src'])
        file_name = unique_name(src)
        request = requests.get(src, stream=True)
        with open(os.path.join(MEDIA_ROOT, file_name), 'wb') as fd:
            for chunk in request.iter_content(chunk_size):
                fd.write(chunk)
        link['src'] = urljoin(MEDIA_URL, file_name)
    return soup.prettify()


def edit_image_attr(document, url, alt):
    soup = BeautifulSoup(document)
    for img in soup('img'):
        img['alt'] = alt
        img['title'] = alt
        img['class'] = 'img-responsive center-block'
        if img.parent.name != u'a':
            link = img.wrap(soup.new_tag('a'))
            link['href'] = url
            link['class'] = 'text-center'
        else:
            link = img.parent
            link['href'] = url
    return soup.prettify(formatter=None)


def with_new_line(content):
    soup = BeautifulSoup(content)
    for p in soup('p'):
        if p.string == '\n':
            p.string = br'&nbsp;'
    return soup.prettify(formatter=None)  # to preserve &nbsp
