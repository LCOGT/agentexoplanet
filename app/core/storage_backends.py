from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

# Static files are public (anyone can read them)
class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

# Media files are not public. Only authorized users should have access.
class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = None
    file_overwrite = True
