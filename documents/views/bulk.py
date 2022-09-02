import csv
import io

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render
from django_q.tasks import Task, async_task

from documents.fetch import fetch_documents_for_charity
from documents.models import Charity, CharityFinancialYear, Tag


@login_required
@permission_required("documents.add_document")
def doc_upload_bulk(request):
    return render(request, "doc_upload_bulk.html.j2")


def get_record(record: CharityFinancialYear, request):
    documents = list(record.documents.all())
    tags = []
    if request.POST.get("tags"):
        request_tags = request.POST.get("tags").split(",")
        for tag in request_tags:
            tag_object, _ = Tag.objects.get_or_create(
                slug=Tag._meta.get_field("slug").slugify(tag), defaults=dict(name=tag)
            )
            tags.append(tag_object)
            for doc in documents:
                doc.tags.add(tag_object)
                doc.save()

    if request.POST.get("action") == "Fetch Documents":
        if not documents:
            task_id = async_task(
                fetch_documents_for_charity,
                record.charity.org_id,
                record.financial_year_end,
                tags=tags,
            )
            print("Starting task", task_id)
            record.task_id = task_id
            record.save()

    return {
        "org_id": record.charity.org_id,
        "fyend": record.financial_year_end,
        "status": get_status(record, documents),
        "error": None,
        "charity": record.charity,
        "fy": record,
        "documents": documents,
    }


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
    for row in reader:
        fyend = default_fye
        if len(row) == 2:
            org_id = row[0]
            if row[1]:
                fyend = row[1]
        else:
            org_id = row[0]
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
                [get_record(fy, request) for fy in charity.financial_years.all()]
            )
        elif fyend == "latest":
            fy = charity.financial_years.order_by("-financial_year_end").first()
            records.append(get_record(fy, request))
        else:
            fy = charity.financial_years.filter(financial_year_end=fyend).first()
            records.append(get_record(fy, request))

    return render(
        request,
        "bulk_load_list.html.j2",
        {
            "records": records,
            "source": source,
        },
    )


@login_required
@permission_required("documents.add_document")
def bulk_record_status(request, fy_id):
    fy = get_object_or_404(CharityFinancialYear, id=fy_id)
    return render(
        request,
        "_record_status.html.j2",
        {"fy": get_record(fy, request)},
    )
