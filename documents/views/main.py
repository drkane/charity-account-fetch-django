from django.shortcuts import render
from elasticsearch_dsl import A

from documents.models import Tag
from documents.documents import DocumentDocument as DocumentModel


def index(request):

    # get count for all tags
    s = DocumentModel.search()
    tag_agg = A("terms", field="tags")
    s.aggs.bucket("per_tag", tag_agg)
    s = s.extra(track_total_hits=True)
    response = s.execute()

    tag_counts = {t.name: t for t in Tag.objects.all()}
    for bucket in response.aggregations.per_tag.buckets:
        tag_counts[bucket.key].doc_count = bucket.doc_count

    return render(
        request,
        "index.html.j2",
        {
            "docs": response.hits.total.value,
            "q": None,
            "tag_counts": sorted(
                tag_counts.values(),
                key=lambda t: getattr(t, "doc_count", 0),
                reverse=True,
            ),
        },
    )
