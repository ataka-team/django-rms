from django.conf.urls.defaults import *

urlpatterns = patterns('rms.views',
    (r'^rules$',
        'all_rules',
        None, 'rms-all-rules'),

    (r'^rules/(?P<_id>\d+)$',
        'rules_by_application',
        None, 'rms-rules-by-application'),

    (r'^rules/(?P<app_id>[\w_-]+)/all$',
        'rules',
        None, 'rms-rules-app-all'),

    (r'^rules/(?P<app_id>[\w_-]+)/(?P<cat_id>[\w_-]+)$',
        'rules',
        None, 'rms-rules'),

    (r'^app/(?P<_id>\d+)/clone$',
        'clone_application',
        None, 'rms-app-clone'),

    (r'^app/clone$',
        'clone_application',
        None, 'rms-app-clone-params'),

    (r'^app/locale$',
        'export_locale',
        None, 'rms-app-export-locale-params'),

    (r'^locale/clone$',
        'clone_locale',
        None, 'rms-app-clone-locale-params'),

    (r'^locale/delete$',
        'delete_locale',
        None, 'rms-app-delete-locale-params'),

    (r'^locale/new$',
        'new_locale',
        None, 'rms-app-new-locale-params'),

    (r'^locales/(?P<_id>\d+)$',
        'locales_by_application',
        None, 'rms-locales-by-application'),



)
