from django.shortcuts import render, get_object_or_404, resolve_url
from django.http import FileResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
import markupsafe
import csv
from django.http import HttpResponse
from django.utils.text import slugify

from documents.documents import (
    DocumentDocument as DocumentModel,
    ElasticsearchPaginator,
)
from documents.models import Document
from elasticsearch_dsl.query import SimpleQueryString, Terms
from elasticsearch_dsl import A


def index(request):
    return render(request, "index.html.j2", {"docs": 100, "q": None})


def search(request, filetype="html"):
    q = request.GET.get("q")
    page_number = request.GET.get("page")
    tags = request.GET.getlist("tag")
    results = {}
    if q:
        s = DocumentModel.search()
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
