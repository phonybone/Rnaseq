'''
Evoque - managed eval-based freeform templating 
Copyright (C) 2007 Mario Ruggier <mario@ruggier.org>
Licensed under the Academic Free License version 3.0
URL: http://evoque.gizmojo.org/
'''
__url__ = "$URL: svn://gizmojo.org/pub/evoque/trunk/collection.py $"
__revision__ = "$Id: collection.py 1150 2009-01-20 00:55:08Z mario $"

from os.path import isabs, isdir, normpath
from evoque.translate import Translator
from evoque.template import Template
from evoque.evaluator import specified_kwargs

def check_dir(path):
    """ (path:str) -> bool 
    Check if path is absolute and is a directory.
    """
    if not isabs(path):
        raise ValueError("Path %r is not absolute" % path)
    if not isdir(path):
        raise ValueError("Path %r is not a directory" % path)


# $begin{init}
class Collection(object):
    """ A collection of templates, rooted at a directory """
    
    def __init__(self, domain, name, path, 
            # defaults from Domain
            cache_size=None, auto_reload=None, slurpy_directives=None, 
            # defaults (from Domain) for Templates
            quoting=None, input_encoding=None, filters=None):
        """
        domain: either(None, Domain)
        name: str, name by which to retrieve the collection
        path: str, abs path for root folder for the collection
        
        For more on defaults from Domain init parameters, see the 
        docstring in domain.Domain.__init__().
        
        Preferred way to create a new collection: 
            domain.set_collection()
        """ 
        # $end{init}
        check_dir(path)
        self.dir = normpath(path)
        if name is None:
            raise ValueError("A Collection cannot have a None name")
        self.name = name
        domain_kw = specified_kwargs(self.from_domain, vars())
        if domain is None:
            # in this case self is the default_collection
            from evoque.domain import Domain
            domain = Domain(self, **domain_kw)
        self.domain = domain
        # defaults -- cascaded down from domain
        for attr in self.from_domain:
            setattr(self, attr, domain_kw.get(attr, getattr(domain, attr)))
        #
        self.cache = Cache(maxsize=self.cache_size)
        self.translator = Translator(self)
    
    from_domain = ("cache_size", "auto_reload", "slurpy_directives", 
            "quoting", "input_encoding", "filters")
    
    # [get/set] the *raw* keyword -- unlike on Template.evoque() -- states 
    # to load the raw template string without compiling it.
    # [get] If already loaded and is file-based, then check/do auto_reload.
    # [get] If not file-based, may only retrieve -- string memory-based 
    # templates must be pre-loaded with set_template().
    # [set] if from_string, src holds raw TS, else src/name holds locator
    # [set] raises ValueError if a template is already set under name; for
    # already existing templates, they required a template.unload() first.
    #
    def get_template(self, name="", src=None, raw=None, data=None, 
                quoting=None, input_encoding=None, filters=None):
        """ () -> Template : get / load (if file-based) a template 
        """
        try:
            t = self.cache.get(name)
            if t.is_modified_since():
                t.refresh()
        except KeyError:
            t = Template(self.domain, name, src, self, raw, data, False,
                    quoting, input_encoding, filters)
            self.cache.set(name, t)
        return t
    
    def set_template(self, name, src, raw=None, data=None, from_string=True, 
                quoting=None, input_encoding=None, filters=None):
        """ () -> None : typically used to set a template from a string 
        """
        try:
            t = self.cache.get(name)
            raise ValueError("Collection [%s] already has a template named "
                    "[%s]" % (self.name, name))
        except KeyError:
            t = Template(self.domain, name, src, self, raw, data, from_string,
                    quoting, input_encoding, filters)
            self.cache.set(name, t)
    
    def has_template(self, name):
        """ (name:str) -> bool """
        return self.cache.has(name)
    

class Cache(object):
    """ A cache of items - discards least recently used 
    """
    
    def __init__(self, maxsize=0):
        """ (maxsize:int) """
        self.maxsize = maxsize
        self.cache = {}
        self.order = [] # least recently used first
    
    def get(self, key):
        """ (key:hashable) -> item 
        """
        item = self.cache[key] # KeyError if not present
        if self.maxsize > 0:
            self.order.remove(key)
            self.order.append(key)
        return item
    
    def set(self, key, value):
        """ (key:hashable, value:any) -> None 
        """
        if key in self.cache:
            self.order.remove(key)
        elif self.maxsize > 0 and len(self.cache) >= self.maxsize:
            # discard least recently used item
            del self.cache[self.order.pop(0)]
        self.cache[key] = value
        self.order.append(key)
    
    def has(self, key):
        """ (key:hashable) -> bool 
        """
        return key in self.cache
    
    def unset(self, key):
        """ (key:hashable) -> None 
        """
        self.order.remove(key)
        del self.cache[key]
    
