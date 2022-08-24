import csv
import io

import markupsafe
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, resolve_url
from django.utils.text import slugify
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django_q.tasks import Task, async_task
from elasticsearch_dsl import A
from elasticsearch_dsl.query import SimpleQueryString, Terms

from documents.documents import DocumentDocument as DocumentModel
from documents.documents import ElasticsearchPaginator
from documents.fetch import fetch_documents_for_charity
from documents.models import Charity, CharityFinancialYear, Document, Tag


def index(request):
    s = DocumentModel.search()
    tag_agg = A("terms", field="tags")
    s.aggs.bucket("per_tag", tag_agg)
    s = s.extra(track_total_hits=True)
    response = s.execute()
    tag_counts = response.aggregations.per_tag.buckets
    return render(
        request,
        "index.html.j2",
        {
            "docs": response.hits.total.value,
            "q": None,
            "tag_counts": tag_counts,
        },
    )


def search(request, filetype="html"):
    q = request.GET.get("q")
    page_number = request.GET.get("page")
    tags = request.GET.getlist("tag")
    results = {}
    s = DocumentModel.search()
    if q:
        s = (
            s.query(
                SimpleQueryString(
                    query=q,
                    fields=["attachment.content"],
                    default_operator="or",
                )
            )
            .source(excludes=["attachment.content"])
            .highlight(
                "attachment.content",
                fragment_size=150,
                number_of_fragments=3,
                pre_tags=['<em class="bg-yellow b highlight">'],
                post_tags=["</em>"],
            )
        )
    if tags:
        s = s.filter("terms", tags=tags)

    if q or tags:
        if filetype == "csv":
            response = HttpResponse(
                content_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="account_search_{slugify(q).replace("-", "_")}.csv"'
                },
            )
            fields = {
                "regno": "charity_org_id",
                "fye": "financial_year_end",
                "filename": None,
                "name": "charity_name",
                "income": "income",
                "spending": "expenditure",
                "assets": None,
                "search term": None,
                "tags": "tags",
            }
            writer = csv.DictWriter(response, fieldnames=fields.keys())
            writer.writeheader()
            for k, result in enumerate(s.scan()):
                row = {
                    "search term": q,
                    **{
                        k: getattr(result, v, None)
                        for k, v in fields.items()
                        if v is not None
                    },
                }
                writer.writerow(row)
            return response

        s = s.extra(track_total_hits=True)
        tag_agg = A("terms", field="tags")
        s.aggs.bucket("per_tag", tag_agg)

        result_page = ElasticsearchPaginator(s, 100).get_page(page_number)
        results = {
            "page_obj": result_page,
            "tag_counts": result_page.paginator.result.aggs.per_tag.buckets,
            "q": q,
            "tags": tags,
            "downloadUrl": resolve_url("doc.doc_search_csv")
            + "?"
            + request.GET.urlencode(),
        }

    return render(
        request,
        "doc_search.html.j2",
        results,
    )


def doc_get(request, id):
    doc_highlight = get_doc(id, request.GET.get("q"))
    doc = get_object_or_404(Document, id=id)
    return render(
        request,
        "doc_display.html.j2",
        {
            "result": doc,
            "highlight": request.GET.get("q"),
            "highlight_count": doc_highlight.get("_highlight_count", 0),
        },
    )


@xframe_options_sameorigin
def doc_get_embed(request, id):
    doc_highlight = get_doc(id, request.GET.get("q"))
    doc = get_object_or_404(Document, id=id)
    return render(
        request,
        "doc_display_embed.html.j2",
        {
            "content": doc_highlight.get("_highlight", doc.content),
            "highlight": request.GET.get("q"),
            "highlight_count": doc_highlight.get("_highlight_count", 0),
        },
    )


@xframe_options_sameorigin
def doc_get_pdf(request, id):
    doc = get_object_or_404(Document, id=id)
    return FileResponse(doc.file.open("rb"))


def get_doc(id, q=None):
    highlight_class = 'data-charity-account-highlight="true"'
    s = DocumentModel.search()
    s = s.query(
        Terms(
            _id=[id],
        )
    ).source(excludes=["attachment.content"])
    if q:
        s = s.highlight(
            "attachment.content",
            fragment_size=150,
            number_of_fragments=0,
            pre_tags=[f'<em class="bg-yellow b highlight" {highlight_class}>'],
            post_tags=["</em>"],
            highlight_query=SimpleQueryString(
                query=q,
                fields=["attachment.content"],
                default_operator="or",
            ),
        )
    response = s.execute()
    if len(response.hits) == 1:
        result = {
            "id": response.hits[0].meta.id,
        }
        if getattr(response.hits[0].meta, "highlight", {"attachment.content": None})[
            "attachment.content"
        ]:
            result["_highlight_count"] = markupsafe.Markup(
                response.hits[0].meta.highlight["attachment.content"]
            ).count(highlight_class)
            result["_highlight"] = response.hits[0].meta.highlight[
                "attachment.content"
            ][0]
        return result
    return {}


def doc_upload_bulk(request):
    return render(request, "doc_upload_bulk.html.j2")


def charity_search(request):
    q = request.GET.get("q")
    vector = SearchVector("name")
    search_query = SearchQuery(q)
    query = (
        Charity.objects.annotate(
            search=vector,
        )
        .filter(search=search_query)
        .annotate(rank=SearchRank(vector, search_query))
        .order_by("-rank")
    )
    paginator = Paginator(query, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "charity_search.html.j2", {"page_obj": page_obj, "q": q})


def charity_get(request, regno, filetype="html"):
    charity = get_object_or_404(Charity, org_id=regno)
    if filetype == "json":
        return JsonResponse(
            {
                "data": {
                    "results": {},
                    "charity": {
                        "name": charity.name,
                        "finances": [
                            {
                                "fyend": fy.financial_year_end,
                                "income": fy.income,
                                "expenditure": fy.expenditure,
                                "documents": [
                                    {
                                        "id": doc.id,
                                        "pages": doc.pages,
                                        "content_type": doc.content_type,
                                    }
                                    for doc in fy.documents.all()
                                ],
                                "task_id": fy.task_id,
                            }
                            for fy in charity.financial_years.order_by(
                                "-financial_year_end"
                            ).all()
                        ],
                    },
                    "regno": regno,
                }
            }
        )
    return render(
        request,
        "charity.html.j2",
        {"charity": charity, "filetype": filetype},
    )


def task_fetch_accounts(request, org_id, fyend):
    charity = get_object_or_404(Charity, org_id=org_id)
    charity_financial_year = get_object_or_404(
        CharityFinancialYear, charity=charity, financial_year_end=fyend
    )
    task_id = async_task(
        fetch_documents_for_charity,
        charity_financial_year.charity.org_id,
        charity_financial_year.financial_year_end,
    )
    charity_financial_year.task_id = task_id
    charity_financial_year.save()
    return JsonResponse({"task_id": task_id})


def task_get_status(request, task_id):
    task = Task.get_task(task_id)
    return JsonResponse({"task": task})


def get_record(record: CharityFinancialYear, request):
    documents = list(record.documents.all())
    tags = []
    if request.POST.get("tags"):
        request_tags = request.POST.get("tags").split(",")
        for tag in request_tags:
            tag_object, _ = Tag.objects.get_or_create(name=tag)
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


def bulk_record_status(request, fy_id):
    fy = get_object_or_404(CharityFinancialYear, id=fy_id)
    return render(
        request,
        "_record_status.html.j2",
        {"fy": get_record(fy, request)},
    )
