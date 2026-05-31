"""JS scenarios + assertions for MusicKit JS end-to-end tests (PLAN §11.2).

Each scenario is a JS string passed to ``page.evaluate`` and an assertion
function operating on the result. Both are shared between
``test_musickit_sync.py`` and ``test_musickit_async.py``.

The first scenario (``LOAD_AND_CONFIGURE``) injects MusicKit JS via a script
tag, waits for the ``musickitloaded`` event, calls ``MusicKit.configure``,
and stashes the instance on ``window.__mk`` for subsequent scenarios. It also
installs a ``window.fetch`` recorder on ``window._fetches`` so that playback
scenarios can verify which mocked endpoints were actually exercised.
"""

from __future__ import annotations

from typing import TypedDict

from tests.constants import MUSICKIT_JS_URL


class _ConfigureResult(TypedDict, total=False):
    isAuthorized: bool
    storefrontId: str
    version: str


class _QueueItemResult(TypedDict, total=False):
    id: str
    type: str
    title: str
    artistName: str
    albumName: str


class _AuthorizeResult(TypedDict, total=False):
    isAuthorized: bool
    token: str


class _UnauthorizeResult(TypedDict, total=False):
    before: bool
    after: bool


class _PlayingResult(TypedDict, total=False):
    states: list[int]
    fetches: list[str]


class _PlaybackErrorResult(TypedDict, total=False):
    errorCode: str
    status: int
    name: str
    thrown: str
    fetches: list[str]


class _SkipToNextResult(TypedDict, total=False):
    firstNowPlaying: str
    secondNowPlaying: str
    fetches: list[str]


class _QueueIdsResult(TypedDict, total=False):
    ids: list[str]


class _PauseResumeResult(TypedDict, total=False):
    states: list[int]


class _SeekResult(TypedDict, total=False):
    currentTime: float


class _StopResult(TypedDict, total=False):
    states: list[int]


class _JumpResult(TypedDict, total=False):
    firstId: str
    secondId: str


class _LoopResult(TypedDict, total=False):
    states: list[int]
    wrapped: bool
    endedSeen: bool
    playingAfterEnded: bool
    isPlaying: bool
    repeatMode: int


LOAD_AND_CONFIGURE = f"""async (devToken) => {{
    if (!window._fetchInstrumented) {{
        window._fetches = [];
        const origFetch = window.fetch.bind(window);
        window.fetch = function(...args) {{
            const u = (args[0] && args[0].url) || args[0] || '';
            const m = (args[1] && args[1].method) || (args[0] && args[0].method) || 'GET';
            window._fetches.push(m + ' ' + String(u));
            return origFetch(...args);
        }};
        window._fetchInstrumented = true;
    }}
    if (!window.MusicKit) {{
        const ready = new Promise((r) => document.addEventListener('musickitloaded', r, {{ once: true }}));
        const s = document.createElement('script');
        s.src = '{MUSICKIT_JS_URL}';
        document.head.appendChild(s);
        await ready;
    }}
    const mk = await MusicKit.configure({{
        developerToken: devToken,
        app: {{ name: 'mock-test', build: '1.0' }},
    }});
    window.__mk = mk;
    return {{
        isAuthorized: mk.isAuthorized,
        storefrontId: mk.storefrontId,
        version: MusicKit.version,
    }};
}}"""


def assert_configured(result: _ConfigureResult, expected_storefront: str) -> None:
    assert isinstance(result.get("version"), str), result
    assert result["isAuthorized"] is False
    assert result["storefrontId"] == expected_storefront


SET_QUEUE_AND_GET_ITEM = """async (songId) => {
    await window.__mk.setQueue({ songs: [songId] });
    const item = window.__mk.queue.items[0];
    return {
        id: item.id,
        type: item.type,
        title: item.title,
        artistName: item.artistName,
        albumName: item.albumName,
    };
}"""


def assert_queue_item_resolved(result: _QueueItemResult, expected_id: str) -> None:
    assert result["id"] == expected_id, result
    assert result["title"] == "Silence"
    assert result["artistName"] == "Test Artist"


AUTHORIZE = """async () => {
    const token = await window.__mk.authorize();
    return { isAuthorized: window.__mk.isAuthorized, token };
}"""


def assert_authorize_succeeded(result: _AuthorizeResult, expected_token: str) -> None:
    assert result["isAuthorized"] is True, result
    assert result["token"] == expected_token


UNAUTHORIZE = """async () => {
    await window.__mk.authorize();
    const before = window.__mk.isAuthorized;
    await window.__mk.unauthorize();
    return { before, after: window.__mk.isAuthorized };
}"""


def assert_unauthorize_clears(result: _UnauthorizeResult) -> None:
    assert result["before"] is True, result
    assert result["after"] is False, result


# Wait for both playbackState=2 (playing) AND a POST to acquireWebPlaybackLicense
# after changeToMediaAtIndex. Both signals are required because state=2 alone can
# be reached by routes that bypass the encrypted playback chain (e.g. preview m4a),
# and a license POST alone does not prove playback actually started.
PLAY_AND_AWAIT_PLAYING = """async (songId) => {
    await window.__mk.setQueue({ songs: [songId] });
    const states = [];
    const licenseCalled = () => window._fetches.some(
        (f) => f.startsWith("POST ") && f.indexOf("acquireWebPlaybackLicense") !== -1
    );
    const reachedPlaying = new Promise((resolve, reject) => {
        let didReachPlaying = false;
        let pollHandle = null;
        const tryResolve = () => {
            if (didReachPlaying && licenseCalled()) {
                if (pollHandle) clearInterval(pollHandle);
                resolve({ states, fetches: window._fetches });
            }
        };
        window.__mk.addEventListener('playbackStateDidChange', (e) => {
            states.push(e.state);
            if (e.state === 2) {
                didReachPlaying = true;
                tryResolve();
            }
        });
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            reject(new Error('mediaPlaybackError: ' + JSON.stringify({
                code: e.errorCode, status: e.status, name: e.name,
            }) + ', fetches=' + JSON.stringify(window._fetches)));
        });
        pollHandle = setInterval(tryResolve, 50);
        setTimeout(() => {
            if (pollHandle) clearInterval(pollHandle);
            reject(new Error('timeout, states=' + JSON.stringify(states) + ', fetches=' + JSON.stringify(window._fetches)));
        }, 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    return await reachedPlaying;
}"""


def _called_license_endpoint(fetches: list[str]) -> bool:
    return any(
        f.startswith("POST ") and "acquireWebPlaybackLicense" in f for f in fetches
    )


def assert_reached_playing(result: _PlayingResult) -> None:
    assert isinstance(result, dict), result
    states = result.get("states")
    fetches = result.get("fetches") or []
    assert isinstance(states, list), result
    assert 2 in states, result
    assert _called_license_endpoint(fetches), (
        f"License endpoint was not called; fetches={fetches}"
    )


PLAY_AND_AWAIT_ERROR = """async (songId) => {
    await window.__mk.setQueue({ songs: [songId] });
    const result = await new Promise((resolve, reject) => {
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            resolve({ errorCode: e.errorCode, status: e.status, name: e.name, fetches: window._fetches });
        });
        setTimeout(() => reject(new Error('timeout waiting for mediaPlaybackError, fetches=' + JSON.stringify(window._fetches))), 30000);
        window.__mk.changeToMediaAtIndex(0).catch((e) => {
            resolve({ errorCode: e && e.errorCode, status: e && e.status, name: e && e.name, thrown: String(e), fetches: window._fetches });
        });
    });
    return result;
}"""


def assert_playback_error(result: _PlaybackErrorResult) -> None:
    assert isinstance(result, dict), result
    assert result.get("errorCode") == "GEO_BLOCK", result
    fetches = result.get("fetches") or []
    assert _called_license_endpoint(fetches), (
        f"License endpoint was not called; fetches={fetches}"
    )


def assert_playback_error_code(
    result: _PlaybackErrorResult, expected_code: str
) -> None:
    """Generic variant of ``assert_playback_error`` parameterized on the code name."""
    assert isinstance(result, dict), result
    assert result.get("errorCode") == expected_code, result
    fetches = result.get("fetches") or []
    assert _called_license_endpoint(fetches), (
        f"License endpoint was not called; fetches={fetches}"
    )


# Multi-track queue: starts playing track 0, then advances via skipToNextItem
# and waits for ``nowPlayingItem.id`` to change. Verifies the queue advance
# triggers a fresh license POST (one POST per track) and the player exits the
# first-track playing state.
PLAY_AND_SKIP_TO_NEXT = """async (songIds) => {
    await window.__mk.setQueue({ songs: songIds });
    const result = { firstNowPlaying: null, secondNowPlaying: null };
    const reachedPlaying = new Promise((resolve, reject) => {
        const onState = (e) => {
            if (e.state === 2) {
                window.__mk.removeEventListener('playbackStateDidChange', onState);
                resolve();
            }
        };
        window.__mk.addEventListener('playbackStateDidChange', onState);
        setTimeout(() => reject(new Error('timeout waiting for first play, fetches=' + JSON.stringify(window._fetches))), 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    await reachedPlaying;
    result.firstNowPlaying = window.__mk.nowPlayingItem ? window.__mk.nowPlayingItem.id : null;

    const advanced = new Promise((resolve, reject) => {
        const handle = setInterval(() => {
            const cur = window.__mk.nowPlayingItem ? window.__mk.nowPlayingItem.id : null;
            if (cur !== result.firstNowPlaying && cur !== null) {
                clearInterval(handle);
                resolve();
            }
        }, 50);
        setTimeout(() => { clearInterval(handle); reject(new Error('timeout after skip, fetches=' + JSON.stringify(window._fetches))); }, 30000);
    });
    window.__mk.skipToNextItem().catch(() => {});
    await advanced;
    result.secondNowPlaying = window.__mk.nowPlayingItem ? window.__mk.nowPlayingItem.id : null;
    return result;
}"""


def assert_skipped_to_next(result: _SkipToNextResult) -> None:
    """Assert ``skipToNextItem`` advanced ``nowPlayingItem`` to the next track.

    Asserts the user-observable contract (the now-playing item changed to a
    different track id). License-POST count is not asserted: webkit reuses
    the EME session across adjacent same-key tracks while chromium re-fetches,
    so the count varies by browser and is implementation detail rather than
    user-facing behavior.
    """
    assert isinstance(result, dict), result
    assert result["firstNowPlaying"] is not None, result
    assert result["secondNowPlaying"] is not None, result
    assert result["firstNowPlaying"] != result["secondNowPlaying"], result


# Set queue from a non-songs source: ``{ album }`` / ``{ playlist }``. MusicKit
# JS resolves the source to its tracks internally and populates ``queue.items``
# with the resolved track ids. The scenario reports the resolved queue ids so
# the caller can verify the source's tracks ended up in the queue.
SET_QUEUE_FROM_ALBUM = """async (albumId) => {
    await window.__mk.setQueue({ album: albumId });
    return {
        ids: window.__mk.queue.items.map((i) => i.id),
        types: window.__mk.queue.items.map((i) => i.type),
    };
}"""

SET_QUEUE_FROM_PLAYLIST = """async (playlistId) => {
    await window.__mk.setQueue({ playlist: playlistId });
    return {
        ids: window.__mk.queue.items.map((i) => i.id),
        types: window.__mk.queue.items.map((i) => i.type),
    };
}"""


def assert_queue_contains_ids(result: _QueueIdsResult, expected_ids: list[str]) -> None:
    assert isinstance(result, dict), result
    assert result.get("ids") == expected_ids, result


class _QueueWithFetchesResult(TypedDict, total=False):
    ids: list[str]
    types: list[str]
    fetches: list[str]


# Set queue from a single source item and record every fetch issued during
# the resolution window, so the caller can assert the chain stayed inside
# its expected envelope. ``params`` is ``{ kind, id }`` where ``kind`` is
# the MusicKit-recognized source key (``"musicVideo"`` / ``"song"`` / ...)
# and ``id`` is the resource id (catalog or library-prefixed). The recorded
# slice contains only fetches issued after the call site, not the page-load
# / configure fetches.
SET_QUEUE_AND_RECORD_FETCHES = """async (params) => {
    const { kind, id } = params;
    const fetchesBefore = window._fetches.length;
    await window.__mk.setQueue({ [kind]: id });
    return {
        ids: window.__mk.queue.items.map((i) => i.id),
        types: window.__mk.queue.items.map((i) => i.type),
        fetches: window._fetches.slice(fetchesBefore),
    };
}"""


def assert_queue_resolved_without_chain(
    result: _QueueWithFetchesResult,
    expected_ids: list[str],
    forbidden_substrings: tuple[str, ...],
) -> None:
    """Assert the queue resolved to ``expected_ids`` and the recorded fetch window contained no forbidden substring.

    ``forbidden_substrings`` are URL fragments the recorded fetch window
    must not contain — letting callers pin what MusicKit JS does and does
    not emit during a given setQueue resolution. Catches regressions where
    the chain shape changes (a path that was not emitted starts being
    emitted, or vice versa) between MusicKit JS versions.
    """
    assert isinstance(result, dict), result
    assert result.get("ids") == expected_ids, result
    fetches = result.get("fetches") or []
    for sub in forbidden_substrings:
        for f in fetches:
            assert sub not in f, (
                f"MusicKit JS chained to forbidden path fragment {sub!r}: {f}\n"
                f"all recorded fetches={fetches}"
            )


# Pause + resume during DRM playback: state=2 reached → pause() → state=3 →
# play() → state=2 again. Verifies the player can re-enter PLAYING after a
# user-initiated pause, exercising the state machine path that webkit's
# FairPlay shim path cannot recover from (see test_musickit_playback_control_*).
PAUSE_AND_RESUME = """async (songId) => {
    await window.__mk.setQueue({ songs: [songId] });
    const states = [];
    const promise = new Promise((resolve, reject) => {
        let pausedRequested = false;
        let resumeRequested = false;
        let resumeAcked = false;
        window.__mk.addEventListener('playbackStateDidChange', (e) => {
            states.push(e.state);
            if (e.state === 2 && !pausedRequested) {
                pausedRequested = true;
                window.__mk.pause().catch(() => {});
            } else if (e.state === 3 && pausedRequested && !resumeRequested) {
                resumeRequested = true;
                window.__mk.play().catch(() => {});
            } else if (e.state === 2 && resumeRequested && !resumeAcked) {
                resumeAcked = true;
                resolve({ states });
            }
        });
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            reject(new Error('mediaPlaybackError: ' + e.errorCode + ' states=' + JSON.stringify(states)));
        });
        setTimeout(() => reject(new Error('timeout, states=' + JSON.stringify(states) + ' fetches=' + JSON.stringify(window._fetches))), 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    return await promise;
}"""


def assert_paused_and_resumed(result: _PauseResumeResult) -> None:
    """Assert ``pause`` then ``play`` returned the player to state=2.

    Verifies state=2 appeared, state=3 (paused) appeared between two state=2
    occurrences (= second state=2 is the resume).
    """
    assert isinstance(result, dict), result
    states = result.get("states")
    assert isinstance(states, list), result
    assert 2 in states, result
    assert 3 in states, result
    first_two = states.index(2)
    paused_at = states.index(3, first_two)
    second_two = states.index(2, paused_at)
    assert second_two > paused_at, result


# Seek to a specific time during playback: reach state=2 → seekToTime(N) →
# verify currentPlaybackTime advanced to ~N. Exercises the state-machine path
# that depends on the player accepting a seek request mid-playback.
SEEK_TO_TIME = """async (params) => {
    const { songId, targetSec } = params;
    await window.__mk.setQueue({ songs: [songId] });
    const promise = new Promise((resolve, reject) => {
        let didSeek = false;
        window.__mk.addEventListener('playbackStateDidChange', (e) => {
            if (e.state === 2 && !didSeek) {
                didSeek = true;
                window.__mk.seekToTime(targetSec);
                setTimeout(() => {
                    resolve({ currentTime: window.__mk.currentPlaybackTime });
                }, 500);
            }
        });
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            reject(new Error('mediaPlaybackError: ' + e.errorCode + ' fetches=' + JSON.stringify(window._fetches)));
        });
        setTimeout(() => reject(new Error('timeout waiting for state=2, fetches=' + JSON.stringify(window._fetches))), 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    return await promise;
}"""


def assert_seeked_to(
    result: _SeekResult, target_sec: float, tolerance_sec: float = 2.0
) -> None:
    assert isinstance(result, dict), result
    cur = result.get("currentTime")
    assert isinstance(cur, (int, float)), result
    assert abs(cur - target_sec) <= tolerance_sec, (
        f"expected ~{target_sec}±{tolerance_sec}s, got {cur}"
    )


# Stop during playback: reach state=2 → stop() → state=0 (idle).
STOP_DURING_PLAYBACK = """async (songId) => {
    await window.__mk.setQueue({ songs: [songId] });
    const states = [];
    const promise = new Promise((resolve, reject) => {
        let didStop = false;
        window.__mk.addEventListener('playbackStateDidChange', (e) => {
            states.push(e.state);
            if (e.state === 2 && !didStop) {
                didStop = true;
                window.__mk.stop().catch(() => {});
            } else if (e.state === 4 && didStop) {
                resolve({ states });
            }
        });
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            reject(new Error('mediaPlaybackError: ' + e.errorCode + ' states=' + JSON.stringify(states)));
        });
        setTimeout(() => reject(new Error('timeout, states=' + JSON.stringify(states))), 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    return await promise;
}"""


def assert_stopped(result: _StopResult) -> None:
    """Assert ``stop()`` transitioned the player out of PLAYING into a stopped state.

    MusicKit JS surfaces ``stop()`` as a state=4 transition (not the spec's
    NONE=0). Both chromium and firefox produce ``[2, 8, 1, 2, 4, 6, 4]`` —
    state=4 is the user-observable stop completion.
    """
    assert isinstance(result, dict), result
    states = result.get("states")
    assert isinstance(states, list), result
    assert 2 in states, result
    assert 4 in states, result
    assert states.index(4) > states.index(2), result


# Jump to a different queue index during playback: reach state=2 on track 0 →
# changeToMediaAtIndex(2) → wait for nowPlayingItem.id to change. Exercises the
# state-machine path through a mid-playback track replacement (distinct from
# skipToNextItem's adjacent-track advance in PLAY_AND_SKIP_TO_NEXT).
JUMP_DURING_PLAYBACK = """async (params) => {
    const { songIds, targetIndex } = params;
    await window.__mk.setQueue({ songs: songIds });
    const result = { firstId: null, secondId: null };
    const reachedPlaying = new Promise((resolve, reject) => {
        const onState = (e) => {
            if (e.state === 2) {
                window.__mk.removeEventListener('playbackStateDidChange', onState);
                resolve();
            }
        };
        window.__mk.addEventListener('playbackStateDidChange', onState);
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            reject(new Error('mediaPlaybackError: ' + e.errorCode + ' fetches=' + JSON.stringify(window._fetches)));
        });
        setTimeout(() => reject(new Error('timeout 1st play, fetches=' + JSON.stringify(window._fetches))), 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    await reachedPlaying;
    result.firstId = window.__mk.nowPlayingItem ? window.__mk.nowPlayingItem.id : null;

    const jumped = new Promise((resolve, reject) => {
        const handle = setInterval(() => {
            const cur = window.__mk.nowPlayingItem ? window.__mk.nowPlayingItem.id : null;
            if (cur !== result.firstId && cur !== null) {
                clearInterval(handle);
                resolve();
            }
        }, 50);
        setTimeout(() => { clearInterval(handle); reject(new Error('timeout jump, fetches=' + JSON.stringify(window._fetches))); }, 30000);
    });
    window.__mk.changeToMediaAtIndex(targetIndex).catch(() => {});
    await jumped;
    result.secondId = window.__mk.nowPlayingItem ? window.__mk.nowPlayingItem.id : null;
    return result;
}"""


def assert_jumped_to(result: _JumpResult, expected_id: str) -> None:
    assert isinstance(result, dict), result
    assert result.get("firstId") is not None, result
    assert result.get("secondId") is not None, result
    assert result["firstId"] != result["secondId"], result
    assert result["secondId"] == expected_id, result


# Single-song repeat (repeatMode = 1): play a short song head-to-tail and
# observe one loop iteration. The resolve condition captures the externally
# observable loop signals: currentPlaybackTime rises then wraps back near 0
# while playback continues, the player surfaces ended (state 5) at the end
# boundary, and then re-enters playing (state 2). Resolves as soon as one full
# loop is observed so the test stays fast.
LOOP_SINGLE_SONG = """async (songId) => {
    await window.__mk.setQueue({ songs: [songId] });
    window.__mk.repeatMode = 1;
    const states = [];
    let maxTime = 0;
    let wrapped = false;
    let endedSeen = false;
    let playingAfterEnded = false;
    const promise = new Promise((resolve, reject) => {
        let done = false;
        let sampler = null;
        const finish = () => {
            if (done) return;
            done = true;
            if (sampler) clearInterval(sampler);
            resolve({
                states: states.slice(),
                wrapped: wrapped,
                endedSeen: endedSeen,
                playingAfterEnded: playingAfterEnded,
                isPlaying: window.__mk.isPlaying,
                repeatMode: window.__mk.repeatMode,
            });
        };
        const tryResolve = () => {
            if (wrapped && endedSeen && playingAfterEnded) finish();
        };
        sampler = setInterval(() => {
            const t = Number(window.__mk.currentPlaybackTime);
            if (isFinite(t)) {
                if (t > maxTime) maxTime = t;
                if (maxTime > 1 && t < maxTime - 1) wrapped = true;
            }
            tryResolve();
        }, 100);
        window.__mk.addEventListener('playbackStateDidChange', (e) => {
            states.push(e.state);
            if (e.state === 5) endedSeen = true;
            if (e.state === 2 && endedSeen) playingAfterEnded = true;
            tryResolve();
        });
        window.__mk.addEventListener('mediaPlaybackError', (e) => {
            if (sampler) clearInterval(sampler);
            reject(new Error('mediaPlaybackError: ' + e.errorCode + ' states=' + JSON.stringify(states)));
        });
        setTimeout(() => {
            if (sampler) clearInterval(sampler);
            reject(new Error('loop not observed; states=' + JSON.stringify(states)
                + ' wrapped=' + wrapped + ' endedSeen=' + endedSeen
                + ' playingAfterEnded=' + playingAfterEnded
                + ' fetches=' + JSON.stringify(window._fetches)));
        }, 30000);
    });
    window.__mk.changeToMediaAtIndex(0).catch(() => {});
    return await promise;
}"""


def assert_looped(result: _LoopResult) -> None:
    """Assert single-song repeat looped at the end boundary.

    Verifies the externally observable loop signals: repeat is enabled,
    currentPlaybackTime wrapped back toward 0 while playing, the player
    surfaced ended (state 5), playing (state 2) resumed after that ended, and
    playback stayed active.
    """
    assert isinstance(result, dict), result
    assert result.get("repeatMode") == 1, result
    states = result.get("states")
    assert isinstance(states, list), result
    assert 5 in states, result
    ended_at = states.index(5)
    assert 2 in states[ended_at:], result
    assert result.get("endedSeen") is True, result
    assert result.get("playingAfterEnded") is True, result
    assert result.get("wrapped") is True, result
    assert result.get("isPlaying") is True, result
