import json

from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.forms.widgets import Select
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, ListView, TemplateView

from accounts.views import AdminRequiredMixin, LoginRequiredMixin
from capturer.models import Variable, NumericalVariable, CategoricalVariable, Category, Template, Case, \
    Algorithm, Question
from capturer.utils import prepare_valid_auth_json
from dashboard.context_processors import get_contract_pk, get_contract
from dashboard.forms import CategoryForm
from polymaze.celery_app import run_algorithm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'


class GenerateCaseView(AdminRequiredMixin, TemplateView):
    template_name = ''

    def get(self, request, *args, **kwargs):
        count = self.request.resolver_match.kwargs.get('count', 1)
        count = int(count)
        pk = 0
        for i in range(0, count):
            template = Template.objects.get(pk=int(kwargs['template_pk']))
            pk = template.pk
            code = template.code.code
            case = Case()
            case.template = template
            variables = {}
            exec code
            case.variables = variables
            case.save()
        return HttpResponseRedirect(reverse('dashboard:cases_list', args=[get_contract_pk(self.request), pk]))


class CategoryFormsMixin(object):
    form_name = None

    def get_queryset(self):
        try:
            contract = get_contract(self.request)
            return contract.template.categories.all()
        except:
            return Category.objects.all()

    def get_success_url(self):
        return reverse_lazy('dashboard:categories_list', args=[get_contract_pk(self.request)])

    def get_context_data(self, **kwargs):
        ctx = super(CategoryFormsMixin, self).get_context_data(**kwargs)
        instance = self.get_object()
        ctx['object'] = instance
        initial_form = CategoryForm(self.request.POST, instance=instance) if self.request.method == 'POST'\
            else CategoryForm(instance=instance)
        try:
            ctx['form'] = initial_form
        except TypeError:
            ctx['form'] = CategoryForm()

        ctx['form'].fields['template'].empty_label = None
        ctx['form'].fields['template'].queryset = Template.objects.filter(pk=instance.template.pk)

        category_cat_vars_names = Variable.objects.filter(categoricalvariable__isnull=False,
                                                          category__template=instance.template,
                                                          category=instance).values_list('name', flat=True)
        ctx['categorical_variables_queryset'] = Variable.objects.filter(
            categoricalvariable__isnull=False, category__template=instance.template).exclude(
            Q(name__in=category_cat_vars_names) & ~Q(category=instance)).order_by('name').distinct('name')
        category_num_vars_names = Variable.objects.filter(numericalvariable__isnull=False,
                                                          category__template=instance.template,
                                                          category=instance).values_list('name', flat=True)
        ctx['numerical_variables_queryset'] = Variable.objects.filter(
            numericalvariable__isnull=False,category__template=instance.template).exclude(
            Q(name__in=category_num_vars_names) & ~Q(category=instance)).order_by('name').distinct('name')
        ctx['form'].fields['parent_category'].queryset = Category.objects.filter(
            template=instance.template, parent_category__isnull=True).exclude(pk=instance.pk)
        category_questions_questions = Question.objects.filter(category__template=instance.template,
                                                               category=instance).values_list('question', flat=True)
        ctx['questions_queryset'] = Question.objects.filter(category__template=instance.template, type='usual').exclude(
            Q(question__in=category_questions_questions) & ~Q(category=instance)
        ).order_by('question').distinct('question')

        # for readonly Template
        if instance.template.readonly:
            for f in ctx['form'].fields:
                if isinstance(ctx['form'].fields[f].widget, Select):
                    ctx['form'].fields[f].widget.attrs['disabled'] = 'disabled'
                else:
                    ctx['form'].fields[f].widget.attrs['readonly'] = 'readonly'

        return ctx


class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'dashboard/categories/list.html'

    def get_queryset(self):
        try:
            contract = get_contract(self.request)
            template_pk = self.request.resolver_match.kwargs.get('template_pk', None)
            if template_pk:
                template = Template.objects.get(pk=template_pk, contract=contract)
                return Category.objects.filter(template=template)
            else:
                return Category.objects.filter(template__in=contract.case_templates.all())
        except:
            return Category.objects.all()


class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    template_name = 'dashboard/categories/details.html'
    form_class = CategoryForm

    def get_success_url(self):
        return reverse_lazy('dashboard:categories_list', args=[get_contract_pk(self.request)])

    def get_context_data(self, **kwargs):
        context = super(CategoryCreateView, self).get_context_data(**kwargs)
        context['new'] = True
        return context

    def get_form(self, form_class):
        form = super(CategoryCreateView, self).get_form(form_class)
        case_templates = get_contract(self.request).case_templates.all() if not self.request.user.is_superuser\
            else Template.objects.all()
        form_templates = [t.id for t in case_templates if not t.readonly]
        form.fields['template'].queryset = case_templates.filter(id__in=form_templates)
        form.fields['template'].empty_label = None
        form.fields['parent_category'].queryset = Category.objects.filter(template__id__in=form_templates,
                                                                          parent_category__isnull=True)
        return form

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
            self.object.save()
            # Automatically create Realism question for new category
            question = Question(category=self.object, type='realism',
                                question='Is this a possible combination of variables?',
                                options={'Possible': 1, 'Outlier': 2, 'Impossible': 0})
            question.save()
            # Automatically create Algorithm for new question
            algo_name = 'Algo for %s question with ID: %d' % (question.type, question.pk)
            algorithm = Algorithm(question=question, name=algo_name)
            algorithm.save()
            if 'submit-form-and-add-another' in request.POST:
                return HttpResponseRedirect(
                    reverse('dashboard:category_create', args=[get_contract_pk(self.request)]))
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.form_invalid(form)


class CategoryView(AdminRequiredMixin, CategoryFormsMixin, DetailView, UpdateView):
    model = Category
    template_name = 'dashboard/categories/details.html'

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = CategoryForm(request.POST, instance=self.get_object())
        if form.is_valid():
            self.form_valid(form)
            # process categorical vars
            categorical_vars_ids = self.object.get_categorical_vars().values_list('id', flat=True)
            new_categorical_vars_ids = [int(x) for x in request.POST.getlist('categorical_variables')]
            deleted_categorical_vars_ids = list(set(categorical_vars_ids) - set(new_categorical_vars_ids))
            added_categorical_vars_ids = list(set(new_categorical_vars_ids) - set(categorical_vars_ids))
            for id in deleted_categorical_vars_ids:
                CategoricalVariable.objects.get(pk=id).delete()
            for id in added_categorical_vars_ids:
                categorical_var = CategoricalVariable.objects.get(pk=id)
                categorical_var.pk = None
                categorical_var.id = None
                categorical_var.category = self.object
                categorical_var.save()
            # process numerical vars
            numerical_vars_ids = self.object.get_numerical_vars().values_list('id', flat=True)
            new_numerical_vars_ids = [int(x) for x in request.POST.getlist('numerical_variables')]
            deleted_numerical_vars_ids = list(set(numerical_vars_ids) - set(new_numerical_vars_ids))
            added_numerical_vars_ids = list(set(new_numerical_vars_ids) - set(numerical_vars_ids))
            for id in deleted_numerical_vars_ids:
                NumericalVariable.objects.get(pk=id).delete()
            for id in added_numerical_vars_ids:
                numerical_var = NumericalVariable.objects.get(pk=id)
                numerical_var.pk = None
                numerical_var.id = None
                numerical_var.category = self.object
                numerical_var.save()
            # process questions
            questions_ids = self.object.get_usual_questions().values_list('id', flat=True)
            new_questions_ids = [int(x) for x in request.POST.getlist('questions')]
            deleted_questions_ids = list(set(questions_ids) - set(new_questions_ids))
            added_questions_ids = list(set(new_questions_ids) - set(questions_ids))
            for id in deleted_questions_ids:
                Question.objects.get(pk=id).delete()
            for id in added_questions_ids:
                question = Question.objects.get(pk=id)
                question.pk = None
                question.category = self.object
                question.save()
                # Automatically create Algorithm for new question
                algo_name = 'Algo for %s question with ID: %d' % (question.type, question.pk)
                algorithm = Algorithm(question=question, name=algo_name)
                algorithm.save()
            if 'submit-form-and-add-another' in request.POST:
                return HttpResponseRedirect(
                    reverse('dashboard:category_create', args=[get_contract_pk(self.request)]))
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.form_invalid(form)


class CategoryDeleteView(AdminRequiredMixin, DeleteView, UpdateView):
    model = Category
    template_name = 'dashboard/categories/delete.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:categories_list', args=[get_contract_pk(self.request)])


@require_POST
def ajax_change_active_contract(request, contract_pk):
    if request.user.is_admin:
        new_contract_pk = request.POST.get('contract_pk', 0)
        if new_contract_pk and request.user.contracts.filter(pk=new_contract_pk):
            request.session['session_contract_pk'] = int(new_contract_pk)
            resp = {'result': 'OK'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    resp = {'result': 'Error'}
    return HttpResponse(json.dumps(resp), content_type="application/json")


def run_algo(request, contract_pk, template_pk, type):
    run_algorithm.delay(template_pk, type)
    return HttpResponseRedirect(reverse_lazy('dashboard:templates_list', args=[get_contract_pk(request)]))


@login_required
def terminal(request):
    valid_json_auth_object = prepare_valid_auth_json(request.user.username)
    return render(
        request,
        'dashboard/terminal.html',
        {'auth_obj': valid_json_auth_object}
    )