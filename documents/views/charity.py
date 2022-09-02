from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from documents.models import Charity


@login_required
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


@login_required
def charity_get(request, regno, filetype="html"):
    charity = get_object_or_404(Charity, org_id=regno)
    return render(
        request,
        "charity.html.j2",
        {"charity": charity, "filetype": filetype},
    )
