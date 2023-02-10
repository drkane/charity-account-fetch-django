import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Min, Q
from django.shortcuts import render
from django.utils import timezone
from django_q.models import Failure, OrmQ, Schedule, Success
from django_q.monitor import Stat

from documents.models import CharityFinancialYear, Document, DocumentStatus


@login_required
def stats_index(request):

    today = timezone.now().date()

    income_bands = [
        # ("under_25k", 0, 25_000),
        ("25k_to_100k", 25_000, 100_000),
        ("100k_to_1m", 100_000, 1_000_000),
        ("1m_to_10m", 1_000_000, 10_000_000),
        ("over_10m", 10_000_000, 100_000_000_000),
    ]

    financial_years = CharityFinancialYear.objects.values(
        "financial_year_end__year"
    ).annotate(
        rows=Count("id"),
        eligible_rows=Count("id", filter=Q(income__gt=25_000)),
        success=Count("id", filter=Q(status=DocumentStatus.SUCCESS)),
        failed=Count("id", filter=Q(status=DocumentStatus.FAILED)),
        attempted=Count("id", filter=Q(status=DocumentStatus.PENDING)),
        **{
            "income_{}_eligible".format(band[0]): Count(
                "id", filter=Q(income__gte=band[1], income__lt=band[2])
            )
            for band in income_bands
        },
        **{
            "income_{}_success".format(band[0]): Count(
                "id",
                filter=Q(
                    status=DocumentStatus.SUCCESS,
                    income__gte=band[1],
                    income__lt=band[2],
                ),
            )
            for band in income_bands
        },
    )
    financial_years = [
        fy for fy in financial_years if fy["financial_year_end__year"] > 2013
    ]
    financial_years.append(
        {
            **{
                k: sum((fy[k] or 0) for fy in financial_years)
                for k in financial_years[0].keys()
            },
            "financial_year_end__year": "Total",
        }
    )

    financial_years = [
        {
            "Year": fy["financial_year_end__year"],
            "Accounts": fy["rows"],
            "Eligible Accounts": fy["eligible_rows"],
            "Successfully fetched": fy["success"],
            "Failed": fy["failed"],
            "Attempted": fy["attempted"],
            "Success %": fy["success"] / fy["rows"],
            **{
                "{} success %".format(band[0].replace("_", " ")): (
                    fy["income_{}_success".format(band[0])]
                    / fy["income_{}_eligible".format(band[0])]
                )
                if fy["income_{}_eligible".format(band[0])]
                else None
                for band in income_bands
            },
        }
        for fy in financial_years
    ]

    days_ago_14 = today - datetime.timedelta(days=14)
    recently_fetched = (
        Document.objects.filter(created_at__date__gte=days_ago_14)
        .values("created_at__date")
        .annotate(
            documents=Count("id"),
            has_content=Count("id", filter=Q(content__isnull=False)),
            has_file=Count("id", filter=Q(file__isnull=False)),
            earliest_fy=Min(
                "financial_year__financial_year_end", filter=Q(content__isnull=False)
            ),
            latest_fy=Max(
                "financial_year__financial_year_end", filter=Q(content__isnull=False)
            ),
            biggest=Max("financial_year__income", filter=Q(content__isnull=False)),
            smallest=Min("financial_year__income", filter=Q(content__isnull=False)),
        )
    )
    # failed tasks by date
    failures = {
        f["started__date"]: f["failed_tasks"]
        for f in Failure.objects.filter(started__date__gte=days_ago_14)
        .values("started__date")
        .annotate(
            failed_tasks=Count("id"),
        )
    }

    recently_fetched = sorted(
        [
            {
                "Date": d["created_at__date"],
                "Documents fetched": d["documents"],
                "Has content": d["has_content"],
                "Has file": d["has_file"],
                "Earliest FYE": d["earliest_fy"],
                "Latest FYE": d["latest_fy"],
                "Largest income": d["biggest"],
                "Smallest income": d["smallest"],
                "With content %": d["has_content"] / d["documents"],
                "With file %": d["has_file"] / d["documents"],
                "Failed tasks": failures.get(d["created_at__date"], 0),
            }
            for d in recently_fetched
        ],
        key=lambda d: d["Date"],
    )[::-1]

    return render(
        request,
        "stats.html.j2",
        dict(
            clusters=Stat.get_all(),
            fyears=financial_years,
            recently_fetched=recently_fetched,
            queue_stats={
                "in_queue": Schedule.objects.count(),
                "in_queue_today": Schedule.objects.filter(next_run__date=today).count(),
                "failed": Failure.objects.filter(stopped__date=today).count(),
                "success": Success.objects.count(),
            },
        ),
    )
