from django.shortcuts import render
from elasticsearch_dsl import A

from documents.documents import DocumentDocument as DocumentModel


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
