from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from ccew.utils import to_titlecase
from documents.models import Charity, CharityFinancialYear, Document, Tag


class ActiveCharityListFilter(admin.SimpleListFilter):
    title = _("active")
    parameter_name = "main"

    def lookups(self, request, model_admin):
        return (
            (1, _("Active")),
            (0, _("Inactive")),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if int(self.value()) == 0:
            return queryset.exclude(date_removed__isnull=True)
        if int(self.value()) == 1:
            return queryset.filter(date_removed__isnull=True)


class CharityFinancialYearAdminList(admin.TabularInline):
    model = CharityFinancialYear
    readonly_fields = (
        "financial_year_end",
        "document_due",
        "document_submitted",
        "income",
        "expenditure",
    )
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class DocumentAdminList(admin.StackedInline):
    model = Document
    extra = 1
    fields = ("file", "tags")


@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    list_display = (
        "charity_name",
        "org_id",
        "date_registered",
        "date_removed",
        "source",
    )
    list_display_links = ("charity_name",)
    list_filter = (
        ActiveCharityListFilter,
        "source",
    )
    ordering = ("org_id",)
    search_fields = (
        "name",
        "org_id",
    )
    inlines = [
        CharityFinancialYearAdminList,
    ]
    readonly_fields = (
        "name",
        "org_id",
        "date_registered",
        "date_removed",
        "source",
    )

    def charity_name(self, instance):
        return to_titlecase(instance.name)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class HasDocumentsListFilter(admin.SimpleListFilter):
    title = _("Has documents")
    parameter_name = "has_docs"

    def lookups(self, request, model_admin):
        return (
            (1, _("Has documents")),
            (0, _("No documents")),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if int(self.value()) == 0:
            return queryset.annotate(document_count=Count("documents")).filter(
                document_count=0
            )
        if int(self.value()) == 1:
            return queryset.annotate(document_count=Count("documents")).filter(
                document_count__gte=1
            )


@admin.register(CharityFinancialYear)
class CharityFinancialYearAdmin(admin.ModelAdmin):
    list_display = (
        "charity_org_id",
        "charity_name",
        "financial_year_end",
        "documents",
    )
    list_display_links = ("charity_name",)
    search_fields = (
        "charity__name",
        "financial_year_end",
    )
    list_filter = (HasDocumentsListFilter,)
    ordering = ("charity__org_id", "financial_year_end")
    raw_id_fields = ("charity",)
    inlines = [
        DocumentAdminList,
    ]
    readonly_fields = (
        "charity",
        "financial_year_end",
        "document_due",
        "document_submitted",
        "income",
        "expenditure",
    )

    def charity_name(self, record):
        return to_titlecase(record.charity.name)

    def charity_org_id(self, record):
        return record.charity.org_id

    def documents(self, record):
        return record.documents.count()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ("financial_year",)
    readonly_fields = ("content", "content_length", "pages", "content_type", "language")
    list_display = (
        "charity_name",
        "charity_org_id",
        "financial_year_end",
        "pages",
        "content_type",
        "content_length",
        "language",
    )
    list_display_links = (
        "charity_name",
        "financial_year_end",
    )
    search_fields = (
        "financial_year__charity__name",
        "financial_year__charity__org_id",
    )

    def charity_name(self, record):
        return to_titlecase(record.financial_year.charity.name)

    def charity_org_id(self, record):
        return record.financial_year.charity.org_id

    def financial_year_end(self, record):
        return record.financial_year.financial_year_end


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "charities_count",
        "documents_count",
    )

    def charities_count(self, instance):
        return instance.charities.count()

    def documents_count(self, instance):
        return instance.documents.count()
