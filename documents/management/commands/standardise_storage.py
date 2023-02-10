import os
import re
import uuid

from boto3 import session
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django_q.tasks import async_task
from tqdm import tqdm

from documents.models import CharityFinancialYear, Document, DocumentStatus

# <orgid eg GB-CHC-1234567ABDCD>-<year>-<month>-<day>.pdf
FILENAME_REGEX = re.compile(
    r"(?P<org_id>GB-(CHC|SC|NIC|COH)-[\w]+)-(?P<date>\d{4}-\d{2}-\d{2}).pdf"
)


def get_orgid_and_date(filename):
    match = FILENAME_REGEX.search(filename)
    if match:
        return match.group("org_id"), match.group("date")
    else:
        return None, None


def get_new_filename(org_id, date):
    org_id = org_id.split("-")
    return "accounts/pdf/{}-{}/Ends{}/{}-{}.pdf".format(
        org_id[0],
        org_id[1],
        org_id[2][-2:],
        "-".join(org_id),
        date,
    )


class Command(BaseCommand):
    def handle(self, *args, **options):

        # connect to s3

        # get all files in s3
        # for each file
        #   get the file name
        #   move the file to the new location
        #   update the document record with the new file name

        bucket = settings.AWS_STORAGE_BUCKET_NAME
        s3_session = session.Session()
        client = s3_session.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )
        results = {
            "files_moved": 0,
            "files_checked": 0,
            "files_skipped": 0,
            "documents_created": 0,
            "documents_updated": 0,
            "fys_created": 0,
        }
        continuation_token = "None"
        while True:
            objects_list = client.list_objects_v2(
                Bucket=bucket, ContinuationToken=continuation_token
            )
            continuation_token = objects_list.get("NextContinuationToken")
            for index, key in tqdm(enumerate(objects_list.get("Contents", []))):
                original_filename = key["Key"]
                org_id, date = get_orgid_and_date(original_filename)
                if not org_id or not date:
                    results["files_skipped"] += 1
                    # print("Skipping", original_filename)
                    continue
                results["files_checked"] += 1
                new_filename = get_new_filename(org_id, date)
                if original_filename != new_filename:
                    client.copy_object(
                        Bucket=bucket,
                        CopySource=f"{bucket}/{original_filename}",
                        Key=new_filename,
                    )
                    client.delete_object(Bucket=bucket, Key=original_filename)
                    # print("moved {} to {}".format(original_filename, new_filename))
                    results["files_moved"] += 1

                fy, created = CharityFinancialYear.objects.get_or_create(
                    financial_year_end=date,
                    charity_id=org_id,
                )
                if created:
                    results["fys_created"] += 1
                    # print("created fy for", original_filename)
                doc = fy.document
                if not doc:
                    doc = Document.objects.create(
                        financial_year=fy,
                        file=new_filename,
                        content_type=Document.DocumentTypes.PDF,
                        language=Document.DocumentLanguages.EN,
                        created_at=key["LastModified"],
                        updated_at=key["LastModified"],
                        content_length=key["Size"],
                    )
                    results["documents_created"] += 1
                    # print("created document for", original_filename)
                elif doc.file != new_filename:
                    doc.file = new_filename
                    doc.save()
                    results["documents_updated"] += 1
                    # print("updated document for", original_filename)
                fy.status = DocumentStatus.SUCCESS
                fy.save()

                if index % 1000 == 0:
                    print(" | ".join([f"{k}:{v:,.0f}" for k, v in results.items()]))
            if not continuation_token:
                break

        for k, v in results.items():
            print(k, v)
