from django.shortcuts import render
from django.views.generic import ListView, DetailView
from jobs.models import Job, JobTag, JobCategory
from m_article.models import Article, ArticleTag, ArticleCategory
from django.http import HttpResponse
from django.core import serializers
import simplejson
import json
from django.http import JsonResponse

class ListJSONViewMixin(object):
    json_fields = []
    many_to_many_fields = []
    foreign_keys = []
    combine = False

    def get(self, request, *args, **kwargs):
        bounds = {arg: self.request.GET.get(arg, None) for arg in ('begin', 'end')}
        bounds = dict((name,int(bound)) if bound else (name, None) for name, bound in bounds.iteritems())
        result = [self.arrange_json(instance) for instance in self.get_queryset()[bounds['begin']:bounds['end']]]
        if self.combine:
            temp = result
            result = []
            for o in temp:
                result += o['word_list']#heavy todo: Clean this!!!!
            result = list(set(result))
        # return HttpResponse(serializers.serialize('json', self.get_queryset()[bounds['begin']:bounds['end']]), content_type="application/json") 
        return JsonResponse(result, safe=False)

    def arrange_json(self, instance):
        """combines fields in self.json_fields and self.many_to_many_fields's and self.foreign_keys pks"""
        json = dict((field, getattr(instance, field)) for field in self.json_fields)
        for many_related_field in self.many_to_many_fields:
            related_list = getattr(instance, many_related_field)#this is a manager (job_instance.tags) but it can be none type
            if related_list:
                json[many_related_field]=[related_object.pk for related_object in related_list.all()]
            else:
                json[many_related_field] = []
        for foreign_key in self.foreign_keys:
            foreign = getattr(instance, foreign_key)
            if foreign:
                json[foreign_key] = foreign.pk
            else:
                json[foreign_key] = None
        return json
   
class ArticleView(ListJSONViewMixin, DetailView):
    queryset = Article.publishable_objects
    json_fields = ['pk', 'title', 'm_content']
    many_to_many_fields = ['tags', 'category']
    foreign_keys = []

class JobView(ListJSONViewMixin, DetailView):
    model = Job
    json_fields = ['title', 'pk', 'm_description', 'm_address', 'email_address']
    many_to_many_fields = ['tags', 'category']
    foreign_keys = []

class ArticleCategoryListView(ListJSONViewMixin, ListView):
    model = ArticleCategory
    json_fields = ['pk', 'name']

class ArticleTagListView(ListJSONViewMixin, ListView):
    model = ArticleTag
    json_fields = ['pk', 'name']

class JobCategoryListView(ListJSONViewMixin, ListView):
    model = JobCategory
    json_fields = ['pk', 'name']

class JobTagListView(ListJSONViewMixin, ListView):
    model = JobTag
    json_fields = ['name', 'pk']

class ArticleByCategoryListView(ListJSONViewMixin, ListView):
    queryset = Article.non_archived_objects
    json_fields = ['pk', 'title', 'm_content']
    many_to_many_fields = ['tags', 'category']
    foreign_keys = []
    
    def get_queryset(self):
        query_set = super(ArticleByCategoryListView, self).get_queryset()
        return query_set.filter(category__pk=self.kwargs['pk'])

class ArticleByTagListView(ListJSONViewMixin, ListView):
    queryset = Article.non_archived_objects
    json_fields = ['pk', 'title', 'm_content']
    many_to_many_fields = ['tags', 'category']
    foreign_keys = []

    def get_queryset(self):
        query_set = super(ArticleByTagListView, self).get_queryset()
        return query_set.filter(tags__pk=self.kwargs['pk'])

class JobByCategoryListView(ListJSONViewMixin, ListView):
    model = Job
    json_fields = ['title', 'pk', 'm_description']
    many_to_many_fields = ['tags', 'category']
    foreign_keys = []

    def get_queryset(self):
        query_set = super(JobByCategoryListView, self).get_queryset()
        return query_set.filter(category__pk=self.kwargs['pk'])

class JobByTagListView(ListJSONViewMixin, ListView):
    model = Job
    json_fields = ['title', 'pk', 'm_description']
    many_to_many_fields = ['tags', 'category']
    foreign_keys = []

    def get_queryset(self):
        query_set = super(JobByTagListView, self).get_queryset()
        return query_set.filter(tags__pk=self.kwargs['pk'])

class JobWordSuggestion(ListJSONViewMixin, ListView):
    model = Job
    json_fields = ['word_list']
    combine = True