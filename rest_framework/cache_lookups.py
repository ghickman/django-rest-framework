"""
Provides a set of pluggable cache policies.
"""
from django.core.cache import cache
from rest_framework.exceptions import PreconditionFailed


class BaseCacheLookup(object):
    def get_header(self, obj):
        return {}

    def resource_unchanged(self, request):
        """
        Return `False` if resource has changed, `True` otherwise.
        """
        return False


class ETagCacheLookup(BaseCacheLookup):
    """
    """
    etag_variable = 'etag'
    request_header = 'HTTP_IF_NONE_MATCH'

    @staticmethod
    def get_cache_key(cls, pk):
        try:
            class_name = cls.__name__  # class
        except AttributeError:
            class_name = cls.__class__.__name__  # instance
        return 'etag-{}-{}'.format(class_name, pk)

    def get_etag(self, obj):
        return getattr(obj, self.etag_variable)

    def get_request_header(self):
        return self.request_header

    def get_response_header(self, obj):
        key = self.get_cache_key(obj, 'pk')
        etag = self.get_etag(obj)
        cache.set(key, etag)
        return {'ETag': etag}

    def precondition_check(self, obj, request):
        if self.get_etag(obj) != request.META.get(self.get_request_header()):
            raise PreconditionFailed

    def resource_unchanged(self, request, key):
        etag = cache.get(key)
        header = request.META.get(self.get_request_header())
        if etag is not None and etag == header:
            return True
        return False
