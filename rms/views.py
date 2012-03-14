from django.template import Context
from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponsePermanentRedirect

from django.core.urlresolvers import reverse

from django.db import transaction

from rms.models import *

import simplejson
import datetime

from django.conf import settings

def _get_parameter(request, name):
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

    _locale = locale.lower()

    json_responses = {}

    try:
      a = Application.objects.get(appid=app_id)
      c_list = Category.objects.filter(catid=cat_id,application=a)

      if len(c_list)==0:
          print "No category found"
          return {}

      rk_list = \
              RuleKey.objects.filter(category=c_list[0])
      if len(rk_list)==0:
          print "No rule keys found"
          return {}

      r_list = []
      for i in rk_list:
          aux = Rule.objects.filter(
                            rule_key=i,
                            locale=_locale
                            )
          # print unicode(i.keyname) + " 1: " + _locale
          if len(aux)==0:
              # aux = Rule.objects.filter(
              #               rule_key=i,
              #               locale__startswith=_locale.split("-")[0] + "-"
              #               )
              # # there are other similar languages
              # if len(aux)>0:
              #     _l = aux[0].locale
              #     # print unicode(i.keyname) + " 2: " + (_l)
              #     aux = Rule.objects.filter(
              #               rule_key=i,
              #               locale=_l
              #               )
              # # using "default" as default
              # else:
              #     # print unicode(i.keyname) + " 3: default"
              #     aux = Rule.objects.filter( ...
              aux = Rule.objects.filter(
                            rule_key=i,
                            locale="default"
                            )

          for ii in aux:
             r_list.append(ii)

      for rule in r_list:
          try:
            keyname = rule.rule_key.keyname
            if rule.weight <= 0:
               continue

            if not json_responses.has_key(keyname):
                json_responses[keyname] = []

            json_responses[keyname].append(rule.to_dict())

          except Exception, e:
            print e

    except Exception, e:
        print e
        raise Http500

    return json_responses


def rules(request, app_id, cat_id=None):

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

    try:
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

      hr =  HttpResponse(simplejson.dumps(json_responses),
                           mimetype='application/json;charset=utf-8')
      hr['Character-Set'] = 'UTF-8'
      try:
          hr['Cache-Control'] = settings.HTTP_CACHE_CONTROL
      except Exception:
          pass

      return hr

    except Exception, e:
        print e
        raise Http404


@transaction.commit_on_success
@login_required
def clone_application(request, _id=None):
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
    hr =  HttpResponse(simplejson.dumps(json_responses),
                           mimetype='application/json;charset=utf-8')
    hr['Character-Set'] = 'UTF-8'
    return hr


@transaction.commit_on_success
@login_required
def clone_locale(request):
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
                r.clone_deep()
                r.locale = new_locale
                r.save()
      except Exception, e:
        print e
        raise Http404


      json_responses = {}
      json_responses["message"] = "Done"
      json_responses["result"] = 0
      hr =  HttpResponse(simplejson.dumps(json_responses),
                           mimetype='application/json;charset=utf-8')
      hr['Character-Set'] = 'UTF-8'
      return hr



@login_required
def export_locale(request):
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

    json_responses = {}

    try:
      a = Application.objects.get(id=_id)

      if cat_id:
        c_list = \
          Category.objects.filter(catid=cat_id,application=a).order_by('catid')
      else:
        c_list = Category.objects.filter(application=a).order_by('catid')

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
      hr =  HttpResponse(simplejson.dumps(json_responses),
                           mimetype='application/json;charset=utf-8')
      hr['Character-Set'] = 'UTF-8'
      return hr

    except Exception, e:
        print e
        raise Http404


def all_rules(request):
    json_responses = []
    for a in Application.objects.all():
        _a = {}

        c_list = Category.objects.filter(application=a).order_by('catid')

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

    hr =  HttpResponse(simplejson.dumps(json_responses),
                           mimetype='application/json;charset=utf-8')
    hr['Character-Set'] = 'UTF-8'
    return hr



def locales_by_application(request,_id):

    try:
      a = Application.objects.get(id=_id)

      locales = a.get_available_locales()

      hr =  HttpResponse(simplejson.dumps(locales),
                           mimetype='application/json;charset=utf-8')
      hr['Character-Set'] = 'UTF-8'
      return hr

    except Exception, e:
        print e
        raise Http404



