import csv

from django.http import HttpResponse
from django.shortcuts import render, resolve_url
from django.utils.text import slugify
from elasticsearch_dsl import A
from elasticsearch_dsl.query import SimpleQueryString, Terms

from documents.documents import DocumentDocument as DocumentModel
from documents.documents import ElasticsearchPaginator


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
