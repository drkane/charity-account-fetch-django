from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
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


class DocumentAdminList(admin.StackedInline):
    model = Document
    extra = 1
    fields = ("file", "tags")


@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "org_id",
        "date_registered",
        "date_removed",
        "source",
    )
    list_display_links = ("name",)
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
        return record.charity.name

    def charity_org_id(self, record):
        return record.charity.org_id

    def documents(self, record):
        return record.documents.count()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ("financial_year",)
    readonly_fields = ("content", "content_length", "pages")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
