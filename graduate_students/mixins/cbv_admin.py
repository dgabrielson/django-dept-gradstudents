from __future__ import print_function, unicode_literals

from django.contrib.admin import helpers
from django.contrib.admin.options import get_content_type_for_model
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

##########################################################################

##########################################################################


class ClassBasedViewsAdminMixin(object):
    """
    Utility functions for making use of CBVs in Django admin.
    
    This still needs work for greater utility.
    
    E.g., this does *not* check any permissions: wrap with
    ``from django.contrib.auth.decorators import permission_required``
    if needed.
    
    
    Yo'll still need to add urls using get_urls()::
    
    def get_urls(self):
        urls = super(..., self).get_urls()
        urls = [url(r'^extra-action/$',
                    self.admin_site.admin_view(self.cb_changeform_view),
                    kwargs={'view_class': ViewClass, }
                    name='...',
                    ),
                ] + urls
        return  urls
    """

    def cb_changeform_view(self, request, *args, **kwargs):
        """
        Like a change view in the admin.
        """
        view_class = kwargs.get("view_class")
        add = kwargs.get("add", True)
        obj = kwargs.get("original", None)
        object_id = kwargs.get("object_id", None)
        title = kwargs.get("title", None)

        form = view_class.form_class()
        formsets = []
        opts = self.model._meta
        TO_FIELD_VAR = False
        IS_POPUP_VAR = False
        change = not True
        view_on_site_url = None
        form_url = ""
        app_label = opts.app_label
        adminForm = helpers.AdminForm(form, formsets, {}, None, model_admin=self)
        media = self.media + adminForm.media
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        inline_formsets = None

        # From ``changeform_view``
        if title is None:
            title = (_("Bulk add %s") if add else _("Bulk change %s")) % force_text(
                opts.verbose_name_plural
            )
        context = dict(
            self.admin_site.each_context(request),
            title=title,
            adminform=adminForm,
            object_id=object_id,
            original=obj,
            is_popup=(IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            to_field=to_field,
            media=media,
            inline_admin_formsets=inline_formsets,
            errors=helpers.AdminErrorList(form, formsets),
            preserved_filters=self.get_preserved_filters(request),
        )
        # From ``render_change_form``
        context.update(
            {
                "add": add,
                "change": change,
                "has_add_permission": self.has_add_permission(request),
                "has_change_permission": self.has_change_permission(request, obj),
                "has_delete_permission": self.has_delete_permission(request, obj),
                "has_file_field": True,  # FIXME - this should check if form or formsets have a FileField,
                "has_absolute_url": view_on_site_url is not None,
                "absolute_url": view_on_site_url,
                "form_url": form_url,
                "opts": opts,
                "content_type_id": get_content_type_for_model(self.model).pk,
                "save_as": self.save_as,
                "save_on_top": self.save_on_top,
                "to_field_var": TO_FIELD_VAR,
                "is_popup_var": IS_POPUP_VAR,
                "app_label": app_label,
                "media": self.media,
            }
        )

        original_get_context_data = view_class.get_context_data

        def _monkey_patch_get_context_data(instance, *args, **kwargs):
            data = original_get_context_data(instance, *args, **kwargs)
            data.update(context)
            return data

        view_class.get_context_data = _monkey_patch_get_context_data
        return view_class.as_view()(request)


##########################################################################
