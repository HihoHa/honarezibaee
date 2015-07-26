from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from . import views
from m_article.views import banner_redirect
from myflatpages.views import flatpage
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'beauty.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('m_article.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^logout/$', views.logout_view, name="logout_view"),
    url(r'^login/$', views.login_view, name="login_view"),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^api/', include('apis.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^banner/(?P<banner_pk>\d+)', banner_redirect, name="ad_view"),
    url(r'^about-us/$', flatpage, {'url': '/about-us/'}, name='about_us'),
    url(r'^contact-us/$', flatpage, {'url': '/contact-us/'}, name='contact_us'),
    url(r'^advertisement/$', flatpage, {'url': '/ad/'}, name='advertisement'),
    url(r'', include('m_article.urls')),
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS )

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )