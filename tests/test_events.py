import unittest

from core.events import EventBus


class TestEventBus(unittest.TestCase):
    def test_priority_once_and_pending(self):
        bus = EventBus()
        calls = []

        def low(payload):
            calls.append(("low", payload))

        def high(payload):
            calls.append(("high", payload))

        bus.subscribe("evt", low, priority=1)
        bus.subscribe_once("evt", high, priority=5)

        bus.emit_later("evt", 1)
        self.assertEqual(bus.pending_count(), 1)
        bus.process_pending()
        self.assertEqual(bus.pending_count(), 0)
        self.assertEqual(calls, [("high", 1), ("low", 1)])

        calls.clear()
        bus.emit("evt", 2)
        self.assertEqual(calls, [("low", 2)])

    def test_clear_event_removes_pending(self):
        bus = EventBus()
        bus.emit_later("a", 1)
        bus.emit_later("b", 2)
        self.assertEqual(bus.pending_count(), 2)
        bus.clear("a")
        self.assertEqual(bus.pending_count(), 1)


if __name__ == "__main__":
    unittest.main()
