from datetime import datetime, date
import re
import urllib.parse
from jinja2 import Environment
from django.urls import reverse, NoReverseMatch
from django.shortcuts import resolve_url
from django.utils.text import slugify
from ccew.utils import to_titlecase


def url_for(
    endpoint, *, _anchor=None, _method=None, _scheme=None, _external=None, **values
):
    if not values:
        return resolve_url(endpoint)
    url = None
    k = None
    values = {k: v for k, v in values.items() if v is not None}
    potential_args = list(values.values())
    for k in range(len(potential_args) + 1):
        try:
            url = reverse(endpoint, args=potential_args[0:k])
            break
        except NoReverseMatch:
            continue
    if k:
        values = dict(list(values.items())[k:])
    if not url:
        return resolve_url(endpoint, kwargs=values)
    if values:
        url += "?" + urllib.parse.urlencode(values)
    return url


def get_flashed_messages(*args, **kwargs):
    return []


def get_now():
    return datetime.now()


def strip_whitespace(text):
    return re.sub(r"(\s)\s+", r"\1", text)


def replace_url_params(url, **kwargs):
    parsed_url = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed_url.query)
    params = {**params, **kwargs}
    return urllib.parse.urlunparse(
        parsed_url._replace(query=urllib.parse.urlencode(params, doseq=True))
    )


def parse_datetime(d, f: str = "%Y-%m-%d", output_format=None) -> date:
    """
    Parse a date from a string
    """
    if isinstance(d, datetime):
        d = d.date()
    elif isinstance(d, date):
        pass
    else:
        d = datetime.strptime(d, f).date()
    if output_format:
        return d.strftime(output_format)
    return d


def dateformat_filter(d, f="%Y-%m-%d", o=None):
    return parse_datetime(d, f, o)


def environment(**options):
    env = Environment(**options)

    env.globals.update(
        {
            "url_for": url_for,
            "get_flashed_messages": get_flashed_messages,
            "now": get_now(),
        }
    )
    env.filters.update(
        {
            "strip_whitespace": strip_whitespace,
            "dateformat": dateformat_filter,
            "replace_url_params": replace_url_params,
            "slugify": slugify,
            "to_titlecase": to_titlecase,
        }
    )
    return env
