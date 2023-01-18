import datetime
from math import ceil

from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.utils.translation import gettext_lazy as _
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Document as DocumentModel


@registry.register_document
class DocumentDocument(Document):

    attachment = fields.ObjectField(
        properties={
            "content": fields.TextField(),
            "content_length": fields.IntegerField(),
            "pages": fields.IntegerField(),
            "content_type": fields.KeywordField(),
            "language": fields.KeywordField(),
            "date": fields.DateField(),
        }
    )
    charity_name = fields.TextField()
    charity_org_id = fields.KeywordField()
    income = fields.IntegerField()
    expenditure = fields.IntegerField()
    financial_year_end = fields.DateField()
    tags = fields.KeywordField()

    def prepare_charity_name(self, instance):
        return instance.financial_year.charity.name

    def prepare_charity_org_id(self, instance):
        return instance.financial_year.charity.org_id

    def prepare_financial_year_end(self, instance):
        return instance.financial_year.financial_year_end

    def prepare_income(self, instance):
        return instance.financial_year.income

    def prepare_expenditure(self, instance):
        return instance.financial_year.expenditure

    def prepare_attachment(self, instance):
        return {
            "content": instance.content,
            "content_length": len(instance.content) if instance.content else 0,
            "pages": instance.pages,
            "content_type": instance.content_type,
            "language": instance.language,
            "date": datetime.datetime.now(),
        }

    def prepare_tags(self, instance):
        return list(
            set(
                list(instance.tags.values_list("name", flat=True))
                + list(
                    instance.financial_year.charity.tags.values_list("name", flat=True)
                )
            )
        )

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        return self.django.model._default_manager.filter(content__isnull=False).filter(
            file__isnull=False
        )

    def should_index_object(self, obj):
        if not obj.content or not obj.file:
            return False
        return True

    class Index:
        name = "documents"
        # See Elasticsearch Indices API reference for available settings
        # settings = {'number_of_shards': 1,
        #             'number_of_replicas': 0}

    class Django:
        model = DocumentModel  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = []

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000


class ElasticsearchPaginator(Paginator):
    """
    Override Django's built-in Paginator class to take in a count/total number of items;
    Elasticsearch provides the total as a part of the query results, so we can minimize hits.
    """

    def __init__(self, *args, params=None, **kwargs):
        super(ElasticsearchPaginator, self).__init__(*args, **kwargs)
        self._params = params
        self.count = None
        self.num_pages = None

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_("That page number is not an integer"))
        if number < 1:
            raise EmptyPage(_("That page number is less than 1"))
        return number

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        return self._get_page(self.object_list[bottom:top], number, self)

    def _get_page(self, object_list, number, paginator):
        if self._params:
            self.result = object_list.execute(params=self._params)
        else:
            self.result = object_list.execute()
        if isinstance(self.result.hits.total, int):
            self.count = self.result.hits.total
        else:
            self.count = int(self.result.hits.total.value)

        if self.count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self.count - self.orphans)
        self.num_pages = ceil(hits / self.per_page)
        return Page(self.result, number, self)
