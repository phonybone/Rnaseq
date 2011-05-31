'''
Evoque - managed eval-based freeform templating 
Copyright (C) 2007 Mario Ruggier <mario@ruggier.org>
Licensed under the Academic Free License version 3.0
URL: http://evoque.gizmojo.org/
'''
__url__ = "$URL: svn://gizmojo.org/pub/evoque/trunk/template.py $"
__revision__ = "$Id: template.py 1148 2009-01-19 17:21:13Z mario $"

import time
from os import stat
from os.path import join, exists, normpath
from evoque.decodeh import decode, decode_from_file
from evoque.evaluator import Evaluator, RestrictedEvaluator, cascaded, \
        specified_kwargs, xml, unistr, string

def get_qsclass(quoting):
    """ (quoting:either(str, type) -> type 
    """
    if quoting == "xml":
        if xml is None:
            raise ValueError(
                    "Quoting [%s] requires qpy to be installed" % (quoting))
        return xml
    elif quoting == "str":
        return unistr
    elif type(quoting) is type(Template):
        # already a class
        return quoting
    raise ValueError('Unknown quoting [%s]. Must be "str", "xml" or a '
            'Quoted-No-More String Class.' % (quoting))

def parse_locator(src):
    """ (src:str) -> [pathfile:str, label:either(str, None)] 
    """
    pathfile_label = src.split('#')
    if len(pathfile_label)==1:
        pathfile_label.append(None)
    if len(pathfile_label)!=2:
        raise ValueError('Malformed src: %s' % (src))
    return pathfile_label


# $begin{init}
class Template(object):
    """ An Evoque template 
    """
    
    def __init__(self, domain, name, src=None, collection=None, 
            raw=None, data=None, from_string=False, 
            # defaults from Collection
            quoting=None, input_encoding=None, filters=None):
        """
        domain: either(str, Domain)
            abs path, or actual domain instance
        name: str
            if no src this is collection-root-relative locator
        src: either(None, str)
            (file-based) collection-root-relative locator
            (from_string=True) template source string
        collection: either(None, str, Collection)
            None implies default collection, else 
            str/Collection refer to an existing collection
        raw: bool 
            if raw, do not compile the template source 
        data: either(None, dict) 
            default data for template evaluation 
        from_string: bool
            when True src must specify the template source
        
        For more on defaults from Collection init parameters, see the 
        docstring in collection.Collection.__init__().
        
        Preferred way to create a new template:
            domain.{get_template(), set_template()}
        """ 
        # $end{init}
        # domain, ensure one is available
        if domain is None:
            raise ValueError("A Template cannot have a None domain")
        if isinstance(domain, string):
            # creates domain with the "" collection
            from evoque.domain import Domain
            domain = Domain(domain, 
                        **specified_kwargs(self.from_collection, vars()))
        # collection
        self.collection = domain.get_collection(collection)
        # name, qsclass, input_encoding, filters, raw, data
        if name is None:
            raise ValueError("A Template cannot have a None name")
        self.qsclass = get_qsclass(cascaded(quoting, self.collection.quoting))
        self.input_encoding = cascaded(input_encoding, 
                self.collection.input_encoding)
        self.filters = cascaded(filters, self.collection.filters)
        self.raw = raw or False
        self.data = data
        
        # src (stored as either .file or .ts_raw), file, label
        self.ts_raw = None
        self.last_modified = None
        if not name and src is None:
            raise ValueError("Template must specify a locator (name/src)")
        self.file, self.label = None, None
        if from_string:
            # src must hold the raw string
            self.label = parse_locator(name)[1]
            # from_string templates may only be loaded once
            self.ts_raw = self.redecode_from_string(src)
            self.last_modified = time.time()
        else:
            # name or src (or combination of both) must hold the locator
            if name:
                # fragment label from name takes precedence: 
                # name, src = name#label, path/file.ext#label2
                self.file, self.label = parse_locator(name)
            if src is not None:
                # file from src takes precedence
                self.file, label = parse_locator(src)
                if self.label is None:
                    self.label = label
            if not exists(self.get_abspath()):
                raise ValueError("File [%s] not found for template " 
                    '[name="%s" collection="%s"]. Template File locator ' 
                    "(name/src) must be relative to collection root." % (
                                self.file, name, self.collection.name))
        
        # never modify a user-specified name
        self.name = name 
        
        # ts_raw + last_modified (file)
        self.eval_overlay, self.labels, self.prefer = None, None, None
        self.test_data, self.ts, self.ts_raw_frag = None, None, None
        self.refresh()
        if self.prefer:
            # may need to refresh still if different preferances than defaults
            refresh = (self.qsclass, self.raw)
            self.qsclass = get_qsclass(cascaded(quoting, 
                    self.prefer.get("quoting"), self.collection.quoting))
            self.raw = cascaded(raw, self.prefer.get("raw"), self.raw)
            self.filters = cascaded(filters, self.prefer.get("filters"), 
                    self.collection.filters)
            if refresh != (self.qsclass, self.raw):
                self.refresh()
        
        try:
            self.collection.cache.get(name)
            raise ValueError(("A template named [%s] is already defined "
                    "in collection [%s]") % (name, self.collection.name))
        except KeyError:
            self.collection.cache.set(name, self)
        
        if not domain.restricted:
            self.evaluator = Evaluator(self)
        else:
            self.evaluator = RestrictedEvaluator(self)
    
    from_collection = ("quoting", "input_encoding", "filters")
    
    overlay_spaces = { "positive":True, "negative":False }
    def get_space_overlay(self):
        """ () -> (overlay:dict, space:boolean)
        Assumption: self.eval_overlay is not None
        """
        overlay = eval("dict(%s)"%(self.eval_overlay), 
            self.collection.domain.globals, self.evaluator.locals)
        space = self.overlay_spaces[overlay.pop("space", "positive")]
        # ensure only suppoted subset of get_template() kwargs are present
        for key in overlay:
            if key not in ("name", "src", "collection"):
                raise SyntaxError("$overlay{%s} : unexpected kwarg [%s]" % (
                        self.eval_overlay, key))
        return space, overlay
    
    def get_overlaid(self):
        """ () -> Template
        Dynamically looks up and retrieves an overlaid template, guaranteeing
        correct cache checking and/or reloading as per configuration in place.
        
        Assumption: caller has already verified that this template is an 
        overlay, i.e. that self.eval_overlay is not None
        """
        space, overlay = self.get_space_overlay()
        return self.collection.domain.get_template(**overlay)
    
    def get_overlaid_ts(self):
        """ () -> qsclass
        Get the template string for a positive overlay template, i.e. 
        the negative space from a template further down the overlay chain. 
        
        Assumption: caller has already verified that this template is an 
        overlay, i.e. that self.eval_overlay is not None
        """
        overlaid = self.get_overlaid()
        if overlaid.eval_overlay is not None:
            # overlaid is also an overlay -- eval space, overlay in own context
            o_space, o_overlay = overlaid.get_space_overlay()
            if o_space is True:
                # overlaid is also a positive overlay i.e. its negative space
                # is supplied by an overlaid template further below
                return overlaid.get_overlaid_ts()
        return overlaid.ts
    
    def evoque(self, locals=None, raw=None, quoting=None, **kw):
        """ (locals:dict, raw:bool, quoting:either(str, type)) -> qsclass
        Render template, as an instance of the specified Quoted-No-More string
        class. If raw, return raw string, else update locals and evaluate.
        """
        qsclass = quoting and get_qsclass(quoting) or self.qsclass
        evaluator = self.evaluator
        evaluator.qsclass = qsclass # qsclass to use for *this* evoque'ation
        evaluator.qsjoin = qsclass("").join
        if raw or self.raw:
            if self.label: 
                # we use cached extracted ts_raw 
                return self.filtered(qsclass(self.ts_raw_frag))
            return self.filtered(qsclass(self.ts_raw))
        # always work on a fresh locals -- copy "own" if necessary 
        if locals is not None:
            locals = locals.copy()
        else:
            locals = {}
        if self.data:
            for key in self.data:
                if not key in locals:
                    locals[key] = self.data[key]
        if kw:
            locals.update(kw)
        # permanent locals
        locals.update(evaluator.permalocals) 
        # use customized locals for *this* evaluation
        evaluator.locals = locals
        # process overlay
        if self.eval_overlay is not None:
            # is an overlay, if +ve then the -ve space is supplied by overlaid
            o_space, o_overlay = self.get_space_overlay()
            if o_space is True:
                return self.filtered(qsclass(self.get_overlaid_ts()) % evaluator)
        return self.filtered(qsclass(self.ts) % evaluator)
    
    def filtered(self, rs):
        """ (rs:str) -> type(rs) 
        """
        if self.filters:
            qsclass = type(rs)
            for f in self.filters:
                rs = qsclass(f(rs))
                if not type(rs) is qsclass:
                    rs = qsclass(rs)
        return rs
    
    def test(self):
        """ () -> yields(qsclass)
        Generator method, to be called by application code to test a template
        with own data. Run through the list of test dicts extracted from the 
        template. Sets errors to raise exceptions, and resets it back on exit.

        It is recommended to provide a cascaded sequence of test dicts such
        that every logical branch of the template is exercised.
        May also be used to prime the self.evaluator.codes cache. 
        """
        if not self.raw:
            _errors = self.collection.domain.errors
            # always start with self.data, if any is set 
            d = (self.data and self.data.copy()) or {}
            # if no tests, attempt eval with self.data (that may be no data)
            for testd in self.test_data or [d]:
                d.update(testd)
                try:
                    self.collection.domain.errors = 4 # force raise
                    result = self.evoque(d)
                finally:
                    self.collection.domain.errors = _errors
                yield result
    
    def is_modified_since(self):
        """ (abspath:str) -> bool 
        Checks self.file st_mtime to see if file has been modified since last 
        check. Updates self.last_modified with value read from file system.
        """
        if self.file is None:
            return False
        if not time.time()-self.last_modified > self.collection.auto_reload:
            return False
        last_modified = self.last_modified
        self.last_modified = stat(self.get_abspath()).st_mtime
        return (last_modified < self.last_modified)
    
    def get_abspath(self):
        """ () -> abspath:str
        Return absolute path for self.file, ensuring that it is indeed 
        within collection root.
        """
        path = normpath(join(self.collection.dir, self.file))
        if not path.startswith(self.collection.dir):
            raise LookupError("Template file [%s] not within collection [%s]"
                        % (path, self.collection.name))
        return path
    
    def redecode_from_string(self, src):
        """ (src:str) -> ts_raw:str
        Re-decode raw template string from src 
        """
        if src is None:
            raise ValueError("Template from string may not have src=None")
        if self.file is not None:
            raise ValueError("Template is file-based")
        return decode(src, enc=self.input_encoding)
    def redecode(self):
        """ () -> ts_raw:str
        Re-decode raw template string from file 
        """
        #+ if "#..." then just use caller's ts_raw
        return decode_from_file(self.get_abspath(), enc=self.input_encoding)
    
    def refresh(self):
        """ () -> None. (Re-)set the following attributes:
            ts_raw (file templates only) 
            last_modified (file templates only)
            ts_raw_frag (nested templates only)
            labels (not raw)
            prefer (not raw)
            eval_overlay (not raw)
            test_data (not raw)
            ts (not raw)
        """
        if self.file is not None:
            self.ts_raw = self.redecode()
            self.last_modified = time.time()
        trans = self.collection.translator
        if self.label is not None: 
            # cache extract ts_raw (when different than ts_raw)
            self.ts_raw_frag = trans.extract_nested(self.ts_raw, self.label)
        if not self.raw:
            # translate from $-syntax to %-syntax
            # als extracts several template attributes
            self.labels, self.prefer, self.eval_overlay, self.test_data, \
                    self.ts = trans.translate(self.ts_raw_frag or self.ts_raw)
        # in the case of preferred data that has changed, update it if it 
        # has not been explicitly passed in as an evoque() parameter
        if self.prefer and self.prefer.get("data"):
            if self.data:
                self.data.update(self.prefer.get("data"))
            else:
                self.data = self.prefer.get("data")
    
    def unload(self):
        """ Unload self from collection, rendering each template in the 
        instance hierarchy unusable. 
        Thus, re-doing a get_template() with same parameters will create and 
        return a new Template instance.
        """
        if self.labels:
            for label in self.labels:
                subname = "%s#%s" % (self.name.split("#")[0], label)
                if self.collection.has_template(subname):
                    self.collection.get_template(subname).unload()
        self.collection.cache.unset(self.name)
        self.collection = None
    
