import datetime
from typing import Optional
from netex import *

def getRef(obj: object, klass=None):
    if klass == None:
        asobj = type(obj).__name__ + 'RefStructure'
        klass = globals()[asobj]
    instance = klass()

    if hasattr(obj, 'id'):
        instance.ref = obj.id
    elif hasattr(obj, 'ref'):
        instance.ref = obj.ref

    name = type(obj).__name__
    if hasattr(obj, 'Meta') and hasattr(obj.Meta, 'name'):
        name = obj.Meta.name
    elif name.endswith('RefStructure'):
        name = name.replace('RefStructure', 'Ref')

    if hasattr(obj, 'version'):
        instance.version = obj.version

    kname = klass.__name__
    meta_kname = klass.__name__
    if hasattr(klass, 'Meta') and hasattr(klass.Meta, 'name'):
        meta_kname = klass.Meta.name

    if not (kname.startswith(name) or meta_kname.startswith(name)):
        instance.name_of_ref_class = name
    return instance

def getFakeRef(id: str, klass, version: str):
    if id is None:
        return None

    instance = klass()
    instance.ref = id
    instance.version = version
    return instance

def getIdByRef(obj: object, codespace: Codespace, ref: str):
    name = type(obj).__name__
    if hasattr(obj.Meta, 'name'):
        name = obj.Meta.name
    return "{}:{}:{}".format(codespace.xmlns, name, str(ref).replace(':', '-'))

from operator import attrgetter

def getIndex(l, attr=None):
    if not attr:
        return {x.id:x for x in l }

    f = attrgetter(attr)
    return  {f(x):x for x in l }

def setIdVersion(obj: object, codespace: Codespace, id: str, version: Optional[Version]):
    name = type(obj).__name__
    if hasattr(obj.Meta, 'name'):
        name = obj.Meta.name
    obj.id = "{}:{}:{}".format(codespace.xmlns, name, str(id).replace(':', '-'))
    if version:
        obj.version = version.version
    else:
        obj.version = "any"

def getVersionOfObjectRef(obj: object):
    return VersionOfObjectRefStructure(name_of_ref_class=type(obj).__name__, ref=obj.id)

def getBitString2(available: list, f_orig, t_orig):
    l = sorted(available)
    f = f_orig

    out = ''
    while f <= t_orig:
        out += str(int(f in l))
        f += datetime.timedelta(days=1)

    return out

def getOptionalString(name: str):
    if name:
        return MultilingualString(name)
