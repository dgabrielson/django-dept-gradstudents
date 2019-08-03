from __future__ import print_function, unicode_literals

from django.core.files.storage import FileSystemStorage


class NoUrlMixin(object):
    """
    Override the url method, because things here are not accessed the normal way.
    """

    def url(self, name):
        """
        It's impractical to get the model instance from the file name.
        """
        raise ValueError("This file is not accessible via a URL.")


class PaperworkFileSystemStorage(NoUrlMixin, FileSystemStorage):
    pass
