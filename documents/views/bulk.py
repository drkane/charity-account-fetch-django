import csv
import io

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, resolve_url
from django_htmx.http import HttpResponseClientRedirect
from django_q.tasks import Task, async_task

from documents.fetch import fetch_documents_for_charity
from documents.models import Charity, CharityFinancialYear, FetchGroup, Tag


@login_required
@permission_required("documents.add_document")
def doc_upload_bulk(request):
    return render(request, "doc_upload_bulk.html.j2")


def get_record(
    record: CharityFinancialYear, tags=None, fetch_documents=None, task_group=None
):
    documents = list(record.documents.all())
    if tags:
        for tag in tags:
            for doc in documents:
                doc.tags.add(tag)
                doc.save()

    if fetch_documents:
        if not documents:
            task_id = async_task(
                fetch_documents_for_charity,
                record.charity.org_id,
                record.financial_year_end,
                tags=tags,
                group=task_group.id if task_group else None,
            )
            print("Starting task", task_id)
            record.task_id = task_id
            record.task_groups.add(task_group)
            record.save()
            task_group.task_count += 1
            task_group.save()

    return {
        "org_id": record.charity.org_id,
        "fyend": record.financial_year_end,
        "status": get_status(record, documents),
        "error": None,
        "charity": record.charity,
        "fy": record,
        "documents": documents,
    }


def get_record_meta(request):
    record_meta = {"tags": [], "fetch_documents": False, "task_group": None}
    if request.POST.get("tags"):
        for tag in request.POST.get("tags", "").split(","):
            tag_object, _ = Tag.objects.get_or_create(
                slug=Tag._meta.get_field("slug").slugify(tag), defaults=dict(name=tag)
            )
            print(tag_object)
            record_meta["tags"].append(tag_object)
    record_meta["fetch_documents"] = request.POST.get("action") == "Fetch Documents"
    if record_meta["fetch_documents"]:
        task_group = FetchGroup.objects.create()
        record_meta["task_group"] = task_group
    return record_meta


def get_status(record: CharityFinancialYear, documents):
    # record has at least one document
    if len(documents) > 0:
        return "Document available"

    if record.task_id:
        task = Task.get_task(record.task_id)
        if not task:
            return "Document being fetched"
        if not task.success:
            return "Document fetch failed"
        return "Document available"

    return "Available to fetch"


@login_required
@permission_required("documents.add_document")
def bulk_load_list(request):
    charity_list = io.StringIO(request.POST.get("list"))
    source = "textarea"
    reader = csv.reader(charity_list)
    default_fye = "latest"
    records = []
    record_meta = get_record_meta(request)

    for row in reader:
        fyend = default_fye
        if len(row) == 2:
            org_id = row[0]
            if row[1]:
                fyend = row[1]
        elif row[0]:
            org_id = row[0]
        else:
            continue
        try:
            charity = Charity.objects.get(org_id=org_id)
        except Charity.DoesNotExist:
            records.append(
                {
                    "org_id": org_id,
                    "fyend": fyend,
                    "error": "Charity not found",
                    "status": "Error",
                    "charity": None,
                    "fy": None,
                    "documents": None,
                }
            )
            continue
        if fyend == "all":
            records.extend(
                [get_record(fy, **record_meta) for fy in charity.financial_years.all()]
            )
        elif fyend == "latest":
            fy = charity.financial_years.order_by("-financial_year_end").first()
            records.append(get_record(fy, **record_meta))
        else:
            fy = charity.financial_years.filter(financial_year_end=fyend).first()
            records.append(get_record(fy, **record_meta))

    if record_meta.get("task_group"):
        return HttpResponseClientRedirect(
            resolve_url(
                "bulk.bulk_record_status", group_id=record_meta["task_group"].id
            )
        )

    return render(
        request,
        "bulk_load_list.html.j2",
        {
            "records": records,
            "source": source,
            "record_meta": record_meta,
        },
    )


@login_required
@permission_required("documents.add_document")
def bulk_record_status(request, group_id):
    group = get_object_or_404(FetchGroup, id=group_id)
    group.update_task_group()

    return render(
        request,
        "bulk_load_list_results.html.j2",
        {
            "base_template": "_partial.html.j2" if request.htmx else "base.html.j2",
            "group": group,
        },
    )
