from m_article.utils import get_article_from_url, get_tag_from_url
from django.shortcuts import render_to_response, render, redirect
from m_article.models import Article, ArticleTag, ArticleCategory, SlideShow
from django.views.generic import View, DetailView
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm
from django.core.urlresolvers import reverse
from django.contrib import messages
from cookie_user.models import mCookieUser, Opinion
import uuid
from django import forms
from datetime import datetime
from ipware.ip import get_ip  # todo: import and use get_real_ip instead
import logging
from django.utils import timezone
from django.http import Http404
from datetime import datetime, timedelta

logger = logging.getLogger('django')


class BaseView(TemplateView):
    template_name = 'base.html'
    view_name = 'article_view_by_category'

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['menuitems'] = ArticleCategory.get_root_nodes().order_by('ordering')
        new_articles = Article.non_archived_objects.filter(created_at__lte=(datetime.utcnow() - timedelta(days=15)))
        context['hot'] = new_articles.order_by('-views')[:5]
        context['best'] = new_articles.order_by('-likes')[:5]
        context['view_name'] = self.view_name
        context['slides'] = SlideShow.objects.all()
        context['multimedia_categories'] = ArticleCategory.objects.filter(is_multimedia=True)
        return context


class VoteForm(forms.ModelForm):
    class Meta:
        model = Opinion
        fields = ['like', 'dislike']
        # exclude = ['ip', 'date', 'user', 'article']: Does nothing. exclude means these fields exclude from models validation (.clean() method).


class ArticleView(BaseView):
    template_name = 'm_article/article.html'
    set_cookie = False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cookie_user = mCookieUser.objects.get(user_id=request.COOKIES.get('user_id', None))
        except:
            user_id = uuid.uuid4()  # distinct ids for users
            # if mCookieUser.objects.filter(user_id=user_id).exists():
            self.cookie_user = mCookieUser.objects.create(user_id=user_id)
            self.set_cookie, self.user_id = True, user_id
        # logger.error('fuck')
        article_title = kwargs['article_title']
        self.article = Article.publishable_objects.get(title=article_title)
        self.opinion, self.opinion_is_new = Opinion.objects.get_or_create(user=self.cookie_user,
                                                                          article=self.article,
                                                                          defaults={'date': timezone.now(),
                                                                                    'ip': get_ip(request)})
        # self.form = VoteForm(request.POST or None, instance=self.opinion)

        return super(ArticleView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.article.first_category().url_prefix() != self.kwargs['category_name']:
            raise Http404(self.kwargs['category_name'] + '***' + self.article.first_category().url_prefix())
        self.article.views += 1
        self.article.save()
        return super(ArticleView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)
        context['article'] = self.article
        context['related_articles'] = self.article.related_articles.all()
        context['vote_form'] = VoteForm(instance=self.opinion)
        # context['comments'] = ArticleComment.objects.filter(article = self.article).filter(is_verified=True)
        context['cookie_user'] = self.cookie_user
        context['recent_related'] = Article.get_by_category(self.article.category.all().first().get_root()).exclude(pk=self.article.pk).order_by('-created_at')[:6]
        context['slides'] = None
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(ArticleView, self).render_to_response(context, **response_kwargs)
        if self.set_cookie:
            response.set_cookie('user_id', self.user_id,
                                max_age=10 * 365 * 24 * 60 * 60)  # todo: set the duration of cookie
        return response

    def post(self, request, *args, **kwargs):
        opinion, opinion_is_new = self.opinion, self.opinion_is_new
        old_like, old_dislike = opinion.like, opinion.dislike
        form = VoteForm(request.POST, instance=opinion)
        # logger.error('first we are here!')
        if form.is_valid():
            article = self.article
            if opinion_is_new:
                article.likes += form.cleaned_data['like']
                article.dislikes += form.cleaned_data['dislike']
            else:
                article.likes += form.cleaned_data['like'] - old_like
                article.dislikes += form.cleaned_data['dislike'] - old_dislike
            article.save()
            opinion = form.save(commit=False)
            opinion.date = timezone.now()
            opinion.ip = get_ip(request)
            opinion.save()
        context = self.get_context_data(**kwargs)
        context['vote_form'] = form
        return self.render_to_response(context)

        # def post(self, request, *args, **kwargs):
        # article_title = kwargs['article_title']
        # article = Article.publishable_objects.get(title=article_title)
        #     form = CommentForm(request.POST)
        #     if form.is_valid():
        #         user = request.user
        #         content = form.cleaned_data['comment']
        #         ArticleComment.objects.create(user = user, content = content, article = article)
        #         messages.info(self.request, 'your comment has been submitted')#, extra_tags="comment_message")
        #         messages.warning(self.request, 'your comment needs verification for apearing on this page')
        #     return redirect('article_view', article_title=article_title)


class ArticleListView(BaseView):
    template_name = 'm_article/article_list.html'
    article_per_page = 3

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page')
        context['page'] = page

        tag = kwargs.get('tag')
        if tag:
            articles = Article.m_get_by_tag(tag).order_by('-created_at')
        else:
            articles = Article.non_archived_objects.all().order_by('-created_at')
        paginator = Paginator(articles, self.article_per_page)
        try:
            context['articles'] = paginator.page(page)
        except EmptyPage:
            context['articles'] = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            context['articles'] = paginator.page(1)
        return context


class ArticleListViewByCategory(BaseView):
    template_name = "m_article/article_list.html"
    article_per_page = 3

    def get_context_data(self, **kwargs):
        context = super(ArticleListViewByCategory, self).get_context_data(**kwargs)
        category_name = self.kwargs['category_name']
        page = self.request.GET.get('page')
        category = ArticleCategory.from_url_string(category_name)
        articles = Article.get_by_category(category).order_by('-created_at')
        context['category'] = category
        tag = self.request.GET.get('tag')
        if tag:
            articles = articles.filter(tags__name=tag)
        paginator = Paginator(articles, self.article_per_page)
        try:
            context['articles'] = paginator.page(page)
        except EmptyPage:
            context['articles'] = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            context['articles'] = paginator.page(1)
        context['slides'] = None
        return context