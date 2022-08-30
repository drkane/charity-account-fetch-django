from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ccni.models import Charity


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
                total_income__isnull=True,
            )
        for band in self.size_bands:
            if self.value() == str(band[0]):
                if band[2] is None:
                    return queryset.filter(total_income__gte=band[1])
                else:
                    return queryset.filter(total_income__range=(band[1] + 1, band[2]))


class CharityAdmin(admin.ModelAdmin):
    list_display = (
        "charity_name",
        "reg_charity_number",
        "status",
    )
    list_display_links = ("charity_name",)
    list_filter = (
        "status",
        CharitySizeListFilter,
    )
    ordering = ("reg_charity_number",)
    search_fields = (
        "charity_name",
        "reg_charity_number",
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def income(self, obj):
        if obj.total_income is None:
            return None
        return "£{:,.0f} (FYE {:%b %Y})".format(
            obj.total_income,
            obj.date_for_financial_year_ending,
        )

    income.admin_order_field = "total_income"


admin.site.register(Charity, CharityAdmin)
