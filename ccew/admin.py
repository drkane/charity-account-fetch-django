from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ccew.models import (
    Charity,
    CharityAnnualReturnHistory,
    CharityAreaOfOperation,
    CharityARPartA,
    CharityARPartB,
    CharityClassification,
    CharityEventHistory,
    CharityGoverningDocument,
    CharityOtherNames,
    CharityOtherRegulators,
    CharityPolicy,
    CharityPublishedReport,
    CharityTrustee,
)


class MainCharityListFilter(admin.SimpleListFilter):
    title = _("main charity")
    parameter_name = "main"

    def lookups(self, request, model_admin):
        return (
            (1, _("Main charity")),
            (0, _("Subsidiary")),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if int(self.value()) == 0:
            return queryset.filter(linked_charity_number__gt=0)
        if int(self.value()) == 1:
            return queryset.filter(linked_charity_number=0)


class CharitySizeListFilter(admin.SimpleListFilter):
    title = _("charity size")
    parameter_name = "size"

    size_bands = (
        (0, -1, 0, _("Zero income")),
        (1, 0, 10_000, _("Under £10,000")),
        (2, 10_000, 100_000, _("£10k - £100k")),
        (3, 100_000, 1_000_000, _("£100k - £1m")),
        (4, 1_000_000, 10_000_000, _("£1m - £10m")),
        (5, 10_000_000, 100_000_000, _("£10m - £100m")),
        (6, 100_000_000, None, _("Over £100m")),
    )

    def lookups(self, request, model_admin):
        return (("unknown", _("Unknown")),) + tuple(
            (str(band[0]), band[3]) for band in self.size_bands
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if self.value() == "unknown":
            return queryset.filter(
                latest_income__isnull=True,
            )
        for band in self.size_bands:
            if self.value() == str(band[0]):
                if band[2] is None:
                    return queryset.filter(latest_income__gte=band[1])
                else:
                    return queryset.filter(latest_income__range=(band[1] + 1, band[2]))


class CharityTabularInline(admin.TabularInline):
    exclude = ("registered_charity_number", "date_of_extract")


class CharityTabularInlineWithLinked(admin.TabularInline):
    exclude = ("registered_charity_number", "linked_charity_number", "date_of_extract")


class CharityOtherNamesInline(CharityTabularInlineWithLinked):
    model = CharityOtherNames


class CharityAnnualReturnHistoryInline(CharityTabularInline):
    model = CharityAnnualReturnHistory


class CharityAreaOfOperationInline(CharityTabularInlineWithLinked):
    model = CharityAreaOfOperation


class CharityARPartAInline(CharityTabularInline):
    model = CharityARPartA


class CharityARPartBInline(CharityTabularInline):
    model = CharityARPartB


class CharityClassificationInline(CharityTabularInlineWithLinked):
    model = CharityClassification


class CharityEventHistoryInline(CharityTabularInlineWithLinked):
    model = CharityEventHistory


class CharityGoverningDocumentInline(CharityTabularInlineWithLinked):
    model = CharityGoverningDocument


class CharityOtherNamesInline(CharityTabularInlineWithLinked):
    model = CharityOtherNames


class CharityOtherRegulatorsInline(CharityTabularInline):
    model = CharityOtherRegulators


class CharityPolicyInline(CharityTabularInlineWithLinked):
    model = CharityPolicy


class CharityPublishedReportInline(CharityTabularInlineWithLinked):
    model = CharityPublishedReport


class CharityTrusteeInline(CharityTabularInlineWithLinked):
    model = CharityTrustee


class CharityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "registered_charity_number",
        "linked_charity_number",
        "charity_registration_status",
        "charity_type",
        "income",
    )
    list_display_links = ("name",)
    list_filter = (
        MainCharityListFilter,
        "charity_registration_status",
        CharitySizeListFilter,
        "charity_type",
    )
    ordering = (
        "registered_charity_number",
        "linked_charity_number",
    )
    search_fields = (
        "charity_name",
        "registered_charity_number",
    )
    inlines = [
        CharityAnnualReturnHistoryInline,
        CharityAreaOfOperationInline,
        CharityARPartAInline,
        CharityARPartBInline,
        CharityClassificationInline,
        CharityEventHistoryInline,
        CharityGoverningDocumentInline,
        CharityOtherNamesInline,
        CharityOtherRegulatorsInline,
        CharityPolicyInline,
        CharityPublishedReportInline,
        CharityTrusteeInline,
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def income(self, obj):
        if obj.latest_income is None:
            return None
        return "£{:,.0f} (FYE {:%b %Y})".format(
            obj.latest_income,
            obj.latest_acc_fin_period_end_date,
        )

    income.admin_order_field = "latest_income"


admin.site.register(Charity, CharityAdmin)
