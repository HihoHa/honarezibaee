from m_article.models import Article, ArticleCategory, SlideShow, AdvertisementBanner
from datetime import datetime, timedelta

def theme_context(request):
        context = {}
        context['menuitems'] = ArticleCategory.get_root_nodes().order_by('ordering')
        new_articles = Article.non_archived_objects.filter(created_at__gte=(datetime.utcnow() - timedelta(days=15)))
        context['hot'] = new_articles.order_by('-views')[:7]
        context['best'] = new_articles.order_by('-likes')[:7]
        multimedia_categories = ArticleCategory.objects.filter(is_multimedia=True)
        context['new_multimedia_non_video'] = Article.publishable_objects.filter(
            category__in=list(multimedia_categories)).filter(video=None).order_by('-views')[:7]
        context['new_viedeos'] = Article.publishable_objects.filter(
            category__in=list(multimedia_categories)).exclude(video=None).order_by('-views')[:7]
        context['multimedia_categories'] = multimedia_categories
        context['banners'] = AdvertisementBanner.publishable.all().order_by('?')
        for banner in context['banners']:
            banner.views += 1
            banner.save()
        return context