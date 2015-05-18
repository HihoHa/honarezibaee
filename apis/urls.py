from django.conf.urls import patterns, include, url
from apis import views
urlpatterns = patterns('',
    url(r'^article/(?P<pk>\d+)/$', views.ArticleView.as_view(), name='json_job_view'),
    url(r'^job/(?P<pk>\d+)/$', views.JobView.as_view(), name='json_article_view'),
    url(r'^article_categories/$', views.ArticleCategoryListView.as_view(), name='json_article_category_list_view'),
    url(r'^article_tags/$', views.ArticleTagListView.as_view(), name='json_article_tag_list_view'),
    url(r'^job_categories/$', views.JobCategoryListView.as_view(), name='json_job_category_list_view'),
    url(r'^job_tags/$', views.JobTagListView.as_view(), name='json_job_tag_list_view'),
    url(r'^article/by_category/(?P<pk>\d+)/$', views.ArticleByCategoryListView.as_view(),
        name='json_article_by_category_list_view'),
    url(r'^article/by_tag/(?P<pk>\d+)/$', views.ArticleByTagListView.as_view(), name='json_article_by_tag_list_view'),
    url(r'^job/by_category/(?P<pk>\d+)/$', views.JobByCategoryListView.as_view(), name='json_job_by_category_list_view'),
    url(r'^job/by_tag/(?P<pk>\d+)/$', views.JobByTagListView.as_view(), name='json_job_by_tag_list_view'),
)