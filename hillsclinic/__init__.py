# Monkey-patch modelsearch to avoid Python 3.12 typing bug
def _patch_modelsearch():
    try:
        import modelsearch.signal_handlers as handlers
        # Replace the signal handler with a no-op
        def noop_handler(*args, **kwargs):
            pass
        handlers.post_save_signal_handler = noop_handler
        handlers.post_delete_signal_handler = noop_handler
    except Exception:
        pass

_patch_modelsearch()