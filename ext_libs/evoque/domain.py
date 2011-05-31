'''
Evoque - managed eval-based freeform templating 
Copyright (C) 2007 Mario Ruggier <mario@ruggier.org>
Licensed under the Academic Free License version 3.0
URL: http://evoque.gizmojo.org/
'''
__url__ = "$URL: svn://gizmojo.org/pub/evoque/trunk/domain.py $"
__revision__ = "$Id: domain.py 1153 2009-01-20 11:43:21Z mario $"

import sys, logging

from evoque.collection import Collection
from evoque.evaluator import set_namespace_on_dict, xml

def get_log():
    logging.basicConfig(level=logging.INFO, 
        format="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s")
    return logging.getLogger("evoque")

# $begin{init}
class Domain(object):
    """ A registry of collections """
    
    def __init__(self, default_dir, 
            restricted=False, errors=3, log=get_log(),
            # defaults for Collections
            cache_size=0, auto_reload=60, slurpy_directives=True, 
            # defaults for Collections (and Templates)
            quoting="xml", input_encoding="utf_8", filters=[]):
        """
        default_dir: either(str, Collection)
            abs path, or actual default collection instance
        restricted: bool
            restricted evaluation namespace
        errors: int
            ["silent", "zero", "name", "render", "raise"]
        log: the logging.getLogger("evoque") logger; may be pre-initialized 
            and passed in, or adjusted as needed after initialization. 
            Default settings (via loggin.basicConfig()) are:
                handler=StreamHandler()
                level=logging.INFO
                format="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"
        
        # Defaults for Collections (and Templates)
        
        cache_size: int
            max number loaded templates in collection
            0 means unlimited loaded templates
        auto_reload: int
            min seconds to wait to check if needs reloading
            0 means check on every rendering
        slurpy_directives: bool
            consume all whitespace trailing a directive
        quoting: either("xml", "str", type)
            "xml" -> qpy.xml, "str" -> unicode
        input_encoding: str
            hint for how to decode template source
        filters: [callable]
            list of template post-evaluation filter functions
        """ 
        # $end{init}
        self.restricted = restricted 
        self.errors = errors
        self.log = log # the logging.getLogger("evoque") logger
        # defaults -- cascaded down to collections
        self.cache_size = cache_size 
        self.auto_reload = auto_reload 
        self.slurpy_directives = slurpy_directives
        self.quoting = quoting
        self.input_encoding = input_encoding 
        self.filters = filters
        #
        self.collections = {} # by collection name
        # default collection 
        if isinstance(default_dir, Collection):
            self.collections[default_dir.name] = default_dir
            self.default_collection = default_dir
        else:
            self.set_collection("", default_dir, cache_size, auto_reload, 
                    slurpy_directives, quoting, input_encoding, filters)
            self.default_collection = self.collections[""]
        #
        self.globals = {}
        self.globals['xml'] = xml
        if self.restricted:
            restrict_execution_namespace(self.globals)
    
    def set_on_globals(self, name, value):
        """ (name:str, value:any) -> None 
        """
        self.globals[name] = value
    
    def set_namespace_on_globals(self, name, obj, no_underscored=True):
        """ (name:either(str, None), obj:any, no_underscored:bool) -> None 
        If name is None, the obj's namespace will be set onto top-level.
        """
        set_namespace_on_dict(self.globals, name, obj, no_underscored)
    
    
    def get_collection(self, name=None):
        """ (name:either(None, str, Collection)) -> Collection 
        """
        if name is None:
            return self.default_collection
        if isinstance(name, Collection):
            name = name.name
        return self.collections[name] 
    
    def set_collection(self, name, dir, 
            cache_size=None, auto_reload=None, slurpy_directives=None, 
            quoting=None, input_encoding=None, filters=None):
        """ (name:str, dir:str, 
        cache_size:int, auto_reload:int, slurpy_directives:bool, 
        quoting:either(str, type), input_encoding:str, 
        filters:either(None, [callable])) -> None
        """
        if self.has_collection(name):
            raise ValueError(
                    "Domain already has a collection named [%s]" % (name))
        self.collections[name] = Collection(self, name, dir, 
                cache_size, auto_reload, slurpy_directives, quoting, 
                input_encoding, filters)
    
    def has_collection(self, name):
        """ (name:str -> bool 
        """
        return name in self.collections
    
    
    def get_template(self, name, src=None, collection=None, raw=None, 
            data=None, quoting=None, input_encoding=None, filters=None):
        """ Wraps Collection.get_template() 
        """
        return self.get_collection(collection).get_template(name, 
                src, raw, data, quoting, input_encoding, filters)
    
    def set_template(self, name, src=None, collection=None, raw=None, 
            data=None, from_string=True, 
            quoting=None, input_encoding=None, filters=None):
        """ Wraps Collection.set_template() 
        """
        self.get_collection(collection).set_template(name, src, 
                raw, data, from_string, quoting, input_encoding, filters)
    
    def has_template(self, name, collection=None):
        """ Wraps Collection.has_template() 
        """
        return self.get_collection(collection).has_template(name)
    

def restrict_execution_namespace(namespace):
    """ (namespace:dict) -> None
    Modifies the namespace dict parameter to add entries for builtins deemed 
    safe, and sets a dummy __builtins__ empty dict. 
    """
    # here type(__builtins__) is dict (not module as in the interpreter) 
    import inspect
    # In python 2.4, BaseException is not avialable
    BaseException_ = __builtins__.get('BaseException', Exception)
    for name, obj in __builtins__.items():
        if name in DISALLOW_BUILTINS:
            continue
        if inspect.isbuiltin(obj) or \
            (inspect.isclass(obj) and not issubclass(obj, BaseException_)) or \
            (obj in (None, True, False)):
                namespace[name] = obj
    namespace["__builtins__"] = {}

# Potentially unsafe __builtins__ in python 2.5 that will be removed from 
# execution namespace (in addition to all subclasses of BaseException).
# $begin{unsafe}
DISALLOW_BUILTINS = ["_", "__debug__", "__doc__", "__import__", "__name__",
    "buffer", "callable", "classmethod", "coerce", "compile", "delattr", "dir",
    "eval", "execfile", "exit", "file", "getattr", "globals", "hasattr", "id",
    "input", "isinstance", "issubclass", "locals", "object", "open", "quit", 
    "raw_input", "reload", "setattr", "staticmethod", "super", "type", "vars"]
# $end{unsafe}

# why "object" is included, see:
# http://groups.google.com/group/comp.lang.python/msg/5639e1b5cdac3ac2
