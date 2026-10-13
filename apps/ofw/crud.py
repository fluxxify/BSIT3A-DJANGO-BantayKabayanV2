"""Generic CRUD engine for the Kabayani Track modules.

Instead of hand-writing near-identical list/save/delete views for every
monitoring module, this engine builds them from the metadata in
``apps.ofw.registry``. It follows the same page + AJAX pattern used by the
original scaffold.
"""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.forms import modelform_factory
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

import datetime

from .registry import get_module, NAV_ORDER

PAGE_SIZE = 10

# Value -> Tabler badge color, used when rendering choice/boolean cells.
TONES = {
    'Active': 'green',
    'On Leave': 'yellow',
    'Repatriated': 'blue',
    'Completed': 'cyan',
    'Deceased': 'red',
    'Unknown': 'secondary',
    'Safe': 'green',
    'Needs Assistance': 'yellow',
    'At Risk': 'red',
    'Unreachable': 'secondary',
    'Open': 'red',
    'In Progress': 'yellow',
    'Resolved': 'green',
    'Closed': 'secondary',
    'Low': 'secondary',
    'Medium': 'yellow',
    'High': 'orange',
    'Critical': 'red',
    'Pending': 'yellow',
    'Accepted': 'blue',
    'Declined': 'red',
    'Scheduled': 'blue',
    'Cancelled': 'secondary',
    'Overdue': 'red',
    'Yes': 'orange',
    'No': 'secondary',
}


def _spec_or_404(module):
    spec = get_module(module)
    if not spec:
        raise Http404(f'Unknown module: {module}')
    return spec


def _build_form(spec):
    """Create a ModelForm with sensible HTML5 widgets for the module."""
    model = spec['model']
    fields = spec['form_fields']

    widgets = {}
    for name in fields:
        field = model._meta.get_field(name)
        if isinstance(field, models.BooleanField):
            widgets[name] = forms.CheckboxInput()
        elif isinstance(field, models.DateField):
            widgets[name] = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        elif isinstance(field, models.TextField):
            widgets[name] = forms.Textarea(attrs={'rows': 3})
        elif isinstance(field, models.EmailField):
            widgets[name] = forms.EmailInput()
        elif isinstance(field, models.URLField):
            widgets[name] = forms.URLInput()
        elif field.is_relation:
            widgets[name] = forms.Select()

    return modelform_factory(model, fields=fields, widgets=widgets)


def _apply_defaults(model, field_names, data):
    """Fill blank default-bearing fields (e.g. dates) so the form validates."""
    for name in field_names:
        field = model._meta.get_field(name)
        if not field.has_default() or data.get(name):
            continue
        default = field.get_default()
        if isinstance(default, datetime.date):
            data[name] = default.isoformat()
        elif default is not None:
            data[name] = default


def _widget_type(form_field):
    widget = form_field.widget
    if isinstance(widget, forms.CheckboxInput):
        return 'checkbox'
    if isinstance(widget, forms.Textarea):
        return 'textarea'
    if isinstance(widget, forms.EmailInput):
        return 'email'
    if isinstance(widget, forms.URLInput):
        return 'url'
    if isinstance(widget, forms.Select):
        return 'select'
    if isinstance(widget, forms.DateInput):
        return 'date'
    return 'text'


def _fields_meta(form):
    """Describe each form field so the template can render it dynamically."""
    metas = []
    for name, form_field in form.base_fields.items():
        meta = {
            'name': name,
            'label': form_field.label or name.replace('_', ' ').title(),
            'required': form_field.required,
            'help_text': form_field.help_text or '',
            'choices': None,
        }
        if isinstance(form_field, forms.ModelChoiceField):
            meta['type'] = 'select'
            meta['choices'] = [(obj.pk, str(obj)) for obj in form_field.queryset]
        elif isinstance(form_field, forms.ChoiceField):
            meta['type'] = 'select'
            meta['choices'] = list(form_field.choices)
        else:
            meta['type'] = _widget_type(form_field)
        metas.append(meta)
    return metas


def _columns_meta(spec):
    model = spec['model']
    columns = []
    for name in spec['table_fields']:
        field = model._meta.get_field(name)
        columns.append({'name': name, 'label': str(field.verbose_name).title()})
    return columns


def _cell(obj, field_name):
    field = obj._meta.get_field(field_name)
    value = getattr(obj, field_name)

    if field.choices:
        display = getattr(obj, f'get_{field_name}_display')()
        return {'text': display, 'tone': TONES.get(display, 'secondary'), 'badge': True}

    if field.is_relation:
        return {'text': str(value) if value else '—', 'badge': False}

    if isinstance(field, models.BooleanField):
        text = 'Yes' if value else 'No'
        return {'text': text, 'tone': TONES.get(text, 'secondary'), 'badge': True}

    if isinstance(field, models.DateField):
        return {'text': value.strftime('%b %d, %Y') if value else '—', 'badge': False}

    if value in (None, ''):
        return {'text': '—', 'badge': False}

    return {'text': str(value), 'badge': False}


def _row(obj, spec):
    return {
        'id': obj.pk,
        'label': str(obj),
        'cells': [_cell(obj, name) for name in spec['table_fields']],
    }


def _first_error(form):
    for field_errors in form.errors.get_json_data().values():
        if field_errors:
            return field_errors[0]['message']
    return 'Please correct the errors below.'


def nav_modules():
    from .registry import MODULES
    return [{'key': key, **MODULES[key]} for key in NAV_ORDER]


@login_required(login_url='login')
def module_list(request, module):
    spec = _spec_or_404(module)
    model = spec['model']
    query = request.GET.get('q', '').strip()

    queryset = model.objects.all()
    if query and spec['search_fields']:
        condition = Q()
        for field_name in spec['search_fields']:
            condition |= Q(**{f'{field_name}__icontains': query})
        queryset = queryset.filter(condition)

    paginator = Paginator(queryset, PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page', 1))

    form = _build_form(spec)()

    return render(request, 'ofw/module.html', {
        'module': module,
        'spec': spec,
        'columns': _columns_meta(spec),
        'rows': [_row(obj, spec) for obj in page],
        'page_obj': page,
        'query': query,
        'fields': _fields_meta(form),
    })


@login_required(login_url='login')
def module_get_ajax(request, module, pk):
    spec = _spec_or_404(module)
    model = spec['model']
    obj = get_object_or_404(model, pk=pk)

    data = {'id': obj.pk}
    for name in spec['form_fields']:
        field = model._meta.get_field(name)
        value = getattr(obj, name)
        if field.is_relation:
            value = getattr(obj, field.attname)
        elif isinstance(field, models.BooleanField):
            value = bool(value)
        elif isinstance(field, models.DateField):
            value = value.isoformat() if value else ''
        elif value is None:
            value = ''
        else:
            value = str(value)
        data[name] = value

    return JsonResponse(data)


@login_required(login_url='login')
@require_POST
def module_save_ajax(request, module):
    spec = _spec_or_404(module)
    model = spec['model']
    form_class = _build_form(spec)

    obj_id = request.POST.get('id')
    if obj_id:
        obj = get_object_or_404(model, pk=obj_id)
        is_update = True
    else:
        obj = model()
        is_update = False

    data = request.POST.copy()
    _apply_defaults(model, spec['form_fields'], data)

    form = form_class(data, instance=obj)
    if not form.is_valid():
        return JsonResponse({'error': _first_error(form)}, status=400)

    obj = form.save(commit=False)
    for field_name in spec['auto_user_fields']:
        if not getattr(obj, field_name, None):
            setattr(obj, field_name, request.user)
    obj.save()

    messages.success(
        request,
        f'{spec["singular"]} has been {"updated" if is_update else "saved"} successfully.',
    )
    return JsonResponse({'status': 'success', 'id': obj.pk})


@login_required(login_url='login')
@require_POST
def module_delete_ajax(request, module, pk):
    spec = _spec_or_404(module)
    obj = get_object_or_404(spec['model'], pk=pk)
    label = str(obj)
    obj.delete()
    messages.success(request, f'{spec["singular"]} "{label}" has been deleted successfully.')
    return JsonResponse({'status': 'deleted'})
