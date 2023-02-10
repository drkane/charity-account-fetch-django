import datetime
import io
import logging

import ocrmypdf
import pdfplumber
from django.conf import settings

from documents.exceptions import DocumentUploadError


def convert_file(source):
    with pdfplumber.open(source) as pdf:
        content = "\n\n".join(
            [
                "<span id='page-{}'></span>\n{}".format(i, p.extract_text())
                for i, p in enumerate(pdf.pages)
                if p.extract_text()
            ]
        )
        if not content:
            raise DocumentUploadError("No content found in PDF")
        return {
            "content": content,
            "content_length": len(content),
            "pages": len(pdf.pages),
            "content_type": "application/pdf",
            "language": "en",
            "date": datetime.datetime.now(),
        }


def do_document_ocr(file):
    try:
        buffer = io.BytesIO()
        ocrmypdf.ocr(file, buffer, **settings.OCRMYPDF_OPTIONS)
        logging.info("OCRing PDF")
        return buffer.getvalue()
    except ocrmypdf.exceptions.PriorOcrFoundError:
        logging.info("PDF already OCR'd")
        return None
    except ocrmypdf.exceptions.EncryptedPdfError:
        logging.info("PDF is encrypted")
        raise
