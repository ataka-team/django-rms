#!/usr/bin/env python
from django.core.management import setup_environ
import imp
import simplejson

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

if __name__ == "__main__":
    # execute_manager(settings)
    setup_environ(settings)

    from rms.models import *

    f = file("rules.json")
    rules = simplejson.load(f )
    # print rules

    found_application = Application.objects.filter(appid="bob")
    if len(found_application) == 0:
      a = Application(appid="bob", appname="Bob the frog")
      a.save()
    else:
      a = found_application[0]
      a.appname="Bob the frog"
      a.save()

    found_category = \
      Category.objects.filter(catid="default",application=a)
    default_category = None
    if len(found_category) == 0:
      default_category = Category(catid="default",
                   catname="default",
                   application=a)
      default_category.save()
    else:
      default_category = found_category[0]
      default_category.application=a
      default_category.save()


    locale = "default"

    for r in rules:
        c = None
        if r.has_key("category"):
            found_categories = Category.objects.filter(catid=r["category"])
            c = None
            if len(found_categories) == 0:
                c = Category(catid=r["category"],
                             catname=r["category"],
                             application=a
                            )
                c.save()
            else:
                c = found_categories[0]
                c.catname=r["category"]
                c.application=a
                c.save()
            
        else:
            c = default_category

        # print r["rule_key"] + " in " + c.catname



        found_rule_keys = \
              RuleKey.objects.filter(keyname=r["rule_key"],category=c)
        rk = None
        if len(found_rule_keys) == 0:
                rk = RuleKey(
                      keyname=r["rule_key"],
                      category=c
                          )
                rk.save()
        else:
                rk = found_rule_keys[0]
                rk.category=c
                rk.save()

        # To create a rule we need:
        #  - firstable, a message getting from the first speech if it had
        #    else, this rule will not be imported.
        #  - rk
        #  - locale
        #  - slug (generated from message)
        #  - weight (default: 0 )
        #  - json rule data the same r entry

        # XXX: Message is not from rule_key because customer dont want
        # _message = r["rule_key"]
        _message = ""
        found_speechs = False
        if r.has_key("actions"):
            for ac in r["actions"]:
              if ac.has_key("speech"):
                if len(ac["speech"]) > 0:
                  found_speechs = True
                  _message = ac["speech"][0]
                # print r["rule_key"] + " has " + str(len(ac["speech"])) \
                # + " speechs"

        # if found_speechs:
        _weigth = 1
        if r.has_key("weight"):
                _weigth = r["weight"]


        _locale = locale

        found_rules = \
                    Rule.objects.filter(
                            message=_message,
                            rule_key=rk,
                            locale=_locale)

        # XXX: Deleted uneeded keys
        if r.has_key("rule_key"):
          r.pop("rule_key")
        if r.has_key("weight"):
          r.pop("weight")
        if r.has_key("category"):
          r.pop("category")

        rr = None
        if len(found_rules) == 0:
                rr = Rule(
                      rule_key = rk,
                      locale = _locale,
                      message = _message,
                      weight = _weigth,
                      rule_data = simplejson.dumps(r),
                          )
                rr.save()
        else:
                rr = found_rules[0]
                rr.rule_key = rk
                rr.locale = _locale
                rr.message = _message
                rr.weight = _weigth
                rr.rule_data = simplejson.dumps(r)
                rr.save()





    # speechs = []
    # for r in rules:
    #     if r.has_key("actions"):
    #       if r.["actions"]:
    #       rule_keys.append(r["rule_key"])

    # print rule_keys



    # a = Application(appid=2, appname="a")
    # a.save()
    # Application.objects.all()
