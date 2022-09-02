from collections import Counter
import csv

from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import render, resolve_url, get_object_or_404
from django.utils.text import slugify
from elasticsearch_dsl import A
from elasticsearch_dsl.query import SimpleQueryString, Terms

from documents.models import Tag, Document
from documents.documents import (
    DocumentDocument as DocumentModel,
    ElasticsearchPaginator,
)


def document_search(q=None, tags=None, highlight=True):
    s = DocumentModel.search()
    if q:
        s = s.query(
            SimpleQueryString(
                query=q,
                fields=["attachment.content"],
                default_operator="or",
            )
        ).source(excludes=["attachment.content"])
        if highlight:
            s = s.highlight(
                "attachment.content",
                fragment_size=150,
                number_of_fragments=3,
                pre_tags=['<em class="bg-yellow b highlight">'],
                post_tags=["</em>"],
            )
    if tags:
        s = s.filter("terms", tags=tags)
    return s


def search_csv(request):
    q = request.GET.get("q")
    tags = request.GET.getlist("tag")

    if not q and not tags:
        raise Http404("No search terms or tags provided")

    s = document_search(q, tags, highlight=False)
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="account_search_{slugify(q).replace("-", "_")}.csv"'
        },
    )
    fields = {
        "regno": "charity_org_id",
        "fye": "financial_year_end",
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
            **{k: getattr(result, v, None) for k, v in fields.items() if v is not None},
        }
        writer.writerow(row)
    return response


def search(request, filetype="html"):
    if filetype == "csv":
        return search_csv(request)
    q = request.GET.get("q")
    tags = request.GET.getlist("tag")
    results = {}

    if q or tags:
        s = document_search(q, tags)
        s = s.extra(track_total_hits=True)
        tag_agg = A("terms", field="tags")
        s.aggs.bucket("per_tag", tag_agg)

        page_number = request.GET.get("page")
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


def tag_search(request, tag, filetype="html"):
    tag = get_object_or_404(Tag, slug=Tag._meta.get_field("slug").slugify(tag))
    documents = (
        Document.objects.filter(tags=tag)
        .select_related("financial_year")
        .select_related("financial_year__charity")
        .order_by("financial_year__charity__name", "financial_year__financial_year_end")
        .all()
    )
    q = request.GET.get("q")
    search_terms = {term.strip(): 0 for term in q.split(";")} if q else {}

    document_results = []
    search_results = {}
    with_any_term = set()
    matching_term_count = Counter()
    if search_terms:
        for term in search_terms.keys():
            s = document_search(term, tags=[tag.name], highlight=False)
            s.extra(track_total_hits=True)
            search_results[term] = {result.meta.id: result for result in s.scan()}
            search_terms[term] = len(search_results[term])
            with_any_term.update(search_results[term].keys())

    if filetype == "csv":
        return tag_search_csv(request, documents, search_results, search_terms)

    for document in documents:
        doc_search = {
            term: search_results[term].get(str(document.id))
            for term in search_terms.keys()
        }
        matching_count = sum(1 for result in doc_search.values() if result)
        matching_term_count[matching_count] += 1
        document_results.append(
            {
                "document": document,
                "search": doc_search,
            }
        )

    page_number = request.GET.get("page")
    page_obj = Paginator(document_results, 100).get_page(page_number)
    return render(
        request,
        "tag_search.html.j2",
        {
            "tag": tag,
            "page_obj": page_obj,
            "q": q,
            "search_terms": search_terms,
            "totals": {
                "documents": len(documents),
                "with_any_term": len(with_any_term),
                "matching_term_count": matching_term_count,
            },
            "downloadUrl": resolve_url("doc.tag_search_csv", tag=tag.slug)
            + "?"
            + request.GET.urlencode(),
        },
    )


def tag_search_csv(request, documents, search_results, search_terms):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": "attachment"},
    )
    fields = {
        "regno": "charity_org_id",
        "fye": "financial_year_end",
        "name": "charity_name",
        "income": "income",
        "spending": "expenditure",
        "assets": None,
        **{term: None for term in search_terms.keys()},
    }
    writer = csv.DictWriter(response, fieldnames=fields.keys())
    writer.writeheader()
    for k, document in enumerate(documents):
        row = {
            "regno": document.financial_year.charity.org_id,
            "fye": document.financial_year.financial_year_end,
            "filename": document.file.name,
            "name": document.financial_year.charity.name,
            "income": document.financial_year.income,
            "spending": document.financial_year.expenditure,
            "assets": None,
            **{
                term: search_results[term].get(str(document.id)) is not None
                for term in search_terms.keys()
            },
        }
        writer.writerow(row)
    return response
