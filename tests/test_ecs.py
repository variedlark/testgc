import unittest

from core.ecs import World


class Position:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class TestECS(unittest.TestCase):
    def test_entity_component_lifecycle(self):
        w = World()
        e = w.create_entity()
        pos = Position(10, 20)
        w.add_component(e, pos)
        self.assertIs(w.get_component(e, Position), pos)

        q = w.query(Position)
        self.assertIn(e, q)

        w.remove_component(e, Position)
        self.assertIsNone(w.get_component(e, Position))

        w.add_component(e, pos)
        w.remove_entity(e)
        # entity removed, should not appear in queries
        self.assertNotIn(e, w.query())


if __name__ == "__main__":
    unittest.main()
