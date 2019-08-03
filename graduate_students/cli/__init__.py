from __future__ import print_function, unicode_literals

from django.conf import settings
from django.utils.encoding import force_text

#######################################################################


#######################################################################


def resolve_lookup(object, name):
    """
    This function originally found in django.templates.base.py, modified
    for arbitrary nested field lookups from the command line -F argument.
    
    Performs resolution of a real variable (i.e. not a literal) against the
    given context.

    As indicated by the method's name, this method is an implementation
    detail and shouldn't be called by external code. Use Variable.resolve()
    instead.
    """
    current = object
    try:  # catch-all for silent variable failures
        for bit in name.split("."):
            if current is None:
                return ""
            try:  # dictionary lookup
                current = current[bit]
            except (TypeError, AttributeError, KeyError, ValueError):
                try:  # attribute lookup
                    current = getattr(current, bit)
                except (TypeError, AttributeError):
                    try:  # list-index lookup
                        current = current[int(bit)]
                    except (
                        IndexError,  # list index out of range
                        ValueError,  # invalid literal for int()
                        KeyError,  # current is a dict without `int(bit)` key
                        TypeError,
                    ):  # unsubscriptable object
                        return "Failed lookup for key [%s] in %r" % (
                            bit,
                            current,
                        )  # missing attribute
            if callable(current):
                if getattr(current, "do_not_call_in_templates", False):
                    pass
                elif getattr(current, "alters_data", False):
                    current = "<< invalid -- no data alteration >>"
                else:
                    try:  # method call (assuming no args required)
                        current = current()
                    except TypeError:  # arguments *were* required
                        # GOTCHA: This will also catch any TypeError
                        # raised in the function itself.
                        current = (
                            settings.TEMPLATE_STRING_IF_INVALID
                        )  # invalid method call
    except Exception as e:
        if getattr(e, "silent_variable_failure", False):
            current = "<< invalid -- exception >>"
        else:
            raise

    return force_text(current)


#######################################################################


def print_object(obj):
    print(obj.__class__.__name__ + "\t" + str(obj))
    fields = [f.name for f in obj.__class__._meta.fields]
    for f in fields:
        value = getattr(obj, "get_{0}_display".format(f), None)
        if value is not None:
            if callable(value):
                value = value()
            else:
                value = None
        if value is None:
            value = str(getattr(obj, f))

        print("\t" + f + "\t" + value)


#######################################################################
