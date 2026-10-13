"""Pytest bootstrap.

Workaround for a Python 3.14 incompatibility when running the Django 5.0.14
test runner: ``django.template.context.Context.__copy__`` calls
``copy(super())``, which fails on Python 3.14 during test-client template
instrumentation (``AttributeError: 'super' object has no attribute 'dicts'``).
This file is only imported by pytest, so the patch never affects the running
application.
"""

from django.template.context import Context


def _fixed_context_copy(self):
    duplicate = Context.__new__(Context)
    duplicate.dicts = self.dicts[:]
    duplicate._var_cache = {}
    duplicate._processors = self._processors
    if hasattr(self, '_template_debug'):
        duplicate._template_debug = self._template_debug
    return duplicate


Context.__copy__ = _fixed_context_copy