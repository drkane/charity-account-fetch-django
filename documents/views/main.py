from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from elasticsearch.exceptions import ConnectionError
from elasticsearch_dsl import A

from documents.documents import DocumentDocument as DocumentModel
from documents.models import Tag


@login_required
def index(request):

    # get count for all tags
    s = DocumentModel.search()
    tag_agg = A("terms", field="tags")
    s.aggs.bucket("per_tag", tag_agg)
    s = s.extra(track_total_hits=True)
    try:
        response = s.execute()
        elasticsearch_working = True
    except ConnectionError:
        response = None
        elasticsearch_working = False

    tag_counts = {t.name: t for t in Tag.objects.all()}
    if response:
        for bucket in response.aggregations.per_tag.buckets:
            tag_counts[bucket.key].doc_count = bucket.doc_count

    return render(
        request,
        "index.html.j2",
        {
            "docs": response.hits.total.value if response else 0,
            "q": None,
            "elasticsearch_working": elasticsearch_working,
            "tag_counts": sorted(
                tag_counts.values(),
                key=lambda t: getattr(t, "doc_count", 0),
                reverse=True,
            ),
        },
    )
