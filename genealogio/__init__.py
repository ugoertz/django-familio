from django_markup.markup import formatter
from .filter.rst_filter import GenRstMarkupFilter


default_app_config = "genealogio.apps.GenealogioConfig"

formatter.register('genrestructuredtext', GenRstMarkupFilter)



