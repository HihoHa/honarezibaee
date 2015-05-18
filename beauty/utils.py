from bs4 import BeautifulSoup, NavigableString
import re


class MobileViewRefiner(object):
    '''
    gets an html and returns mobile view
    '''
    def __init__(self, html):
        self.mobile = []
        self.soup = BeautifulSoup(html)

    def dfs(self, tag, is_bold):
        if isinstance(tag, NavigableString):
            self.mobile.append((is_bold, unicode(tag)))
            return
        if tag.name == 'img':
            self.mobile.append((3, tag['src']))
            return
        if tag.name in ['b', 'h1', 'h2', 'h3', 'h4']:
            is_bold = 2
        for child in tag.children:
            self.dfs(child, is_bold)
        if tag.name in ['p', 'h1', 'h2', 'h3']:
            self.mobile.append((4, 0))
        return

    def refine(self):
        self.dfs(self.soup, 1)
        return self.mobile


class ListFromStringRefiner(object):

    def __init__(self, string):
        self.string = string

    def refine(self):
        word_list = re.split('\W+', self.string, flags=re.UNICODE)
        return word_list

def m_view(attribute_names, mobile_names, refiner_classes):
    def decorator(cls):
        def new_getattr(self, name):
            if name in mobile_names:
                index = mobile_names.index(name)
                refiner = refiner_classes[index](super(cls, self).__getattribute__(attribute_names[index]))
                return refiner.refine()
            else:
                return super(cls, self).__getattribute__(name)
        cls.__getattr__ = new_getattr
        return cls
    return decorator