import json
import os
import random  # need for exec, see method generate_cases in Template

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import model_to_dict
from django.utils.translation import ugettext_lazy as _
from django_pgjson.fields import JsonBField

from accounts.models import User, Contract
from polymaze.fields import PickledObjectField


def check_object_related_template_readonly(instance):
    cls_name = instance.__class__.__name__
    if cls_name == 'Code':
        try:
            if instance.template.first().readonly:
                return True
        except:
            pass
    elif cls_name == 'Template':
        if instance.readonly:
            return True
    elif cls_name == 'Category':
        if instance.template.readonly:
            return True
    elif any(cn == cls_name for cn in ('Variable', 'CategoricalVariable', 'NumericalVariable', 'Question')):
        if instance.category.template.readonly:
            return True

    return False


class TemplateReadonlyMixin(object):
    def save(self, *args, **kwargs):
        if check_object_related_template_readonly(self):
            return
        super(TemplateReadonlyMixin, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if check_object_related_template_readonly(self):
            return
        super(TemplateReadonlyMixin, self).delete(*args, **kwargs)


class Code(TemplateReadonlyMixin, models.Model):
    code = models.TextField()


class Template(TemplateReadonlyMixin, models.Model):
    contract = models.ForeignKey(Contract, related_name='case_templates')
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name='templates',
                                   limit_choices_to={'is_admin': False, 'is_superuser': False}, blank=True)
    last_run = models.DateTimeField(auto_now=True)
    code = models.ForeignKey(Code, related_name='template', null=True, blank=True)
    cron_params = JsonBField(default={'cases': 10})  # amount of cases to generate

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

    @property
    def new_cases(self):
        cases = self.cases.filter(answers=None)
        return cases

    @property
    def readonly(self):
        return True if self.cases.all() else False

    def get_parent_categories(self):
        return self.categories.filter(parent_category__isnull=True)

    def generate_cases(self):
        template = self
        new_cases_ids = []
        count = template.cron_params['cases']
        code = template.code.code
        for i in range(0, count):
            case = Case()
            case.template = template
            exec code
            # variables will come from exec
            case.variables = variables
            case.save()
            new_cases_ids.append(case.id)

        return new_cases_ids


class Category(TemplateReadonlyMixin, models.Model):
    template = models.ForeignKey(Template, related_name='categories')
    name = models.CharField(max_length=255)
    mnemonic_name = models.CharField(max_length=50, blank=True)
    parent_category = models.ForeignKey('self', related_name='child_categories', null=True, blank=True)
    weight = models.IntegerField(default=999)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['pk']

    def __str__(self):
        return self.name

    def get_categorical_vars(self):
        return self.variables.filter(categoricalvariable__isnull=False)

    def get_numerical_vars(self):
        return self.variables.filter(numericalvariable__isnull=False)

    def get_usual_questions(self):
        return self.questions.filter(type='usual')

    def get_realism_question(self):
        try:
            q = Question.objects.filter(type='realism',category=self).first()
        except ObjectDoesNotExist:
            q = None
        return q

    def get_child_categories_recursively(self, ids=None):
        if not ids:
            ids = []
        for c in self.child_categories.all():
            ids.append(c.id)
            c.get_child_categories_recursively(ids)
        return Category.objects.filter(pk__in=ids)

    @property
    def is_parent(self):
        return not self.parent_category


class Variable(TemplateReadonlyMixin, models.Model):
    category = models.ForeignKey(Category, related_name='variables')
    name = models.CharField(max_length=255)
    mnemonic_name = models.CharField(max_length=50, blank=True)
    weight = models.IntegerField(default=999)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        try:
            getattr(self, 'categoricalvariable')
            return '%s | %d options' % (self.name, len(self.categoricalvariable.options))
        except ObjectDoesNotExist:
            return self.name

    @property
    def type(self):
        try:
            getattr(self, 'categoricalvariable')
            return 'categorical'
        except ObjectDoesNotExist:
            return 'numerical'


class CategoricalVariable(Variable):
    options = JsonBField()

    def get_json_options(self):
        return json.dumps(self.options)


class NumericalVariable(Variable):
    generation = JsonBField(blank=True, help_text=_(
                            'Use JSON to pass parameters for case generation: ex. method, mean, range_min, etc.'))


class Question(TemplateReadonlyMixin, models.Model):
    category = models.ForeignKey(Category, related_name='questions')
    TYPE_CHOICES = (
        ('usual', 'Usual'),
        ('realism', 'Realism'),
    )
    type = models.CharField(max_length=20, default='usual', choices=TYPE_CHOICES)
    question = models.CharField(max_length=255)
    mnemonic_name = models.CharField(max_length=50, blank=True)
    options = JsonBField()
    realism_question = models.ForeignKey('self', related_name='main_question', null=True, blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.question


class Case(models.Model):
    template = models.ForeignKey(Template, related_name='cases', null=True, blank=True)
    variables = JsonBField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='cases', blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        if self.template:
            return self.template.name
        else:
            return 'Case without template'

    @property
    def contract(self):
        return self.template.contract

    def get_answers_count(self):
        return self.answers.all().count()

    def get_value_by_var_id(self, var_id):
        for var_dict in self.variables:
            if var_dict['id'] == var_id:
                return var_dict['value']
        return None


class CaseAnswer(models.Model):
    case = models.ForeignKey(Case, related_name='answers')
    answers = JsonBField()
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='case_answers', null=True, blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        if self.case.template:
            return 'Case Answer for %s' % self.case.template.name
        else:
            return 'Case Answer'


class Algorithm(models.Model):
    name = models.CharField(max_length=255)
    question = models.ForeignKey(Question, related_name='algorithms', null=True, blank=True)
    algorithm_object = PickledObjectField(blank=True, null=True)
    last_run = models.DateTimeField(auto_now=True)
    performance = models.DecimalField(max_digits=23, decimal_places=20, blank=True, null=True)
    used_case_answers = ArrayField(models.IntegerField(), blank=True, default=[])  # CaseAnswer

    class Meta:
        ordering = ['pk']


class Metric(models.Model):
    algorithm = models.ForeignKey(Algorithm, related_name='metrics')
    data = JsonBField()
    created = models.DateTimeField(auto_now_add=True)
    used_cases = ArrayField(models.IntegerField())  # Case

    class Meta:
        ordering = ['pk']


class AlgorithmError(models.Model):
    algorithm = models.ForeignKey(Algorithm, related_name='errors')
    data = JsonBField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pk']


class CSVFile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='csv_files', blank=True)
    file = models.FileField(upload_to='csv')
    has_header = models.BooleanField(default=True)
    processed = models.BooleanField(default=False)
    created_cases = ArrayField(models.IntegerField(), blank=True, default=[])  # Case

    class Meta:
        ordering = ['pk']

    def delete(self,*args,**kwargs):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super(CSVFile, self).delete(*args,**kwargs)