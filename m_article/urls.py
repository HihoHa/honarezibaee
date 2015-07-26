from django.conf.urls import patterns, include, url
from m_article import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beauty.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.ArticleListView.as_view()),
    url(r'^tag/(?P<tag_name>[^/]*)/$', views.ArticleListView.as_view(), name="tag_view"),
    url(r'^(?P<category_name>[0-9A-Za-z_//-]*)/$', views.ArticleListViewByCategory.as_view(), name="article_view_by_category"),
    url(r'^(?P<category_name>[0-9A-Za-z_//-]*)/(?P<article_title>[^/]*)/$', views.ArticleView.as_view(), name="article_view"),

    # url(r'^$', views.test_page)
    )