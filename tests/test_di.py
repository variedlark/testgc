import unittest

from core.di import ServiceContainer


class TestDI(unittest.TestCase):
    def test_singleton_and_factory(self):
        sc = ServiceContainer()
        sc.register_singleton('a', 'value')
        self.assertEqual(sc.resolve('a'), 'value')

        def factory():
            return []

        sc.register_factory('list', factory)
        instance1 = sc.resolve('list')
        instance2 = sc.resolve('list')
        # factory is cached as singleton on first resolve
        self.assertIs(instance1, instance2)

        sc.unregister('a')
        with self.assertRaises(KeyError):
            sc.resolve('a')


if __name__ == "__main__":
    unittest.main()
