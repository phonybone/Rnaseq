'''
Evoque - managed eval-based freeform templating 
Copyright (C) 2007 Mario Ruggier <mario@ruggier.org>
Licensed under the Academic Free License version 3.0
URL: http://evoque.gizmojo.org/
'''
__url__ = "$URL: svn://gizmojo.org/pub/evoque/trunk/evaluator.py $"
__revision__ = "$Id: evaluator.py 1153 2009-01-20 11:43:21Z mario $"

import sys, re, traceback, pprint

# Standardize on types for both py2 and py3
if sys.version < '3':
    unistr, string = unicode, basestring
    from cStringIO import StringIO
else:
    unistr, string = str, str
    from io import StringIO

try:
    from qpy import xml
except ImportError:
    xml = None

def cascaded(*args):
    """ (args:any) -> arg : not None
    Returns first non-None arg.
    """
    for arg in args:
        if arg is not None:
            return arg

def specified_kwargs(names=(), items={}):
    """ (names:tuple(str), items:dict) -> dict
    Returns a dict with the *names* subset of entries in *items* for which 
    the value is not None.
    """
    return dict([ (n, items[n]) for n in names if items[n] is not None ])

def set_namespace_on_dict(d, name, obj, no_underscored=True):
    """ (d:dict, name:either(str, None), obj:object, no_underscored:bool) 
                                                                    -> None
    Sets each key in obj.__all__ or in dir(obj) as key=getattr(object, key) 
    in the specified dict. If no_underscored, then exclude "private" 
    (leading "__") and "protected" (leading "_") attributes.
    If name is None, the obj's namespace will be set onto top-level.
    """
    if name is not None:
        if not name in d:
            d[name] = bunch() # bunch : dict w. dotted access
        d = d[name]
    names = getattr(obj, "__all__", None) or dir(obj)
    for name in names:
        if not (name.startswith('_') and no_underscored):
            d[name] = getattr(obj, name)


class Evaluator(object):
    """ Evaluator of code inside of the Template's string 
    """
    
    def __init__(self, template):
        """ (template:Template) """
        self.template = template
        self.globals = self.template.collection.domain.globals
        # errors = self.template.collection.domain.errors
        self.locals = {} # reset liberally during evaluations
        self.codes = {}
        # entries here guaranteed to be always available during evoque'ation 
        # of *this* template
        self.permalocals = {}
        self.permalocals['_evoque_if'] = self._evoque_if
        self.permalocals['_evoque_for'] = self._evoque_for
        self.permalocals['_evoque_for_mup'] = self._evoque_for_mup
        self.permalocals['evoque'] = self.evoque
        self.permalocals['inspect'] = self.inspect
        # template.evoque() sets qsclass on each evoque'ation
        self.qsclass = None
        self.qsjoin = None
        # __getitem__ as closure offers a minor speed improvement
        type(self).__getitem__ = self.get__getitem__()
        
    def get__getitem__(self):
        _g, _codes, _eval, _compile = self.globals, self.codes, eval, compile
        def __getitem__(self, name):
            try:
                return _eval(_codes[name], _g, self.locals)
            except:
                # We want to catch **all** evaluation errors!
                # Some exceptions that have been raised here are:
                # KeyError, NameError, AttributeError, SyntaxError, 
                # ValueError, TypeError, IOError, ...
                #
                # Special case: if KeyError is coming from self.codes[name]
                # lookup, then we add the compiled entry and try again:
                if not name in _codes:
                    _codes[name] = _compile(name, '<string>', 'eval')
                    return self.__getitem__(name)
                return self.handle_get_error(name)
        return __getitem__
    
    def handle_get_error(self, name):
        """ (name:str) -> str | raise 
        """
        # 0:silent, 1:zero, 2:name, 3:render, 4:raise
        etype, exc, tb = sys.exc_info() 
        errors = self.template.collection.domain.errors
        indication = 'EvalError(%s)' % (name)
        description = '%s: %s: %s: %s' % (etype.__name__, exc, 
                traceback.format_tb(tb)[-1], indication)
        # always log errors
        self.template.collection.domain.log.error(description) 
        if errors > 3:
            raise etype('%s: %s' % (indication, exc))
        elif errors > 2:
            return '[%s]' % (description)
        elif errors > 1:
            return '[%s]' % (indication)
        elif errors > 0:
            return '' #+ 
        else:
            return '' 
    
    # evoque 
    
    def evoque(self, name, src=None, collection=None, raw=None, 
                quoting=None, input_encoding=None, filters=None, **kw):
        """ Combines the functionality of Collection.get_template() and 
        Template.evoque() for use from within a template. 
        
        Internally, it is a dispatcher method that determines which 
        template.evoque() to call and to dispatch to it -- *all* template 
        evoque'ations without exception go through the template instance's 
        evoque() method. 
        """
        template, locals = self.template, self.locals
        if collection is None:
            # use "own" collection
            collection = template.collection
        else:
            collection = template.collection.domain.get_collection(collection)
        if name.startswith("#") and collection==template.collection:
            # a locally addressed template
            if name[1:] in template.labels:
                # template supplies a definition for this template
                # just normalize name, using caller's basename
                name = template.name.split("#")[0] + name
            elif template.eval_overlay is not None:
                # template is an overlay (positive or negative)
                if name.startswith("##"):
                    # will recurse, chop away one leading "#"
                    name = name[1:]
                # transfer handling to lower level template's evaluator
                locals.update(kw)
                return template.get_overlaid().evaluator.evoque(name, src, 
                        collection, raw, quoting, input_encoding, **locals)
            # a from_string template may need yet be loaded
            if not collection.has_template(name):
                if src is None:
                    if template.file is None: # from_string
                        src = template.ts_raw
                        collection.set_template(name, src, raw, None, 
                                True, quoting, input_encoding, filters)
                    else:
                        src = template.file
        elif src and src.startswith("#") and collection==template.collection:
            if template.file is not None: # file-based
                # a named file-based template with a "local" src; normalize
                src = template.file + src
        # Pass the *current* execution context. If not previously loaded, then 
        # the template is *loaded* with (raw=raw, quoting=quoting) otherwise 
        # it is only *rendered* with (raw=raw, quoting=quoting). 
        return collection.get_template(name, src, raw, None, quoting,
                input_encoding, filters).evoque(locals, raw, quoting, **kw)
    
    # if 
    
    def _evoque_if(self, if_cts, else_ts):
        """ (if_cts:((cond, str),), else_ts:str) -> qsclass 
        """
        for c, ts in if_cts:
            if c:
                return self.qsclass(ts) % self 
        return self.qsclass(else_ts) % self
    
    # for 
    
    def _evoque_for(self, item, iterator, item_ts, else_ts):
        """ (item:str, iterator, item_ts:str, else_ts:str) -> qsclass
        SingleUnPack for loop handler (having a single item to unpack).
        """
        qs_item_ts, d, acc = self.qsclass(item_ts), self.locals, []
        append = acc.append
        for value in iterator:
            d[item] = value
            append(qs_item_ts % self)
        return self.qsjoin(acc) or self.qsclass(else_ts) % self
    
    def _evoque_for_mup(self, items, iterator, item_ts, else_ts):
        """ (item:[str], iterator, item_ts:str, else_ts:str) -> qsclass
        MultipleUnPack for loop handler (having multiple items to unpack).
        """
        qs_item_ts, d, acc = self.qsclass(item_ts), self.locals, []
        mup_set_on_dict, append = self._evoque_for_mup_set_on_dict, acc.append
        for values in iterator:
            mup_set_on_dict(d, items, values)
            append(qs_item_ts % self)
        return self.qsjoin(acc) or self.qsclass(else_ts) % self
        
    def _evoque_for_mup_set_on_dict(self, d, items, values):
        """ (d:dict, items:sequence, values:sequence(any)) -> None
        Constraint: the "compoundedness" of the type for each value must 
        correspond to the "compoundedness" of the type for each item, 
        i.e. if item is a 3-tuple then value must unpack to a 3-tuple, etc.
        Assumption: if an item is not a string, then it is a sequence.
        """
        for n, v in zip(items, values):
            if not isinstance(n, string):
                self._evoque_for_mup_set_on_dict(d, n, v)
            else:
                d[n] = v

    #
    
    def inspect(self, output=True):
        """ (output:bool) -> either(None, str) 
        Pretty print -- to output or (if output is False) via 
        domain.log.info() -- an overview of the evaluation namespace, 
        namely the context's globals and the locals and the template's 
        expressions needing evaluation.
        
        Templates should wrap the output of this expression appropriately
        e.g. using  <div class="code"> if calling from an HTML context.
        """
        out = StringIO()
        pp = pprint.PrettyPrinter(stream=out, indent=4)
        out.write("INSPECT [%s] start:" % self.template.name)
        def pp_dict(label, d):
            out.write("INSPECT [%s] %s [%s] :" % (
                    self.template.name, label, id(d)))
            for key, value in d.items():
                if not key.startswith("__builtin"):
                    out.write("%s: " % repr(key)) 
                    pp.pprint(value)
        pp_dict("GLOBALS", self.globals)
        pp_dict("LOCALS", self.locals)
        pp_dict("EXPRESSIONS", self.codes)
        out.write("INSPECT [%s] stop." % self.template.name)
        if output:
            return self.qsclass(out.getvalue())
        self.template.collection.domain.log.info(out.getvalue())

# for why the restricted_scan, see:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/689ea92183b91f06/
#
class RestrictedEvaluator(Evaluator):
    """ Evaluator for Restricted Execution 
    """
    def get__getitem__(self):
        # $begin{restricted_scan}
        restricted_scan = re.compile(r"|\.\s*".join([
            "__", "func_", "f_", "im_", "tb_", "gi_", "throw"]), re.DOTALL)
        # $end{restricted_scan}
        _g, _codes, _eval, _compile = self.globals, self.codes, eval, compile
        def __getitem__(self, name):
            # Disallow evaluaton of any string containing "__"
            if restricted_scan.search(name):
                try:
                    raise LookupError(name)
                except:
                    return self.handle_get_error(name)
            try:
                return _eval(_codes[name], _g, self.locals)
            except:
                # We want to catch **all** evaluation errors!
                # Some exceptions that have been raised here are:
                # KeyError, NameError, AttributeError, SyntaxError, 
                # ValueError, TypeError, IOError, ...
                #
                # Special case: if KeyError is coming from self.codes[name]
                # lookup, then we add the compiled entry and try again:
                if not name in _codes:
                    _codes[name] = _compile(name, '<string>', 'eval')
                    return self.__getitem__(name)
                return self.handle_get_error(name)
        return __getitem__

class bunch(dict):
    """ A dictionary-bunch of values, with convenient dotted access. 

    Limitations: 
    - do not use any existing dict attribute name as key, as this will 
      override the attribute and thus break the dict. 
    - keys must be valid object attribute names.
    - initialization supports only keywords arguments (the dict class offers
      a bigger variety of how a dict could be initialized).
    
    Inspiration: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308
    """
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self
    
