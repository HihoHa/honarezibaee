from django.db import models
from m_article.models import Article
from django.core.exceptions import ValidationError

# Create your models here.
class mCookieUser(models.Model):
    user_id = models.CharField(max_length = 1000, unique=True)
    opinions = models.ManyToManyField(Article, through='Opinion')

    def __unicode__(self):
        return self.user_id


class Opinion(models.Model):
    user = models.ForeignKey(mCookieUser)
    article = models.ForeignKey(Article)
    date = models.DateTimeField()
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(unpack_ipv4=True, null=True)

    def clean(self):
        if self.like and self.dislike:
            raise ValidationError('Opinion can not be both like and dislike at the same time.')

    def __unicode__(self):
        return unicode(self.user) + " on " + unicode(self.article)