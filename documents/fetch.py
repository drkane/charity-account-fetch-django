import logging
import time

import requests_cache
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from pdfminer.pdfparser import PDFSyntaxError
from requests_html import HTMLSession

from documents.exceptions import CharityFetchError, DocAlreadyExists
from documents.models import (
    Charity,
    CharityFinancialYear,
    Document,
    DocumentStatus,
    Tag,
)
from documents.scrapers import get_charity_type
from documents.utils import convert_file, do_document_ocr

requests_cache.install_cache("demo_cache")


def get_document(financial_year, tags=None, fail_if_exists=True):
    document, created = Document.objects.get_or_create(
        financial_year=financial_year,
        defaults={
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        },
    )
    if tags:
        for tag in tags:
            if isinstance(tag, str):
                tag, _ = Tag.objects.get_or_create(
                    slug=Tag._meta.get_field("slug").slugify(tag)
                )
            document.tags.add(tag)

    if not created and document.file:
        if fail_if_exists:
            raise DocAlreadyExists(
                "Document already exists for {} {}".format(
                    financial_year.charity.org_id,
                    financial_year.financial_year_end,
                )
            )
        else:
            logging.info(
                "Document already exists for {} {} - replacing with new document".format(
                    financial_year.charity.org_id,
                    financial_year.financial_year_end,
                )
            )
    return document


def fetch_documents_for_charity(
    org_id,
    financial_year_end=None,
    session=None,
    tags=None,
    pause=10,
    fail_if_exists=True,
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
        "{:,.0f} financial accounts found for {} ({})".format(
            len(financial_years), charity.org_id, financial_year_end
        )
    )

    scraper = get_charity_type(charity.org_id)
    accounts = [
        account
        for account in scraper.list_accounts(charity.org_id, session)
        if account.fyend in financial_years.keys()
    ]
    if not accounts:
        for financial_year in financial_years.values():
            financial_year.status = DocumentStatus.FAILED
            financial_year.status_notes = "Accounts not found"
            financial_year.save()
        return []
    logging.info(
        "{:,.0f} accounts found for {} ({})".format(
            len(accounts), charity.org_id, financial_year_end
        )
    )

    documents = []
    for account in accounts:
        financial_year = financial_years[account.fyend]
        try:
            documents.append(
                fetch_account(
                    account,
                    financial_year,
                    session,
                    tags=tags,
                    pause=pause,
                    fail_if_exists=fail_if_exists,
                )
            )

            financial_year.status = DocumentStatus.SUCCESS
            financial_year.save()

        except Exception as e:
            financial_year.status = DocumentStatus.FAILED
            financial_year.status_notes = str(e)
            financial_year.save()
            logging.error(e)
            continue

    return documents


def fetch_account(
    account, financial_year, session=None, tags=None, pause=10, fail_if_exists=True
):
    if session is None:
        session = HTMLSession()

    # get the document (fails after saving the tags if the document already exists)
    document, created = Document.objects.get_or_create(
        financial_year=financial_year,
        defaults={
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        },
    )

    # add tags to the document
    if tags:
        for tag in tags:
            if isinstance(tag, str):
                tag, _ = Tag.objects.get_or_create(
                    slug=Tag._meta.get_field("slug").slugify(tag)
                )
            document.tags.add(tag)

    # if the document already exists, return it
    if not created and document.file and fail_if_exists:
        logging.info(
            "Document already exists for {} {} - replacing with new document".format(
                financial_year.charity.org_id,
                financial_year.financial_year_end,
            )
        )
        return document

    # if we're fetching the document then update the status
    financial_year.status = DocumentStatus.PENDING
    financial_year.last_document_fetch_started = timezone.now()
    financial_year.save()

    # Get the PDF
    logging.info("Fetching {}".format(account.url))
    try:
        r = session.get(account.url)
        r.raise_for_status()
    except Exception as e:
        raise CharityFetchError(e)

    # Pause to save the server
    if pause:
        logging.info("Pausing for {} seconds".format(pause))
        time.sleep(pause)
    pdf_file = ContentFile(r.content, name=financial_year.document_filename)

    # Save the PDF to the database
    logging.info("Saving PDF file {}".format(financial_year.document_filename))
    document.file = pdf_file
    document.save()

    # Convert the PDF to text
    logging.info(
        "Getting text from PDF file {}".format(financial_year.document_filename)
    )
    filedata = convert_file(pdf_file)
    document.content = filedata["content"]
    document.file_text = ContentFile(
        filedata["content"].encode("utf-8"),
        name=financial_year.document_filename.replace(".pdf", ".txt"),
    )
    document.content_length = filedata["content_length"]
    document.pages = filedata["pages"]
    document.content_type = filedata["content_type"]
    document.language = filedata["language"]
    document.save()
    logging.info(
        "PDF file fetched pages: {:,.0f} size: {:,.0f}".format(
            document.pages, document.content_length
        )
    )

    # if there's no content then try and OCR the PDF
    if document.content_length < settings.MIN_DOC_LENGTH:
        new_file = do_document_ocr(document.file)
        if new_file:
            new_file = ContentFile(new_file, name=financial_year.document_filename)
            document.file = new_file
            document.save()
            filedata = convert_file(new_file)
            document.content = filedata["content"]
            document.file_text = ContentFile(
                filedata["content"].encode("utf-8"),
                name=financial_year.document_filename.replace("pdf", "txt"),
            )
            document.content_length = filedata["content_length"]
            document.pages = filedata["pages"]
            document.content_type = filedata["content_type"]
            document.language = filedata["language"]
            document.save()
            logging.info(
                "PDF file OCR pages: {:,.0f} size: {:,.0f}".format(
                    document.pages, document.content_length
                )
            )

    logging.info(
        "Document {} created for {} {}".format(
            document.id, account.regno, account.fyend
        )
    )

    return document


def document_from_file(org_id, financial_year_end, filepath, tags=None):
    charity = Charity.objects.get(org_id=org_id)
    financial_year, _ = CharityFinancialYear.objects.get_or_create(
        charity=charity,
        financial_year_end=financial_year_end,
    )

    # get the document (fails after saving the tags if the document already exists)
    document = get_document(financial_year, tags=tags)

    # Get the PDF
    pdf_file = ContentFile(
        open(filepath, "rb").read(),
        name=f"{charity.org_id}-{financial_year.financial_year_end}.pdf",
    )

    # Save the PDF to the database
    document.file = pdf_file
    document.save()

    print("Document created for {} {}".format(org_id, financial_year_end))
    return document
