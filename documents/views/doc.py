import re

import markupsafe
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from elastic_transport import ConnectionError
from elasticsearch_dsl.query import SimpleQueryString, Terms

from documents.documents import DocumentDocument as DocumentModel
from documents.models import Document

REGNO_REGEX = re.compile(
    r"(?P<regno>GB-(CHC|NI|SC|COH)-[SC0-9]+)-(?P<fyend>\d{4}-\d{2}-\d{2})"
)


@login_required
def doc_get(request, id):
    doc = get_doc(id)
    doc_highlight = get_doc_highlight(doc.id, request.GET.get("q"))

    return render(
        request,
        "doc_display.html.j2",
        {
            "result": doc,
            "highlight": request.GET.get("q"),
            "highlight_count": doc_highlight.get("_highlight_count", 0),
        },
    )


@login_required
@xframe_options_sameorigin
def doc_get_embed(request, id):
    doc = get_doc(id)
    doc_highlight = get_doc_highlight(id, request.GET.get("q"))
    return render(
        request,
        "doc_display_embed.html.j2",
        {
            "content": doc_highlight.get("_highlight", doc.content),
            "highlight": request.GET.get("q"),
            "highlight_count": doc_highlight.get("_highlight_count", 0),
        },
    )


@login_required
@xframe_options_sameorigin
def doc_get_pdf(request, id):
    doc = get_doc(id)
    if doc.file:
        return FileResponse(doc.file.open("rb"))
    raise Http404("No PDF available")


def get_doc(id):
    match = REGNO_REGEX.match(id)
    if match:
        return get_object_or_404(
            Document,
            financial_year__charity__org_id=match.group("regno"),
            financial_year__financial_year_end=match.group("fyend"),
        )
    elif id.isdigit():
        return get_object_or_404(Document, id=int(id))

    raise Http404(f"Document '{id}' not found")


def get_doc_highlight(id, q=None):
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
    try:
        response = s.execute()
    except ConnectionError:
        return {}
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
