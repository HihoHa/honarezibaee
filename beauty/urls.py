from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from m_article.views import banner_redirect

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beauty.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('m_article.urls')),
    url(r'^article/', include('m_article.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^summernote/', include('django_summernote.urls')),
    url(r'^logout/$', views.logout_view, name="logout_view"),
    url(r'^login/$', views.login_view, name="login_view"),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^api/', include('apis.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^banner/(?P<banner_pk>\d+)', banner_redirect, name="ad_view"),
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS )