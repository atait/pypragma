from textwrap import dedent

import pragma
from .test_pragma import PragmaTest


global_x = 10


def global_f(y):
    return global_x + y


class TestLambdaLift(PragmaTest):
    def test_basic(self):
        x = 3

        @pragma.lift(imports=False)
        def f(y):
            return x + y

        self.assertRaises(TypeError, f, 1)
        self.assertEqual(f(1, x=2), 3)

    def test_defaults(self):
        x = 3

        @pragma.lift(defaults=True, imports=False)
        def f(y):
            return x + y

        self.assertEqual(f(1), 4)
        self.assertEqual(f(1, x=2), 3)

    def test_annotations(self):
        x = 3

        @pragma.lift(annotate_types=True, imports=False)
        def f(y):
            return x + y

        self.assertEqual(f(1, x=2), 3)
        import inspect
        self.assertIn(inspect.signature(f).parameters['x'].annotation, (int, 'int'))

    def test_source(self):
        x = 3

        @pragma.lift(annotate_types=True, defaults=True, return_source=True, imports=False)
        def f(y):
            return x + y

        result = dedent('''
        def f(y, *, x: int=3):
            return x + y
        ''')

        self.assertEqual(f.strip(), result.strip())

    def test_not_all_locals(self):
        x = 1
        y = 2

        @pragma.lift(return_source=True, imports=False)
        def f(z):
            return z + x

        result = dedent('''
        def f(z, *, x):
            return z + x
        ''')

        self.assertEqual(f.strip(), result.strip())

    def test_defaults_thoroughly(self):
        x = 1
        y = 2
        o = object()

        def f(z):
            yield o
            return x + y + z

        self.assertEqual(pragma.lift(annotate_types=True, defaults=True, return_source=True, imports=False)(f).strip(), dedent('''
        def f(z, *, o: object, x: int=1, y: int=2):
            yield o
            return x + y + z
        ''').strip())

        self.assertEqual(pragma.lift(annotate_types=['x'], defaults=['y'], return_source=True, imports=False)(f).strip(), dedent('''
        def f(z, *, o, x: int, y=2):
            yield o
            return x + y + z
        ''').strip())

        import ast
        self.assertSourceEqual(pragma.lift(annotate_types={'x': 'number'}, defaults={'y': ast.Num(5)}, return_source=True, imports=False)(f), '''
        def f(z, *, o, x: 'number', y=5):
            yield o
            return x + y + z
        ''')

    def test_no_closure(self):
        @pragma.lift(return_source=True, imports=False)
        def f(x):
            return x

        self.assertEqual(f.strip(), dedent('''
        def f(x):
            return x
        ''').strip())

    def test_method(self):
        class A:
            def __init__(self):
                self.y = 1

            @pragma.lift(imports=False)
            def f(self, x):
                return self.y + x

        a = A()
        something_else = lambda: None
        something_else.y = 2

        self.assertEqual(a.f(1), 2)
        self.assertEqual(A.f(something_else, 1), 3)

    def test_global(self):
        global_g = pragma.lift(return_source=True, lift_globals=['global_x'], defaults=True, imports=False)(global_f)

        self.assertEqual(global_g.strip(), dedent('''
        def global_f(y, *, global_x=10):
            return global_x + y
        ''').strip())

    def test_imports(self):
        import sys

        def f():
            return sys.version_info

        self.assertEqual(f(), sys.version_info)
        self.assertEqual(pragma.lift(f)(), sys.version_info)
        self.assertSourceEqual(pragma.lift(return_source=True, imports=True)(f), '''
        def f():
            import pragma
            import sys
            return sys.version_info
        ''')
        self.assertSourceEqual(pragma.lift(return_source=True, imports=['sys'])(f), '''
        def f():
            import sys
            return sys.version_info
        ''')

        import sys as pseudo_sys

        def g():
            return pseudo_sys.version_info

        self.assertSourceEqual(pragma.lift(return_source=True, imports=True)(g), '''
        def g():
            import pragma
            import sys as pseudo_sys
            return pseudo_sys.version_info
        ''')

    def test_docstring(self):
        @pragma.lift(return_source=True, imports=True)
        def f(x):
            'some docstring'
            return x + 1

        self.assertSourceEqual(f, '''
        def f(x):
            """some docstring"""
            import pragma
            return x + 1
        ''')


