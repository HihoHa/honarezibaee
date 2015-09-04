from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, render
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView, ListView
from .forms import JobSearchForm, JobContentForm
from django.db.models import Q
from .models import Job, JobCategory, JobChange, JobContent
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from m_article.models import Article
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required

# Create your views here.


class BaseView(TemplateView):
    template_name = 'jobs/base.html'

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['menuitems'] = JobCategory.get_root_nodes()
        return context


class MapForm(ModelForm):
    class Meta:
        model = Job
        fields = ['location']


class JobView(BaseView):
    template_name = 'jobs/job_detail.html'

    def get_context_data(self, **kwargs):
        context = super(JobView, self).get_context_data(**kwargs)
        job = Job.objects.get(title=self.kwargs['job_name'])
        context['job'] = job
        context['map'] = MapForm(instance=job)
        return context


class JobListViewByCategory(BaseView):
    template_name = 'jobs/job_list.html'
    article_per_page = 3

    def get_context_data(self, **kwargs):
        context = super(JobListViewByCategory, self).get_context_data(**kwargs)
        jobs = Job.get_by_category(self.kwargs['category_name'])
        page = self.request.GET.get('page')
        paginator = Paginator(jobs, self.article_per_page)
        try:
            qs = paginator.page(page)
        except EmptyPage:
            qs = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            qs = paginator.page(1)
        context['jobs'] = qs
        category = JobCategory.objects.get(name=self.kwargs['category_name'])
        context['open_category'] = category.name
        context['parent_category'] = category.get_parent().name if category.get_parent() else None
        return context


class JobSearch(BaseView):
    template_name = 'jobs/job_search.html'
    article_per_page = 3

    def get(self, request, *args, **kwargs):
        if request.GET:
            context = self.get_form_context(request.GET)
            if context:
                return render(request, 'jobs/job_search.html', context)
            else:
                return HttpResponse('ha?')
        else:
            return super(JobSearch, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JobSearch, self).get_context_data(**kwargs)
        # categories = JobCategory.objects.values_list('name', flat=True)
        context['form'] = JobSearchForm()  # category_names=categories)
        return context

    def post(self, request, *args, **kwargs):
        # categories = JobCategory.objects.values_list('name', flat=True)
        context = self.get_form_context(request.POST)
        if context:
            return render_to_response('jobs/search_results.html', context)
            # return HttpResponse('fuck me')
        else:
            return HttpResponse('error')

    def get_form_context(self, data):
        form = JobSearchForm(data)
        if form.is_valid():
            keywords = form.cleaned_data['keywords'].split()
            name = form.cleaned_data['name']
            q = Q()
            for keyword in keywords:
                q |= Q(category__name__contains=keyword) | Q(address__contains=keyword)
            q &= Q(title__contains=name)
            context = self.get_context_data()
            page = form.cleaned_data['page']
            paginator = Paginator(Job.objects.filter(q).distinct(), self.article_per_page)
            try:
                qs = paginator.page(page)
            except EmptyPage:
                qs = paginator.page(paginator.num_pages)
            except PageNotAnInteger:
                qs = paginator.page(1)
            context['job_list'] = qs
            context['keywords'] = form.cleaned_data['keywords']
            context['form'] = form
            return context
        else:
            return None


@login_required(login_url='/login')
def ad_edit(request, *args, **kwargs):
    job = Job.objects.get(pk=kwargs['pk'])
    if not request.user.is_superuser or not request.user == job.author:
        return HttpResponse(status=403,
                            content='you don\'t have permission'
                            'to acess this page')
    context = {}
    context['job'] = job
    job_change, created = JobChange.objects.get_or_create(job=job)
    context['job_change'] = job_change
    if job_change.content:
        content = job_change.content
    else:
        content = JobContent.objects.create()
        job_change.content = content
        job_change.save()
    context['job_change'] = job_change

    if request.method == 'GET':
        context['job_content_form'] = JobContentForm(instance=content)
        return render(request, 'jobs/ad_edit.html', context)

    if request.method == 'POST':
        if request.user.is_superuser:
            pass
        else:  # user is ad user (any user that is not super user)
            pass


@login_required(login_url='/login')
def ad_preview(request, *args, **kwargs):
    pass


@login_required(login_url='/login')
def ad_list(request, *args, **kwargs):
    pass
