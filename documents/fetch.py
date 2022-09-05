import io
import logging
import re
from collections import namedtuple
import time

import dateutil.parser
import ocrmypdf
import requests_cache
from django.core.files.base import ContentFile, File
from django.utils import timezone
from requests_html import HTMLSession

from ccew.models import Charity as CCEWCharity
from documents.models import Charity, CharityFinancialYear, Document, Tag
from documents.utils import convert_file

requests_cache.install_cache("demo_cache")


Account = namedtuple("Account", ["url", "fyend", "regno", "size"], defaults=[None])


class CharityFetchError(Exception):
    pass


OCRMYPDF_OPTIONS = dict(
    keep_temporary_files=False,
    optimize=0,
    fast_web_view=0,
)


def fetch_documents_for_charity(
    org_id,
    financial_year_end=None,
    session=None,
    tags=None,
    pause=10,
):

    if session is None:
        session = HTMLSession()

    charity = Charity.objects.get(org_id=org_id)
    logging.info("Fetching documents for {}".format(charity.org_id))

    if financial_year_end == "all":
        financial_years = charity.financial_years.order_by("-financial_year_end")
    elif financial_year_end == "latest":
        financial_years = charity.financial_years.order_by("-financial_year_end")[0:1]
    else:
        financial_years = charity.financial_years.filter(
            financial_year_end=financial_year_end
        )
    financial_years = {f.financial_year_end: f for f in financial_years}

    if not financial_years:
        raise CharityFetchError("No financial years found")
    logging.info(
        "{:,.0f} financial accounts found for {}".format(
            len(financial_years), charity.org_id
        )
    )

    scraper = get_charity_type(charity.org_id)
    accounts = [
        account
        for account in scraper.list_accounts(charity.org_id, session)
        if account.fyend in financial_years.keys()
    ]
    if not accounts:
        raise CharityFetchError("No accounts found")
    logging.info("{:,.0f} accounts found for {}".format(len(accounts), charity.org_id))

    for account in accounts:
        document = fetch_account(
            account, financial_years[account.fyend], session, tags=tags, pause=pause
        )

    return None


def fetch_account(account, financial_year, session=None, tags=None, pause=10):
    if session is None:
        session = HTMLSession()

    # check whether document already exists
    document = Document.objects.filter(financial_year=financial_year).first()
    if document is not None:
        if tags:
            for tag in tags:
                if isinstance(tag, str):
                    tag = Tag.objects.get_or_create(
                        slug=Tag._meta.get_field("slug").slugify(tag)
                    )
                document.tags.add(tag)
        logging.warning(
            "Document already exists for {} {}".format(account.regno, account.fyend)
        )
        return document

    # Get the PDF
    if pause:
        logging.debug("Pausing for {} seconds".format(pause))
        time.sleep(pause)
    logging.debug("Fetching {}".format(account.url))
    r = session.get(account.url)
    pdf_file = ContentFile(r.content, name=f"{account.regno}-{account.fyend}.pdf")
    filedata = convert_file(pdf_file)
    logging.debug(
        "PDF file fetched pages: {:,.0f} size: {:,.0f}".format(
            filedata["pages"], filedata["content_length"]
        )
    )

    # OCR the PDF if necessary
    if filedata["content_length"] < 4000:
        try:
            buffer = io.BytesIO()
            ocrmypdf.ocr(io.BytesIO(r.content), buffer, **OCRMYPDF_OPTIONS)
            logging.info("OCRing PDF")
            pdf_file = ContentFile(
                buffer.getvalue(), name=f"{account.regno}-{account.fyend}.pdf"
            )
            filedata = convert_file(pdf_file)
        except ocrmypdf.exceptions.PriorOcrFoundError:
            logging.info("PDF already OCR'd")
        except ocrmypdf.exceptions.EncryptedPdfError:
            logging.info("PDF is encrypted")

    # Save the PDF to the database
    document = Document(
        financial_year=financial_year,
        file=pdf_file,
        content=filedata["content"],
        content_length=filedata["content_length"],
        pages=filedata["pages"],
        content_type=filedata["content_type"],
        language=filedata["language"],
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    document.save()
    if tags:
        for tag in tags:
            if isinstance(tag, str):
                tag = Tag.objects.get_or_create(
                    slug=Tag._meta.get_field("slug").slugify(tag)
                )
            document.tags.add(tag)
    logging.info("Document created for {} {}".format(account.regno, account.fyend))
    return document


def document_from_file(org_id, financial_year_end, filepath, tags=None):
    charity = Charity.objects.get(org_id=org_id)
    financial_year, _ = CharityFinancialYear.objects.get_or_create(
        charity=charity,
        financial_year_end=financial_year_end,
    )

    # check whether document already exists
    document = Document.objects.filter(financial_year=financial_year).first()
    if document is not None:
        if tags:
            for tag in tags:
                if isinstance(tag, str):
                    tag = Tag.objects.get_or_create(
                        slug=Tag._meta.get_field("slug").slugify(tag)
                    )
                document.tags.add(tag)
        print(
            "Document already exists for {} {}".format(
                charity.org_id, financial_year.financial_year_end
            )
        )
        return document

    # Get the PDF
    pdf_file = ContentFile(
        open(filepath, "rb").read(),
        name=f"{charity.org_id}-{financial_year.financial_year_end}.pdf",
    )
    filedata = convert_file(pdf_file)

    # OCR the PDF if necessary
    if filedata["content_length"] < 4000:
        try:
            buffer = io.BytesIO()
            ocrmypdf.ocr(filepath, buffer, **OCRMYPDF_OPTIONS)
            logging.info("OCRing PDF")
            pdf_file = ContentFile(
                buffer.getvalue(),
                name=f"{charity.org_id}-{financial_year.financial_year_end}.pdf",
            )
            filedata = convert_file(pdf_file)
        except ocrmypdf.exceptions.PriorOcrFoundError:
            logging.info("PDF already OCR'd")
        except ocrmypdf.exceptions.EncryptedPdfError:
            logging.info("PDF is encrypted")

    # Save the PDF to the database
    document = Document(
        financial_year=financial_year,
        file=pdf_file,
        content=filedata["content"],
        content_length=filedata["content_length"],
        pages=filedata["pages"],
        content_type=filedata["content_type"],
        language=filedata["language"],
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    document.save()
    if tags:
        for tag in tags:
            if isinstance(tag, str):
                tag = Tag.objects.get_or_create(
                    slug=Tag._meta.get_field("slug").slugify(tag)
                )
            document.tags.add(tag)
    print("Document created for {} {}".format(org_id, financial_year_end))
    return document


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
