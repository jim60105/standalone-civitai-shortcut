from scripts.civitai_manager_libs.http_client import ParallelImageDownloader


class DummyProgress:
    """Dummy progress callback to capture calls."""

    def __init__(self):
        self.calls = []

    def __call__(self, done, total, desc):
        self.calls.append((done, total, desc))


def test_progress_throttling_mechanism(monkeypatch):
    # Simulate time progression for throttling logic
    times = [0.0, 0.05, 0.09, 0.15, 0.16]
    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.time.time",
        lambda: times.pop(0),
    )
    downloader = ParallelImageDownloader()
    downloader.total_count = 5
    downloader.completed_count = 0
    downloader.last_progress_update = 0.0
    downloader.pending_update = False

    progress = DummyProgress()
    # Call update_progress multiple times
    for _ in range(5):
        downloader._update_progress(progress)

    # Only two updates should be sent: one after throttle interval, and the final update
    assert progress.calls == [
        (4, 5, "Downloading image 4/5"),
        (5, 5, "Downloading image 5/5"),
    ]


def test_final_progress_always_sent():
    downloader = ParallelImageDownloader()
    downloader.completed_count = 3
    downloader.total_count = 3
    downloader.pending_update = True

    progress = DummyProgress()
    downloader._send_final_progress_update(progress)
    assert progress.calls == [(3, 3, "Downloaded 3/3 images")]


def test_periodic_update_timer(monkeypatch):
    # Monkeypatch threading.Timer to invoke callback immediately for testing
    timers = []
    invocations = {'count': 0}

    def dummy_timer(interval, func):
        class DummyTimer:
            def __init__(self_inner):
                pass

            def start(self_inner):
                # Invoke callback only once to prevent recursive scheduling
                if invocations['count'] == 0:
                    invocations['count'] += 1
                    func()

            def cancel(self_inner):
                timers.append("cancelled")

        return DummyTimer()

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.threading.Timer",
        dummy_timer,
    )

    downloader = ParallelImageDownloader()
    downloader.completed_count = 1
    downloader.total_count = 3
    downloader.pending_update = True

    progress = DummyProgress()
    timer = downloader._start_progress_timer(progress)
    # periodic_update should have been called once immediately
    assert progress.calls == [(1, 3, "Downloading image 1/3")]
    downloader._stop_progress_timer(timer)
    assert timers == ["cancelled"]


def test_no_mockprogress_dependency(monkeypatch):
    # Ensure on_civitai_internet_url_txt_upload uses the provided progress object
    from scripts.civitai_manager_libs.civitai_shortcut_action import (
        on_civitai_internet_url_txt_upload,
    )
    import scripts.civitai_manager_libs.civitai_shortcut_action as cs_action

    fake_prog = object()
    called = {}

    def fake_upload(urls, register_info_only, progress):
        called['progress'] = progress
        return []

    monkeypatch.setattr(
        cs_action.ishortcut_action,
        'upload_shortcut_by_urls',
        fake_upload,
    )
    # Invoke handler with a URL to trigger upload_shortcut_by_urls
    _ = on_civitai_internet_url_txt_upload("http://example.com", False, progress=fake_prog)
    assert called.get('progress') is fake_prog
