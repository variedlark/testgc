def register(game):
    print("[sample_plugin] register called")

    def on_level_start(payload):
        print("[sample_plugin] level_start event:", payload)

    # subscribe to a conceptual event; projects can emit these via EventBus
    try:
        game.event_bus.subscribe("level_start", on_level_start)
    except Exception:
        # be tolerant if the host API is not present during tests
        pass


def unregister():
    print("[sample_plugin] unregister called")
