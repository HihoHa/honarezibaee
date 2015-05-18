from django.conf.urls import patterns, include, url
from jobs import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beauty.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.JobSearch.as_view(), name='job_main'),
    url(r'^search/$', views.JobSearch.as_view(), name='job_search'),
    url(r'^(?P<job_name>[^/]*)/$', views.JobView.as_view(), name="job_view"),
    url(r'^category/(?P<category_name>[^/]*)/$', views.JobListViewByCategory.as_view(), name='job_by_category_view'),
    
   # url(r'^search/results/$', views.JobSearchResult.as_view(), name='job_search_result_view'),

    )