from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django_q.monitor import Stat


@login_required
def stats_index(request):
    return render(
        request,
        "stats.html.j2",
        dict(clusters=Stat.get_all()),
    )
