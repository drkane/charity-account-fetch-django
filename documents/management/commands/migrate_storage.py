import os
import uuid
from django.core.management.base import BaseCommand
from documents.models import Document
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django_q.tasks import async_task
from tqdm import tqdm


def migrate_document(doc):
    org_id = doc.financial_year.charity.org_id.split("-")
    new_filename = "{}-{}/Ends{}/{}-{}.pdf".format(
        org_id[0],
        org_id[1],
        org_id[2][-2:],
        "-".join(org_id),
        doc.financial_year.financial_year_end.strftime("%Y-%m-%d"),
    )
    with open(os.path.join(settings.MEDIA_ROOT, doc.file.name), "rb") as a:
        doc.file.save(
            new_filename,
            File(a),
            save=False,
        )
    doc.file_text.save(
        new_filename.replace(".pdf", ".txt"),
        ContentFile(doc.content.encode("utf-8")),
        save=False,
    )
    Document.objects.filter(id=doc.id).update(
        file=doc.file,
        file_text=doc.file_text,
    )
    return doc


class Command(BaseCommand):
    def handle(self, *args, **options):
        group_id = uuid.uuid4()
        print("Group ID: {}".format(group_id))
        print("Fetching documents...")
        task_count = 0
        for doc in tqdm(Document.objects.filter(file__isnull=False)):
            if doc.file and "data/documents" in doc.file.name:
                async_task(migrate_document, doc)
                task_count += 1
        print("Queued {} tasks".format(task_count))
        print("Group ID: {}".format(group_id))
