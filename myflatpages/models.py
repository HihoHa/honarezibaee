from django.db import models
from django.contrib.flatpages.models import FlatPage


class MyFlatPage(FlatPage):
    description = models.TextField()