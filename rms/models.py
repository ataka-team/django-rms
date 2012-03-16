from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from django.conf import settings

class Application(models.Model):
    class Meta:
        verbose_name = 'Application'
        ordering = ['appid']

    appname = models.CharField(max_length=100)
    appid = models.CharField(max_length=50)
    icon = models.ImageField(_("image"),
            upload_to="images", blank=True)

    def clone_deep(self):
        a = Application (
                appname=self.appname,
                appid=self.appid,
                icon=self.icon
                )
        a.save()
        c_list = Category.objects.filter(application=self)
        for c in c_list:
            c_clone = c.clone_deep()
            c_clone.application=a
            c_clone.save()
            
        al_list = ApplicationLocale.objects.filter(application=self)
        for al in al_list:
            al_clone = al.clone_deep()
            al_clone.application=a
            al_clone.save()
        return a

    def get_related_rules(self):
        res = []
        c_list = Category.objects.filter(application=self)

        if len(c_list)==0:
          return res

        for c in c_list:
          rk_list = \
              RuleKey.objects.filter(category=c)
          for rk in rk_list:
              r_list = \
                Rule.objects.filter(rule_key=rk)
              for r in r_list:
                res.append(r)

        return res


    def new_locale(self, localename):
        al = ApplicationLocale(application=self, 
            localename=localename)
        al.save()

    def delete_locale(self, localename):
        
        al_list = ApplicationLocale.objects.filter(application=self)
        for al in al_list:
            if al.localename == localename.strip():
                al.delete()
                
        r_list = self.get_related_rules()
        for r in r_list:
            if r.locale == localename.strip():
                r.delete()


    def get_available_locales(self):
        res = []

        # Adding already registered locales
        al_list = ApplicationLocale.objects.filter(application=self)
        for al in al_list:
            _al = al.localename
            try:
                res.index(_al)
            except ValueError:
                res.append(_al)

        c_list = Category.objects.filter(application=self)

        if len(c_list)==0:
          return res

        for c in c_list:
          rk_list = \
              RuleKey.objects.filter(category=c)
          for rk in rk_list:
              r_list = \
                Rule.objects.filter(rule_key=rk)
              for r in r_list:
                  _l = r.locale
                  try:
                    res.index(_l)
                  except ValueError:
                    res.append(_l)
                    # Registering new locale
                    al = ApplicationLocale(application=self, 
                        localename=_l)
                    al.save()
                    
        
        return res


    def __unicode__(self):
        return self.appname

    def save(self, *args, **kwargs):

        appid_candidate = self.appid
        original_appid = appid_candidate

        suffix = 0
        while True:
          found_apps = \
                    Application.objects.filter(
                            appid=appid_candidate,
                            )
          if len(found_apps) == 1:
              if found_apps[0] == self:
                self.appid = appid_candidate
                break

          if len(found_apps) == 0:
              self.appid = appid_candidate
              break

          suffix = suffix + 1
          appid_candidate = \
            original_appid + " duplicate " + unicode(suffix)

        super(Application, self).save(*args, **kwargs)

class ApplicationLocale(models.Model):
    class Meta:
        verbose_name = 'Application locale'
        ordering = ['localename']
        
    localename = models.CharField(max_length=20)
    
    application = models.ForeignKey(Application, 
        blank=False, null=False)

    def clone_deep(self):
        al = ApplicationLocale (
                localename=self.localename,
                application=self.application
                )
        al.save()
        return al

    def to_dict(self):
        res = {}
        res["localename"] = self.localename
        return res

    def __unicode__(self):
        return self.localename


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        ordering = ['catid']

    catname = models.CharField(max_length=100)
    catid = models.CharField(max_length=50)

    application = models.ForeignKey(Application)

    def clone_deep(self):
        c = Category (
                catid=self.catid,
                catname=self.catname,
                application=self.application
                )
        c.save()
        rk_list = RuleKey.objects.filter(category=self)
        for rk in rk_list:
            rk_clone = rk.clone_deep()
            rk_clone.category=c
            rk_clone.save()
        return c


    def to_dict(self):
        res = {}
        res["catname"] = self.catname
        res["catid"] = self.catid
        return res

    def __unicode__(self):
        return self.catname

    def save(self, *args, **kwargs):

        catid_candidate = self.catid

        # XXX: "all" its a keyword using to refer to all categories
        if catid_candidate.strip() == "all":
            catid_candidate = "all_"

        self.catid = catid_candidate

        super(Category, self).save(*args, **kwargs)


class RuleKey(models.Model):
    class Meta:
        verbose_name = 'Rule key'
        ordering = ['keyname']

    keyname = models.CharField(max_length=100)

    category = models.ForeignKey(Category, blank=False, null=False)

    def __unicode__(self):
        return unicode(self.keyname) + \
                u' - ' + \
                unicode(self.category.catname)

    def clone_deep(self):
        rk = RuleKey (
                keyname=self.keyname,
                category=self.category,
                )
        rk.save()
        r_list = Rule.objects.filter(rule_key=self)
        for r in r_list:
            r_clone = r.clone_deep()
            r_clone.rule_key=rk
            r_clone.save()
        return rk

    def to_dict(self):
        res = {}
        res["keyname"] = self.keyname
        return res


    def get_catid(self):
        return self.category.catid
    def set_catid(self, catid):
        self.category.catid = catid
    catid = property(get_catid, set_catid)



class Rule(models.Model):
    class Meta:
        verbose_name = 'Rule'
        ordering = ['slug']

    message = models.CharField(max_length=20)
    locale = models.CharField(max_length=20)
    weight = models.IntegerField(default=1)
    rule_data = models.TextField(max_length=1000)
    slug = models.SlugField()

    rule_key = models.ForeignKey(RuleKey, blank=False, null=False)
    category = models.ForeignKey(Category, blank=False, null=False)
    application = \
        models.ForeignKey(Application, blank=False, null=False)

    def __unicode__(self):
        return self.slug

    def get_application_name(self):
        return self.application.appname
    application_name = property(get_application_name)

    def get_category_name(self):
        return self.category.catname
    category_name = property(get_category_name)

    def clone_deep(self):
        r = Rule (
                message=self.message,
                locale=self.locale,
                weight=self.weight,
                rule_data=self.rule_data,
                rule_key=self.rule_key,
                )
        r.save()
        return r

    def to_dict(self, include_locale=False):
        res = {}
        res["message"] = self.message
        res["slug"] = self.slug
        res["weight"] = self.weight
        res["rule"] = self.rule_data
        if include_locale:
          res["locale"] = self.locale
        return res

    def to_apple_string_format(self):
        res = " \"%s\" = \"%s\" " % (self.slug, self.message)
        return res


    def save(self, *args, **kwargs):
        self.locale = self.locale.lower()

        s = slugify(self.message)        
        
        # If empty message, slug from rule_key.keyname
        if s.strip() == "":
            s = self.rule_key.keyname

        if len(s) > 28:
            s = s[:28]
            
        if self.slug.strip() != "":
            s = self.slug.strip()

        # Avoid slug ended with '-'
        while True:
            if s.endswith("-"):
                s = s[:-1]
            else:
                break

        original_s = s
        suffix = 0
        while True:
            found_rules = \
                    Rule.objects.filter(
                            slug=s,
                            )
            
            if len(found_rules) == 1 and \
            found_rules[0] == self:
                self.slug = s
                break

            if len(found_rules) == 0:
                self.slug = s
                break
                
            suffix = suffix + 1
            s = original_s + unicode(suffix)

        self.category = self.rule_key.category
        self.application = self.rule_key.category.application

        super(Rule, self).save(*args, **kwargs)



