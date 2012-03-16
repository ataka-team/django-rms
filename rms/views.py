from django.template import Context
from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import transaction

from django.conf import settings

from rms.models import *

import simplejson
import datetime

def _json_response(locales,cache_control=True):
    '''
    Prepare a JSON HttpResponse for a dict/list or similar JSON 
    compatible objects
    '''
    hr =  HttpResponse(simplejson.dumps(locales),
        mimetype='application/json;charset=utf-8')
    hr['Character-Set'] = 'UTF-8'
    
    if cache_control:
        try:
            hr['Cache-Control'] = settings.HTTP_CACHE_CONTROL
        except Exception:
            pass
        
    return hr

def _get_parameter(request, name):
    '''
    Helper: abstraction to recover paremeters from POST or GET 
    either
    '''

    if request.POST:
        try:
          return request.POST[name]
        except KeyError:
          pass
    if request.GET:
        try:
          return request.GET[name]
        except KeyError as e:
          raise e

def _get_rules_by_category (app_id, cat_id, locale="default"):
    '''
    Helper: Return a JSON with the rules for a category of a specific 
    application by a concrete locale. If no locale is set, "default" 
    locale will be used.
    
    Result example:
    
        {
            "charactertouch-poke-head": [
                {
                    "rule": "{'is_play': True, 'actions': [ ... ]}",
                    "message": "Yo...",
                    "slug": "yo2",
                    "weight": 6
                }
            ]
        }
    
    '''
    
    _locale = locale.lower()

    json_response = {}

    a = Application.objects.get(appid=app_id)
    c_list = Category.objects.filter(catid=cat_id,application=a)

    if len(c_list)==0:
        #IDEA: Add logger support.
        #IDEA: Add JSON error protocol.
        # print "No category found"
        return {}

    rk_list = \
          RuleKey.objects.filter(category=c_list[0])
    if len(rk_list)==0:
        #IDEA: Add logger support.
        #IDEA: Add JSON error protocol.            
        # print "No rule keys found"
        return {}

    r_list = []
    for i in rk_list:
        aux_rules = Rule.objects.filter(
                        rule_key=i,
                        locale=_locale
                        )

        if len(aux_rules)==0:
            # XXX: Behaviour modification requested by customer:
            #
            # Old: logic: 
            #   - If locale has >0 Rules for a RuleKey 
            #       -> Return them
            #   - If locale has 0 Rules for a RuleKey
            #   - Search rules in a similar locale
            #   - If similar locale has >0 Rules for a RuleKey 
            #       -> Return them
            #   - Search rules in the "en-us" locale
            #   - If "en-us" locale has >0 Rules for a RuleKey 
            #       -> Return them
            #
            # New: logic: 
            #   - If locale has >0 Rules for a RuleKey 
            #       -> Return them
            #   - If locale has 0 Rules for a RuleKey
            #   - Search rules in the "default" locale
            #   - If "defaut" locale has >0 Rules for a RuleKey 
            #       -> Return them
            #
            #
            # aux_rules = Rule.objects.filter(
            #   rule_key=i,
            #   locale__startswith=_locale.split("-")[0] + "-"
            #   )
            # # there are other similar languages
            # if len(aux_rules)>0:
            #     _l = aux_rules[0].locale
            #     # print unicode(i.keyname) + " 2: " + (_l)
            #     aux_rules = Rule.objects.filter(
            #               rule_key=i,
            #               locale=_l
            #               )
            # # using "default" as default
            # else:
            #     # print unicode(i.keyname) + " 3: default"
            #     aux_rules = Rule.objects.filter( ...
            aux_rules = Rule.objects.filter(
                        rule_key=i,
                        locale="default"
                        )

        for aux_r in aux_rules:
            r_list.append(aux_r)

    for rule in r_list:
        try:
            keyname = rule.rule_key.keyname
            if rule.weight <= 0:
                continue

            if not json_response.has_key(keyname):
                json_response[keyname] = []

            json_response[keyname].append(rule.to_dict())

        except Exception, e:
            #IDEA: Add logger support.
            pass

    return json_response


def rules(request, app_id, cat_id=None):
    '''
    Return a rules grouped by rule keys as a JSON dictionary for a 
    spefific locale received as a GET paremeter 
    
    If category requested is "None", output rules for 
    all categories. eg::

        { 'moody' : {
            auto-idle-idle : { }
                             ...,
        {'slepy: { ...

    '''

    try:
        _locale = _get_parameter(request, "locale")
    except Exception, e:
        _locale = "default"
    if not _locale:
        _locale = "default"
    if len(_locale.split("-"))<2:
        _locale = "default"

    _locale = _locale.lower()

    json_responses = {}

    if cat_id == None:
        a = Application.objects.get(appid=app_id)
        c_list = Category.objects.filter(application=a)
        for c in c_list:

            json_responses_for_category = \
                _get_rules_by_category (app_id, c.catid, _locale)

            json_responses[c.catname] = json_responses_for_category

    else:
        json_responses = \
            _get_rules_by_category (app_id, cat_id, _locale)

    return _json_response(json_responses,False)




@transaction.commit_on_success
@login_required
def clone_application(request, _id=None):
    '''
    Clone a application. _id can be received as a GET parameter ("id").
    '''
    if not _id:
      try:
        _id = _get_parameter(request, "id")
      except Exception, e:
        raise Http404
      if not _id:
        raise Http404

    try:
        a = Application.objects.get(id=_id)
    except Exception, e:
        print e
        raise Http404
    try:
        a.clone_deep()
    except Exception, e:
        print e
        raise Http404

    json_responses = {}
    json_responses["message"] = "Done"
    json_responses["result"] = 0
    return _json_response(json_responses,False)


@transaction.commit_on_success
@login_required
def new_locale(request):
    '''
    Create a new locale.
    GET paremeters received are:
    
        * id: application id
        * newlocale: name of the new locale. Egg: "en-us"
    '''
    try:
        _id = _get_parameter(request, "id")
    except Exception, e:
        raise Http404
    if not _id:
        raise Http404
      
    try:
        new_locale = _get_parameter(request, "newlocale")
    except Exception, e:
        raise Http404
    if not new_locale:
        raise Http404
    new_locale = new_locale.lower()

    if len(new_locale.split("-"))<2 and new_locale != "default":
        raise Http404

    try:
        a = Application.objects.get(id=_id)
    except Exception, e:
        print e
        raise Http404
        
    try:
        a.new_locale(new_locale)        
    except Exception, e:
        print e
        raise Http404

    json_responses = {}
    json_responses["message"] = "Done"
    json_responses["result"] = 0
    
    return _json_response(json_responses,False)


@transaction.commit_on_success
@login_required
def clone_locale(request):
    '''
    Clone a locale.
    GET paremeters received are:
    
        * id: application id
        * currentlocale: name of the baselocale. Egg: "en-us"
        * newlocale: name of the new locale. Egg: "en-ca"
    '''
    
    try:
        _id = _get_parameter(request, "id")
    except Exception, e:
        raise Http404
    if not _id:
        raise Http404
    try:
        c_locale = _get_parameter(request, "currentlocale")
    except Exception, e:
        raise Http404
    if not c_locale:
        raise Http404
    c_locale = c_locale.lower()

    try:
        new_locale = _get_parameter(request, "newlocale")
    except Exception, e:
        raise Http404
    if not new_locale:
        raise Http404
    new_locale = new_locale.lower()

    if len(new_locale.split("-"))<2:
        raise Http404

    try:
        a = Application.objects.get(id=_id)
    except Exception, e:
        print e
        raise Http404
    try:
        r_list = a.get_related_rules()
        for r in r_list:
            if r.locale == c_locale:
                r_clone = r.clone_deep()
                r_clone.locale = new_locale
                r_clone.save()
    except Exception, e:
        print e
        raise Http404


    json_responses = {}
    json_responses["message"] = "Done"
    json_responses["result"] = 0
      
    return _json_response(json_responses,False)


@transaction.commit_on_success
@login_required
def delete_locale(request):
    ''''
    Delete a locale.
    GET paremeters received are:
    
        * id: application id
        * locale: name of the locale to delete. Egg: "en-en"
    '''
    
    try:
        _id = _get_parameter(request, "id")
    except Exception, e:
        raise Http404

    try:
        locale = _get_parameter(request, "locale")
    except Exception, e:
        raise Http404
    if not locale:
        raise Http404
    locale = locale.lower()

    try:
        a = Application.objects.get(id=_id)
    except Exception, e:
        print e
        raise Http404
      
    try:
        a.delete_locale(locale)        
    except Exception, e:
        print e
        raise Http404

    json_responses = {}
    json_responses["message"] = "Done"
    json_responses["result"] = 0
      
    return _json_response(json_responses,False)


@login_required
def export_locale(request):
    '''
    Export a locale.
    GET paremeters received are:
    
        * id: application id
        * locale: name of the locale to export. Egg: "en-us"
    '''
    try:
        _id = _get_parameter(request, "id")
    except Exception, e:
        raise Http404
    if not _id:
        raise Http404

    try:
        locale = _get_parameter(request, "locale")
    except Exception, e:
        raise Http404
    if not locale:
        locale = "default"
    locale = locale.lower()

    try:
        a = Application.objects.get(id=_id)
    except Exception, e:
        print e
        raise Http404

    res = u''
    try:
        r_list = a.get_related_rules()
        for r in r_list:
            if r.locale == locale:
                res = res + r.to_apple_string_format() + "\n"

    except Exception, e:
        print e
        raise Http404

    hr =  HttpResponse(res, mimetype='text/plain')
    hr['Content-Disposition'] = "attachment;filename=locale_%s.txt" \
        % locale
    return hr



def rules_by_application(request, _id, cat_id=None):
    '''
    This method is used in the by the change_form template for RMS 
    applications.
    
    Return a JSON list with rules sorted by category and grouped by 
    rule keys.
    '''

    json_responses = {}

    a = Application.objects.get(id=_id)

    if cat_id:
        c_list = \
            Category.objects.filter(catid=cat_id,application=a).order_by('catid')
    else:
        c_list = \
            Category.objects.filter(application=a).order_by('catid')

    if len(c_list)==0:
        print "No category found"
        raise Http404

    categories = []
    for c in c_list:

        _c = c.to_dict()
        _c["id"]=c.id
        categories.append(_c)
        _c["rulekeys"]=[]

        rk_list = \
            RuleKey.objects.filter(category=c)
        for rk in rk_list:
            _rk = rk.to_dict()
            _rk["id"] = rk.id
            _c["rulekeys"].append(_rk)
            _rk["rules"]=[]

            r_list = \
                Rule.objects.filter(rule_key=rk)
            for r in r_list:
                _r = r.to_dict(include_locale=True)
                _r["id"] = r.id
                _rk["rules"].append(_r)


    json_responses = categories
    return _json_response(json_responses,False)



def all_rules(request):
    '''
    This method is used in the by the change_list template for RMS 
    applications.
    
    Return a JSON list with all rules sorted by application and 
    grouped by category and grouped by rule keys.
    '''
    
    json_responses = []
    for a in Application.objects.all():
        _a = {}

        c_list = \
            Category.objects.filter(application=a).order_by('catid')

        categories = []
        for c in c_list:

            _c = c.to_dict()
            _c["id"]=c.id
            categories.append(_c)
            _c["rulekeys"]=[]

            rk_list = \
                RuleKey.objects.filter(category=c)
            for rk in rk_list:
                _rk = rk.to_dict()
                _rk["id"] = rk.id
                _c["rulekeys"].append(_rk)
                _rk["rules"]=[]

                r_list = \
                    Rule.objects.filter(rule_key=rk)
                for r in r_list:
                    _r = r.to_dict(include_locale=True)
                    _r["id"] = r.id
                    _rk["rules"].append(_r)


        _a["categories"] = categories
        _a["appname"] = a.appname
        _a["id"] = a.id
        _a["appid"] = a.appid
        _a["icon"] = a.icon.name
        json_responses.append(_a)

    return _json_response(json_responses,False)


def locales_by_application(request,_id):
    '''
    Get locales availables by application.id (non application.appid)
    '''

    a = Application.objects.get(id=_id)
    locales = a.get_available_locales()
    return _json_response(locales, False)
    


