import io
import os
import unittest
from pyramid import testing

class TestResponse(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.response import Response
        return Response
        
    def test_implements_IResponse(self):
        from pyramid.interfaces import IResponse
        cls = self._getTargetClass()
        self.assertTrue(IResponse.implementedBy(cls))

    def test_provides_IResponse(self):
        from pyramid.interfaces import IResponse
        inst = self._getTargetClass()()
        self.assertTrue(IResponse.providedBy(inst))

class TestFileResponse(unittest.TestCase):
    def _makeOne(self, file, **kw):
        from pyramid.response import FileResponse
        return FileResponse(file, **kw)

    def _getPath(self):
        here = os.path.dirname(__file__)
        return os.path.join(here, 'fixtures', 'minimal.txt')

    def test_with_content_type(self):
        path = self._getPath()
        r = self._makeOne(path, content_type='image/jpeg')
        self.assertEqual(r.content_type, 'image/jpeg')
        r.app_iter.close()

    def test_without_content_type(self):
        path = self._getPath()
        r = self._makeOne(path)
        self.assertEqual(r.content_type, 'text/plain')
        r.app_iter.close()

class TestFileIter(unittest.TestCase):
    def _makeOne(self, file, block_size):
        from pyramid.response import FileIter
        return FileIter(file, block_size)

    def test___iter__(self):
        f = io.BytesIO(b'abc')
        inst = self._makeOne(f, 1)
        self.assertEqual(inst.__iter__(), inst)

    def test_iteration(self):
        data = b'abcdef'
        f = io.BytesIO(b'abcdef')
        inst = self._makeOne(f, 1)
        r = b''
        for x in inst:
            self.assertEqual(len(x), 1)
            r+=x
        self.assertEqual(r, data)

    def test_close(self):
        f = io.BytesIO(b'abc')
        inst = self._makeOne(f, 1)
        inst.close()
        self.assertTrue(f.closed)

class Test_patch_mimetypes(unittest.TestCase):
    def _callFUT(self, module):
        from pyramid.response import init_mimetypes
        return init_mimetypes(module)

    def test_has_init(self):
        class DummyMimetypes(object):
            def init(self):
                self.initted = True
        module = DummyMimetypes()
        result = self._callFUT(module)
        self.assertEqual(result, True)
        self.assertEqual(module.initted, True)
        
    def test_missing_init(self):
        class DummyMimetypes(object):
            pass
        module = DummyMimetypes()
        result = self._callFUT(module)
        self.assertEqual(result, False)


class TestResponseAdapter(unittest.TestCase):
    def setUp(self):
        registry = Dummy()
        self.config = testing.setUp(registry=registry)

    def tearDown(self):
        self.config.end()

    def _makeOne(self, *types_or_ifaces):
        from pyramid.response import response_adapter
        return response_adapter(*types_or_ifaces)

    def test_register_single(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.adapters, [(foo, IFoo)])

    def test_register_multi(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne(IFoo, IBar)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.adapters, [(foo, IFoo), (foo, IBar)])

    def test___call__(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo)
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached,
                         [(foo, dec.register, 'pyramid')])

class Dummy(object):
    pass

class DummyConfigurator(object):
    def __init__(self):
        self.adapters = []

    def add_response_adapter(self, wrapped, type_or_iface):
        self.adapters.append((wrapped, type_or_iface))

class DummyVenusian(object):
    def __init__(self):
        self.attached = []

    def attach(self, wrapped, fn, category=None):
        self.attached.append((wrapped, fn, category))

        
