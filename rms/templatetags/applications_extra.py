from django.template import Library
from django.core.urlresolvers import reverse

from django.conf import settings

register = Library()



def results(cl):
        return cl.result_list

# def result_hidden_fields(cl):
#     if cl.formset:                                                                                     
#         for res, form in zip(cl.result_list, cl.formset.forms):                                        
#             if form[cl.model._meta.pk.name].is_hidden:                                                 
#                 yield mark_safe(force_unicode(form[cl.model._meta.pk.name]))

def result_list(cl):
    """
    Displays the headers and data list together
    """
    return {'cl': cl,
            'results': results(cl)}
result_list = register.inclusion_tag("admin/rms/application/change_list_results.html")(result_list)



