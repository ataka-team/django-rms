from rms.models import *
from django.contrib import admin
from django.forms import ModelForm, PasswordInput, CharField

from django.db import transaction


def process_submited_files(request):
    '''
    Proccess submited files attached to the request.
    
    Note that currently only proccess icon files added for applications
    '''

    for k in request.FILES.keys():
        _k = k.split("-")
        if not len(_k) == 3:
            print k + " : " + request.POST[k]
        else:
            try:
                if k.startswith("application-"):
                    _,_id, _value = k.split("-")

                    _app = Application.objects.get(id=_id)

                    if _value == "icon":
                        _app.icon = request.FILES[k]

                    _app.save()
            except Exception,e:
                #IDEA: Add logger support
                # print "Error: " + str(e) + \
                #   " (Updating file for " + str(k) + " key)"
                pass


def get_submited_values_helper(request):
    '''
    Prepare a dict with the representation of the data submited.
    '''

    categories = {}
    rulekeys = {}
    rules = {}
    applications = {}

    for k in request.POST:
        if k.startswith("application-"):
            if not len(k.split("-")) == 3:
                print k + " : " + request.POST[k]
            else:
                _,_id, _value = k.split("-")
                if not applications.has_key(_id):
                    applications[_id] = {}
                applications[_id][_value] = request.POST[k]

                # To delete applications
                if _value == "DELETE":
                    applications[_id]["deleted"] = True

                # new12121
                if _id.startswith("new"):
                    applications[_id]["add"] = True

        if k.startswith("rule-"):
            if not len(k.split("-")) == 3:
                print k + " : " + request.POST[k]
            else:
                _,_id, _value = k.split("-")
                if not rules.has_key(_id):
                    rules[_id] = {}
                rules[_id][_value] = request.POST[k]

                # To delete rules
                if _value == "DELETE":
                    rules[_id]["deleted"] = True

                # new12121
                if _id.startswith("new"):
                    rules[_id]["add"] = True


        if k.startswith("category-"):
            if not len(k.split("-")) == 3:
                print k + " : " + request.POST[k]
            else:
                _,_id, _value = k.split("-")
                if not categories.has_key(_id):
                    categories[_id] = {}
                categories[_id][_value] = request.POST[k]

                # To delete categories
                if _value == "DELETE":
                    categories[_id]["deleted"] = True

                # new12121
                if _id.startswith("new"):
                    categories[_id]["add"] = True


        if k.startswith("rulekey-"):
            if not len(k.split("-")) == 3:
                print k + " : " + request.POST[k]
            else:
                _,_id, _value = k.split("-")
                if not rulekeys.has_key(_id):
                    rulekeys[_id] = {}
                rulekeys[_id][_value] = request.POST[k]

                # To delete rulekeys
                if _value == "DELETE":
                    rulekeys[_id]["deleted"] = True

                # new12121
                if _id.startswith("new"):
                    rulekeys[_id]["add"] = True


    return {"categories":categories, "rulekeys":rulekeys,
            "rules":rules, "applications": applications}


def process_rules(rules):

    for k,v in rules.iteritems():
        # k: {u'rule': u"", u'message': u'Commentary goes
        #     here...', u'slug': u'commentary-goes-here', u'weight': u'1'}

        try:
            _r = None
            if v.has_key("add") and v["add"]:
                if k.startswith("new"):
                    if v.has_key("rulekey"):
                        _rule_key_id = v["rulekey"]
                        _rule_key = RuleKey.objects.get(id=_rule_key_id)
                        _r = Rule(rule_key=_rule_key)

                        if v.has_key("message") and _r.message != v["message"]:
                            _r.message = v["message"]
                        if v.has_key("rule") \
                               and _r.rule_data.strip() != v["rule"].strip():
                            _r.rule = v["rule"]
                        if v.has_key("weight") and _r.weight != int(v["weight"]):
                            _r.weight = v["weight"]
                        if v.has_key("locale") and _r.weight != v["locale"]:
                            _r.locale = v["locale"]

                        _r.save()
                        print "Creating rule " + str(k)

                continue
            else:
                _r = Rule.objects.get(id=k)

            if v.has_key("deleted") and v["deleted"]:
                _r.weight = 0
                _r.save()
            else:
                rule_modified = False
                if v.has_key("message") and _r.message != v["message"]:
                    rule_modified = True
                if v.has_key("rule") \
                    and _r.rule_data.strip() != v["rule"].strip():
                    rule_modified = True
                if v.has_key("weight") and _r.weight != int(v["weight"]):
                    rule_modified = True

                if rule_modified:
                    print "Updating rule " + str(k)
                    rule_cloned = _r.clone_deep()

                    _r.weight = 0
                    _r.save()

                    if v.has_key("message"):
                        rule_cloned.message = v["message"]
                    if v.has_key("rule"):
                        rule_cloned.rule_data = v["rule"]
                    if v.has_key("weight"):
                        rule_cloned.weight = int(v["weight"])

                    rule_cloned.save()

        except Exception,e:
            #IDEA: Add logger support.
            # print "Error: " + str(e) + \
            #     " (Updating rule " + str(k) + ")"
            pass


def process_rulekeys(rulekeys,categories):
    for k,v in rulekeys.iteritems():
        # k: {u'keyname': u'template'}
        try:
            _rk = None
            if v.has_key("add") and v["add"]:
                if k.startswith("new"):
                    if v.has_key("category"):
                        _cat_id = v["category"]

                        # If is "-new-" try to compare with categories 
                        # should be a new category currently in creation
                        # process.
                        if _cat_id.startswith("new"):
                            _cat_id = categories[_cat_id]["newid"]

                        _cat = Category.objects.get(id=_cat_id)
                        _rk = RuleKey(category=_cat)

                        if v.has_key("keyname"):
                            _rk.keyname = v["keyname"]
                        _rk.save()
                        v["newid"] = _rk.id

                        print "Creating rulekey " + str(_rk)

                continue
            else:
                _rk = RuleKey.objects.get(id=k)

            if v.has_key("deleted") and v["deleted"]:
                _rk.delete()
            else:
                if v.has_key("keyname"):
                    _rk.keyname = v["keyname"]
                _rk.save()
        except Exception,e:
            #IDEA: Add logger support.
            # print "Error: " + str(e) + \
            #   " (Updating rule key" + str(k) + ")"
            pass


def process_categories(categories):
    for k,v in categories.iteritems():
        # k: {u'catname': u'default', u'catid': u'default'}
        try:

            _c = None
            if v.has_key("add") and v["add"]:
                if k.startswith("new"):
                    if v.has_key("application"):
                        _application_id = v["application"]
                        _app = \
                            Application.objects.get(id=_application_id)
                        _c = Category(application=_app)

                        if v.has_key("catid"):
                            _c.catid = v["catid"]
                        if v.has_key("catname"):
                            _c.catname = v["catname"]
                        _c.save()
                        v["newid"] = _c.id
                        print "Creating catname " + str(_c)

                continue
            else:
                _c = Category.objects.get(id=k)

            if v.has_key("deleted") and v["deleted"]:
                _c.delete()
            else:
                if v.has_key("catname"):
                    _c.catname = v["catname"]
                if v.has_key("catid"):
                    _c.catid = v["catid"]
                _c.save()
        except Exception,e:
            #IDEA: Add logger support.
            # print "Error: " + str(e) + \
            #   " (Updating category" + str(k) + ")"
            pass


def process_applications(applications):
    for k,v in applications.iteritems():
        # k: {u'appname': u'Bob the frog', u'appid': u'frog', u'icon':
        # <file>}
        try:

            _a = None
            if v.has_key("add") and v["add"]:
                if k.startswith("new"):
                    if v.has_key("application"):
                        _a = Application()

                        if v.has_key("appid"):
                            _a.appid = v["appid"]
                        if v.has_key("appname"):
                            _a.appname = v["appname"]

                        _a.save()
                        v["newid"] = _a.id
                        print "Creating application " + str(_a)

                continue
            else:
                _a = Application.objects.get(id=k)

            if v.has_key("deleted") and v["deleted"]:
                _a.delete()
            else:
                if v.has_key("appname"):
                    _a.appname = v["appname"]
                if v.has_key("appid"):
                    _a.appid = v["appid"]
                if v.has_key("icon"):
                    _a.icon = v["icon"]

                _a.save()
        except Exception,e:
            #IDEA: Add logger support.
            # print "Error: " + str(e) + \
            #   " (Updating application" + str(k) + ")"
            pass



@transaction.commit_on_success
def clone_selected_items(modeladmin, request, queryset):
    if request.POST:
        s = request.POST.getlist('selected')

        for i in s:
            if i.startswith("rulekey-"):
                rk = RuleKey.objects.get(id=i.split('-')[1])
                rk.clone_deep()
            if i.startswith("category-"):
                c = Category.objects.get(id=i.split('-')[1])
                c.clone_deep()
            if i.startswith("application-"):
                a = Application.objects.get(id=i.split('-')[1])
                a.clone_deep()
clone_selected_items.short_description = "Clone selected items"

@transaction.commit_on_success
def delete_selected_items(modeladmin, request, queryset):
    if request.POST:
        s = request.POST.getlist('selected')

        for i in s:
            if i.startswith("rulekey-"):
                rk = RuleKey.objects.get(id=i.split('-')[1])
                rk.delete()
            if i.startswith("category-"):
                c = Category.objects.get(id=i.split('-')[1])
                c.delete()
            if i.startswith("application-"):
                a = Application.objects.get(id=i.split('-')[1])
                a.delete()
delete_selected_items.short_description = "Delete selected items"

def update_all_items(modeladmin, request, queryset):
    if request.POST:

        process_submited_files(request)

        tmp = get_submited_values_helper(request)
        categories = tmp["categories"]
        rulekeys = tmp["rulekeys"]
        rules = tmp["rules"]
        applications = tmp["applications"]

        # Categories can be modified adding "newid" attribute
        process_applications(applications)
        process_categories(categories)
        process_rulekeys(rulekeys,categories)
        process_rules(rules)
update_all_items.short_description = "Update all items"


class RulesInline(admin.TabularInline):
    model = Rule
    extra = 1

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 3

class ApplicationAdmin(admin.ModelAdmin):
    model = Application
    fieldsets = [
        (None,               {'fields': ['appid','appname']}),
        ('Other information', 
            {'fields': ['icon',], 'classes': ['collapse']}),
    ]
    actions = [ clone_selected_items,
                delete_selected_items,
                update_all_items ]
                
    list_per_page = 50

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    @transaction.commit_on_success
    def change_view(self, request, object_id, extra_context=None):

        if (len(request.POST)>1):

            if request.FILES.has_key("localefile"):
                f = request.FILES["localefile"]

                for l in f:
                    try:
                        k,v = l.split("=")
                        slug = k.strip().replace('"','')
                        message = v.strip().replace('"','')

                        found_rules = \
                                Rule.objects.filter(
                                   slug=slug,
                                   )
                        if len(found_rules)>0:
                            found_rules[0].message = message
                            found_rules[0].save()
                    except Exception, e:
                        print e

            tmp = get_submited_values_helper(request)
            categories = tmp["categories"]
            rulekeys = tmp["rulekeys"]
            rules = tmp["rules"]

            # Categories can be modified adding "newid" attribute
            process_categories(categories)
            process_rulekeys(rulekeys,categories)
            process_rules(rules)



        return super(ApplicationAdmin, self).change_view(request, object_id, extra_context)




class RuleKeyAdmin(admin.ModelAdmin):
    list_display = ('keyname', 'catid')
    list_filter = ['category' ]
    search_fields = ['keyname', 'catid']

    inlines = [RulesInline]


class RuleAdmin(admin.ModelAdmin):
    list_display = ('message', 'slug' ,'locale', 'weight',
            'category', 'application', 'rule_key')
    list_filter = ['locale', 'weight', 'category',
            'application', 'rule_key']
    search_fields = ['message', 'weight']
    exclude = ('application', 'category')


admin.site.register(Application,ApplicationAdmin)
# admin.site.register(Category)
# admin.site.register(RuleKey,RuleKeyAdmin)
admin.site.register(Rule,RuleAdmin)


