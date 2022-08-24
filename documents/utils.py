import datetime

import pdfplumber


class DocumentUploadError(Exception):
    pass


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
