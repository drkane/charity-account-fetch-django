from django.test import TestCase

# Create your tests here.
# scenarios to test:
# - fetch document for financial year
# - document does/doesn't exist in cc website
# - document does/doesn't download successfully
# - document does/doesn't already have text content extracted
# - document does/doesn't convert successfully (PDF should still be saved)
# - document does/doesn't save successfully


# scenario 1:
# - PDF exists and already has text content extracted
# - PDF should be saved successfully
# - status should be set to SUCCESS


# scenario 2:
# - PDF exists and does not have text content extracted
# - PDF should be saved successfully
# - ocr should be run successfully
# - status should be set to SUCCESS
