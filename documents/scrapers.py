import logging
import re
from collections import namedtuple

import dateutil.parser
from charity_django.ccew.models import Charity as CCEWCharity
from requests_html import HTMLSession

from documents.exceptions import CharityFetchError

Account = namedtuple("Account", ["url", "fyend", "regno", "size"], defaults=[None])


class CCEW:
    name = "ccew"
    url_base = "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/{}/accounts-and-annual-returns"
    date_regex = r"([0-9]{1,2} [A-Za-z]+ [0-9]{4})"

    def _get_regno(self, regno):
        return int(regno.lstrip("GB-CHC-"))

    def get_charity_url(self, regno):
        org_details = CCEWCharity.objects.get(
            registered_charity_number=self._get_regno(regno), linked_charity_number=0
        )
        if not getattr(org_details, "organisation_number", None):
            raise CharityFetchError("Charity {} not found".format(regno))
        return self.url_base.format(org_details.organisation_number)

    def list_accounts(self, regno: str, session=HTMLSession()) -> list:
        """
        List accounts for a charity
        """
        url = self.get_charity_url(regno)
        logging.debug("Fetching account list: {}".format(url))

        r = session.get(url)
        r.raise_for_status()
        accounts = []

        for tr in r.html.find("tr.govuk-table__row"):
            cells = list(tr.find("td"))
            cell_text = [c.text.strip() if c.text else "" for c in cells]
            if not cell_text or "accounts" not in cell_text[0].lower():
                continue
            if not cells[-1].find("a"):
                continue
            date_string = re.match(self.date_regex, cell_text[1])
            if date_string:
                accounts.append(
                    Account(
                        regno=regno,
                        url=cells[-1].find("a", first=True).attrs["href"],
                        fyend=dateutil.parser.parse(date_string.group()).date(),
                    )
                )
        return sorted(accounts, key=lambda x: x.fyend, reverse=True)


class CCNI:
    name = "ccni"
    url_base = (
        "https://www.charitycommissionni.org.uk/charity-details/?regId={}&subId=0"
    )
    date_regex = r"([0-9]{1,2} [A-Za-z]+ [0-9]{4})"
    account_url_regex = r"https://apps.charitycommission.gov.uk/ccni_ar_attachments/([0-9]+)_([0-9]+)_CA.pdf"

    def _get_regno(self, regno):
        return regno.lstrip("GB-NIC-").lstrip("NI")

    def get_charity_url(self, regno):
        return self.url_base.format(self._get_regno(regno))

    def list_accounts(self, regno: str, session=HTMLSession()) -> list:
        """
        List accounts for a charity
        """
        url = self.get_charity_url(regno)
        logging.debug("Fetching account list: {}".format(url))

        r = session.get(url)
        accounts = []
        for link in r.html.find("article#documents a"):
            if not link.attrs["href"].endswith("_CA.pdf"):
                continue
            match = re.match(self.account_url_regex, link.attrs["href"])
            if not match:
                continue
            accounts.append(
                Account(
                    regno=match.group(1).lstrip("0"),
                    url=link.attrs["href"],
                    fyend=dateutil.parser.parse(match.group(2)).date(),
                )
            )
        return sorted(accounts, key=lambda x: x.fyend, reverse=True)


class OSCR:
    name = "oscr"
    url_base = "https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number={}"

    def _get_regno(self, regno):
        return int(regno.lstrip("GB-SC-").lstrip("SC").lstrip("0"))

    def get_charity_url(self, regno):
        return self.url_base.format(self._get_regno(regno))

    def list_accounts(self, regno: str, session=HTMLSession()) -> list:
        """
        List accounts for a charity
        """
        url = self.get_charity_url(regno)
        logging.debug("Fetching account list: {}".format(url))

        r = session.get(url)
        accounts = []
        for tr in r.html.find(".history table tr"):
            cells = tr.find("td")
            try:
                fyend = dateutil.parser.parse(cells[0].text).date()
            except dateutil.parser.ParserError:
                continue
            if len(cells) != 6:
                continue
            links = list(cells[5].absolute_links)
            if not links or links[0] in (
                "https://beta.companieshouse.gov.uk",
                "https://www.gov.uk/government/organisations/charity-commission",
            ):
                continue
            accounts.append(
                Account(
                    regno=regno,
                    url=links[0],
                    fyend=fyend,
                )
            )
        return sorted(accounts, key=lambda x: x.fyend, reverse=True)


def get_charity_type(regno):
    if regno.startswith("SC") or regno.startswith("GB-SC-"):
        return OSCR()
    if regno.startswith("NI") or regno.startswith("GB-NIC-"):
        return CCNI()
    if regno.startswith("GB-CHC-"):
        return CCEW()
    return CCEW()
