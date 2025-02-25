"""docdisplay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

import documents.views as views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.main.index, name="main.index"),
    path(
        "search/tag/<str:tag>.csv",
        views.search.tag_search,
        name="doc.tag_search_csv",
        kwargs={"filetype": "csv"},
    ),
    path("search/tag/<str:tag>", views.search.tag_search, name="doc.tag_search"),
    path(
        "search.csv",
        views.search.search,
        name="doc.doc_search_csv",
        kwargs={"filetype": "csv"},
    ),
    path("search", views.search.search, name="doc.doc_search"),
    path("doc/bulkupload", views.bulk.doc_upload_bulk, name="doc.doc_upload_bulk"),
    path("doc/<str:id>.pdf", views.doc.doc_get_pdf, name="doc.doc_get_pdf"),
    path("doc/<str:id>/embed", views.doc.doc_get_embed, name="doc.doc_get_embed"),
    path("doc/<str:id>", views.doc.doc_get, name="doc.doc_get"),
    path("charity/search", views.charity.charity_search, name="charity.charity_search"),
    path("charity/<str:regno>", views.charity.charity_get, name="charity.charity_get"),
    path(
        "bulk/list_charities",
        views.bulk.bulk_load_list,
    ),
    path(
        "bulk/record_status/<str:group_id>",
        views.bulk.bulk_record_status,
        name="bulk.bulk_record_status",
    ),
    path(
        "stats",
        views.stats.stats_index,
        name="stats.stats_index",
    ),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html.j2"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(template_name="registration/logged_out.html.j2"),
        name="logout",
    ),
    path("__debug__/", include("debug_toolbar.urls")),
]
