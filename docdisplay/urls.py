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
from django.urls import path
import documents.views as main_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", main_views.index, name="main.index"),
    path("search", main_views.search, name="doc.doc_search"),
    path(
        "search.csv",
        main_views.search,
        name="doc.doc_search_csv",
        kwargs={"filetype": "csv"},
    ),
    path("doc/<int:id>", main_views.doc_get, name="doc.doc_get"),
    path("doc/<int:id>/embed", main_views.doc_get_embed, name="doc.doc_get_embed"),
    path("doc/<int:id>.pdf", main_views.doc_get_pdf, name="doc.doc_get_pdf"),
    path("charity/search", main_views.charity_search, name="charity.charity_search"),
    path("charity/<str:regno>", main_views.charity_get, name="charity.charity_get"),
]
