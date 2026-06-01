(function () {
  var ns = (window.__musickitApiMock = window.__musickitApiMock || {});
  ns.browser = ns.browser || {};

  var INTERNAL_URL =
    "https://musickit-api-mock.invalid/browser/eme_flavor";

  function fetchFlavor() {
    return fetch(INTERNAL_URL).then(function (r) {
      if (r.status === 200) {
        return r.json().then(function (body) {
          return body && body.value;
        });
      }
      return r.text().then(function (text) {
        throw new Error(text || "browser.eme_flavor is not set");
      });
    });
  }

  function getCachedFlavor() {
    return ns.browser.eme_flavor || null;
  }

  function makeStubSession() {
    var listeners = {};
    var self;
    var closedResolve;
    var closedPromise = new Promise(function (resolve) {
      closedResolve = resolve;
    });
    function dispatch(type, props) {
      var fns = (listeners[type] || []).slice();
      Promise.resolve().then(function () {
        var ev = new Event(type);
        Object.defineProperty(ev, "target", {
          value: self,
          configurable: true,
          writable: true,
        });
        Object.defineProperty(ev, "currentTarget", {
          value: self,
          configurable: true,
          writable: true,
        });
        if (props) {
          for (var k in props) {
            if (Object.prototype.hasOwnProperty.call(props, k)) ev[k] = props[k];
          }
        }
        for (var i = 0; i < fns.length; i++) {
          try {
            fns[i](ev);
          } catch (_) {}
        }
      });
    }
    self = {
      keyStatuses: new Map(),
      sessionId: "musickit-api-mock-" + Math.random().toString(36).slice(2),
      addEventListener: function (type, fn) {
        listeners[type] = listeners[type] || [];
        listeners[type].push(fn);
      },
      removeEventListener: function (type, fn) {
        if (!listeners[type]) return;
        listeners[type] = listeners[type].filter(function (x) {
          return x !== fn;
        });
      },
      generateRequest: function (_initDataType, initData) {
        dispatch("message", {
          messageType: "license-request",
          message: initData,
        });
        return Promise.resolve();
      },
      load: function () {
        return Promise.resolve(true);
      },
      update: function (_response) {
        return Promise.resolve();
      },
      close: function () {
        closedResolve("closed-by-application");
        return Promise.resolve();
      },
      remove: function () {
        return Promise.resolve();
      },
      get expiration() {
        return NaN;
      },
      get closed() {
        return closedPromise;
      },
      _dispatch: dispatch,
    };
    return self;
  }

  function makeStubMediaKeys() {
    return {
      setServerCertificate: function () {
        return Promise.resolve(true);
      },
      createSession: function (_sessionType) {
        return makeStubSession();
      },
    };
  }

  function makeStubAccess(keySystem, configurations) {
    return {
      keySystem: keySystem,
      getConfiguration: function () {
        return (configurations && configurations[0]) || {};
      },
      createMediaKeys: function () {
        return Promise.resolve(makeStubMediaKeys());
      },
    };
  }

  function installModernEme() {
    Object.defineProperty(navigator, "requestMediaKeySystemAccess", {
      configurable: true,
      writable: true,
      value: function (keySystem, configurations) {
        return fetchFlavor().then(
          function (flavor) {
            if (flavor !== keySystem) {
              throw new DOMException(
                "Unsupported keySystem: " + keySystem,
                "NotSupportedError"
              );
            }
            return makeStubAccess(keySystem, configurations);
          },
          function (err) {
            var msg = err && err.message ? err.message : String(err);
            console.error("[musickit-api-mock] " + msg);
            throw new DOMException(msg, "InvalidStateError");
          }
        );
      },
    });
    // Modern-EME path selection in the player can gate on these globals;
    // browsers without a CDM may leave them undefined. Expose empty
    // constructors so the modern path is selectable uniformly.
    if (typeof window.MediaKeys === "undefined") {
      Object.defineProperty(window, "MediaKeys", {
        configurable: true,
        writable: true,
        value: function () {},
      });
    }
    if (typeof window.MediaKeySystemAccess === "undefined") {
      Object.defineProperty(window, "MediaKeySystemAccess", {
        configurable: true,
        writable: true,
        value: function () {},
      });
    }
    if (window.HTMLMediaElement && window.HTMLMediaElement.prototype) {
      Object.defineProperty(
        window.HTMLMediaElement.prototype,
        "setMediaKeys",
        {
          configurable: true,
          writable: true,
          value: function (_mediaKeys) {
            return Promise.resolve();
          },
        }
      );
    }
  }

  function installWebKit() {
    function StubWebKitMediaKeys(keySystem) {
      this.keySystem = keySystem;
    }
    StubWebKitMediaKeys.prototype.createSession = function (_mediaType, initData) {
      var session = makeStubSession();
      session.update = function () {
        return Promise.resolve();
      };
      session._dispatch("webkitkeymessage", { message: initData });
      return session;
    };
    StubWebKitMediaKeys.isTypeSupported = function (keySystem, _contentType) {
      var flavor = getCachedFlavor();
      if (flavor !== "com.apple.fps") return false;
      return (
        keySystem === "com.apple.fps" ||
        keySystem === "com.apple.fps.1_0" ||
        keySystem === "com.apple.fps.2_0"
      );
    };
    Object.defineProperty(window, "WebKitMediaKeys", {
      configurable: true,
      writable: true,
      value: StubWebKitMediaKeys,
    });
    if (window.HTMLMediaElement && window.HTMLMediaElement.prototype) {
      Object.defineProperty(
        window.HTMLMediaElement.prototype,
        "webkitSetMediaKeys",
        {
          configurable: true,
          writable: true,
          value: function (mediaKeys) {
            this.webkitKeys = mediaKeys;
          },
        }
      );
    }
  }

  function installMSMediaKeys() {
    function StubMSMediaKeys(keySystem) {
      this.keySystem = keySystem;
    }
    StubMSMediaKeys.prototype.createSession = function (_mediaType, initData) {
      var session = makeStubSession();
      session._dispatch("mskeymessage", { message: initData });
      return session;
    };
    StubMSMediaKeys.isTypeSupported = function (keySystem, _contentType) {
      var flavor = getCachedFlavor();
      if (flavor !== "com.microsoft.playready") return false;
      return keySystem === "com.microsoft.playready";
    };
    Object.defineProperty(window, "MSMediaKeys", {
      configurable: true,
      writable: true,
      value: StubMSMediaKeys,
    });
  }

  function clearOthers(active) {
    if (active !== "com.apple.fps") {
      try {
        Object.defineProperty(window, "WebKitMediaKeys", {
          configurable: true,
          writable: true,
          value: undefined,
        });
      } catch (_) {}
    }
    if (active !== "com.microsoft.playready") {
      try {
        Object.defineProperty(window, "MSMediaKeys", {
          configurable: true,
          writable: true,
          value: undefined,
        });
      } catch (_) {}
    }
  }

  function installSyntheticEncryptedDispatcher() {
    // The native encrypted event only fires on environments whose media
    // engine has the matching CDM registered: FairPlay needs OS-level
    // skd:// parsing; Widevine / PlayReady need the corresponding CDM
    // installed. Without it the event never fires (or the resource is
    // rejected as unsuitable), so the EME chain has no entry point.
    if (ns.__syntheticDispatcherInstalled) return;
    ns.__syntheticDispatcherInstalled = true;
    var FPS_KEY_REGEX = /#EXT-X-KEY:[^\n]*URI="(skd:\/\/[^"]+)"/;
    var DATA_KEY_REGEX = /#EXT-X-KEY:METHOD=ISO-23001-7[^\n]*URI="data:[^,]*;base64,([^"]+)"/;
    var M3U8_REGEX = /\.m3u8(\?|#|$)/;
    var BLOB_REGEX = /^blob:/;
    var CACHE_TTL_MS = 30000;
    // Fallback for manifests that carry no per-segment durations (e.g. a master
    // playlist, or a live stream): the synthetic element reports an open-ended
    // timeline so playback never hits a fabricated end boundary.
    var SYNTHETIC_DURATION_SEC = 3600;
    var EXTINF_REGEX = /#EXTINF:\s*([0-9.]+)/g;
    var LOAD_PROGRESSION_EVENTS = ["loadstart", "durationchange", "loadedmetadata", "loadeddata", "canplay", "canplaythrough"];
    function monotonicNowMs() {
      return window.performance && typeof window.performance.now === "function" ? window.performance.now() : Date.now();
    }
    function isMusicKitStack() {
      try { throw new Error(); } catch (err) {
        return !!(err && typeof err.stack === "string" && /musickit/i.test(err.stack));
      }
    }
    var keyByUrl = Object.create(null);
    // Duration resolution differs by media engine, so both stores below are
    // load-bearing — neither alone covers every engine, and dropping either
    // breaks the engines that depend on it.
    //
    // Some engines attach the manifest URL directly as the element src; there
    // the duration keyed by that URL is read back for the element's whole
    // lifetime. Other engines feed playback through MediaSource: the element
    // src becomes an opaque blob URL with no readable body and no way to key a
    // duration to it. Playback is sequential (fetch manifest, then attach its
    // MediaSource), so those engines fall back to the most recently parsed
    // manifest duration.
    //
    // The global fallback assumes the most recently parsed manifest belongs to
    // the element being resolved. That holds while one track plays at a time;
    // with a multi-song queue, prefetching the next track's manifest can
    // overwrite the global while the current MediaSource element is still
    // playing, so it would resolve to the wrong duration. Single-track playback
    // (including single-song repeat) is unaffected. A correct multi-song fix
    // needs a per-element duration snapshot taken when its src is attached, or
    // a manifest-to-element link the blob src does not currently carry.
    //
    // TODO: this map is never pruned, so it grows once per distinct manifest
    // URL over a page's lifetime. A blind time-based eviction is unsafe — the
    // direct-src engines read an entry for the element's whole playback, which
    // can outlive any fixed TTL; pruning must instead be tied to the track /
    // element lifecycle (drop an entry once its URL is no longer an active src).
    var durationByUrl = Object.create(null);
    var lastManifestDuration = null;
    var pendingMediaByUrl = Object.create(null);
    function dispatchLoadProgression(mediaEl) {
      Promise.resolve().then(function () {
        LOAD_PROGRESSION_EVENTS.forEach(function (type) {
          try { mediaEl.dispatchEvent(new Event(type)); } catch (_) {}
        });
      });
    }
    function cacheKey(url, key) {
      keyByUrl[url] = key;
      flushPendingMedia(url);
      // Bound the cache for fetches whose src never lands. The entry stays
      // past the first dispatch so a freshly-created audio element for the
      // same URL (e.g. when the player recreates its element to handle seek)
      // can still pick up the synthetic event chain.
      setTimeout(function () { delete keyByUrl[url]; }, CACHE_TTL_MS);
    }
    function flushPendingMedia(url) {
      var pending = pendingMediaByUrl[url];
      if (!pending) return;
      delete pendingMediaByUrl[url];
      pending.forEach(function (mediaEl) { maybeDispatchEncrypted(mediaEl, url); });
    }
    function inputUrl(input) {
      if (typeof input === "string") return input;
      if (input && typeof input.url === "string") return input.url;
      if (input && typeof input.href === "string") return input.href;
      return null;
    }
    function extractKey(body) {
      var fpsMatch = body.match(FPS_KEY_REGEX);
      if (fpsMatch) {
        var skd = fpsMatch[1];
        var skdBytes = new Uint8Array(skd.length);
        for (var i = 0; i < skd.length; i++) skdBytes[i] = skd.charCodeAt(i);
        return { initDataType: "skd", initData: skdBytes.buffer };
      }
      var dataMatch = body.match(DATA_KEY_REGEX);
      if (dataMatch) {
        var raw;
        try { raw = atob(dataMatch[1]); } catch (_) { return null; }
        var dataBytes = new Uint8Array(raw.length);
        for (var j = 0; j < raw.length; j++) dataBytes[j] = raw.charCodeAt(j);
        return { initDataType: "cenc", initData: dataBytes.buffer };
      }
      return null;
    }
    function extractDuration(body) {
      EXTINF_REGEX.lastIndex = 0;
      var total = 0;
      var found = false;
      var m;
      while ((m = EXTINF_REGEX.exec(body)) !== null) {
        var v = parseFloat(m[1]);
        if (isFinite(v)) {
          total += v;
          found = true;
        }
      }
      return found ? total : null;
    }
    var origFetch = window.fetch;
    if (typeof origFetch === "function") {
      window.fetch = function (input, init) {
        var url = inputUrl(input);
        var p = origFetch.call(this, input, init);
        if (typeof url !== "string" || !M3U8_REGEX.test(url)) return p;
        // Defer the resolution returned to the caller until the body has been
        // read and the cache populated, otherwise the player's downstream
        // chain (which reads the same response) races our extraction.
        return p.then(function (response) {
          return response.clone().text().then(
            function (body) {
              var dur = extractDuration(body);
              if (dur != null) {
                durationByUrl[url] = dur;
                lastManifestDuration = dur;
              }
              var key = extractKey(body);
              if (key) cacheKey(url, key);
              return response;
            },
            function () { return response; }
          );
        });
      };
    }
    var urlApi = window.URL || window.webkitURL;
    if (urlApi && typeof urlApi.createObjectURL === "function") {
      var origCreateObjectURL = urlApi.createObjectURL;
      urlApi.createObjectURL = function (object) {
        var url = origCreateObjectURL.apply(this, arguments);
        if (typeof url === "string" && object && typeof object.text === "function") {
          object.text().then(
            function (body) {
              var dur = extractDuration(body);
              if (dur != null) {
                durationByUrl[url] = dur;
                lastManifestDuration = dur;
              }
              var key = extractKey(body);
              if (key) {
                cacheKey(url, key);
              }
            },
            function () {}
          );
        }
        return url;
      };
    }
    var proto = window.HTMLMediaElement && window.HTMLMediaElement.prototype;
    if (!proto) return;
    var srcDesc = Object.getOwnPropertyDescriptor(proto, "src");
    if (!srcDesc || !srcDesc.set) return;
    var origSrcGet = srcDesc.get;
    var origSrcSet = srcDesc.set;
    var srcByEl = new WeakMap();
    function activateSyntheticSrc(mediaEl, value) {
      srcByEl.set(mediaEl, value);
      ns.__currentSyntheticMediaElement = mediaEl;
      ensureState(mediaEl);
      if (!maybeDispatchEncrypted(mediaEl, value)) {
        pendingMediaByUrl[value] = pendingMediaByUrl[value] || [];
        pendingMediaByUrl[value].push(mediaEl);
      }
    }
    // Per-instance ``Object.defineProperty`` on WebIDL accessor properties
    // is rejected by Firefox; routing through the prototype makes the
    // override portable across engines.
    var STATE = new WeakMap();
    function ensureState(mediaEl) {
      var s = STATE.get(mediaEl);
      if (!s) {
        s = { playing: false, seeking: false, ended: false, simCurrentTime: 0, lastTickMs: null, tickHandle: null };
        STATE.set(mediaEl, s);
      }
      return s;
    }
    function deactivateSyntheticSrc(mediaEl) {
      srcByEl.delete(mediaEl);
      var s = STATE.get(mediaEl);
      if (s) stopTick(s);
      STATE.delete(mediaEl);
      if (ns.__currentSyntheticMediaElement === mediaEl) ns.__currentSyntheticMediaElement = null;
    }
    (function () {
      // MusicKit may register native media error/stall handlers before src is
      // assigned. Keep unrelated page media untouched by only suppressing
      // handlers registered from MusicKit JS itself.
      var SUPPRESSED = /^(error|stalled|waiting|abort|emptied)$/;
      var origAdd = proto.addEventListener;
      var origRemove = proto.removeEventListener;
      if (typeof origAdd !== "function" || typeof origRemove !== "function") return;
      var wrappedByEl = new WeakMap();
      function captureOf(opts) {
        return !!(opts === true || (opts && typeof opts === "object" && opts.capture));
      }
      function recordsFor(el) {
        var records = wrappedByEl.get(el);
        if (!records) {
          records = [];
          wrappedByEl.set(el, records);
        }
        return records;
      }
      function findRecord(el, type, fn, opts) {
        var records = wrappedByEl.get(el) || [];
        var capture = captureOf(opts);
        for (var i = records.length - 1; i >= 0; i--) {
          var record = records[i];
          if (record.type === type && record.fn === fn && record.capture === capture) return { records: records, index: i, record: record };
        }
        return null;
      }
      try {
        proto.addEventListener = function (type, fn, opts) {
          if (typeof type !== "string" || !SUPPRESSED.test(type) || !fn || !isMusicKitStack()) {
            return origAdd.call(this, type, fn, opts);
          }
          var existing = findRecord(this, type, fn, opts);
          if (existing) return origAdd.call(this, type, existing.record.wrapped, opts);
          var wrapped = function (event) {
            return;
          };
          recordsFor(this).push({ type: type, fn: fn, capture: captureOf(opts), wrapped: wrapped });
          return origAdd.call(this, type, wrapped, opts);
        };
        proto.removeEventListener = function (type, fn, opts) {
          var found = typeof type === "string" && fn ? findRecord(this, type, fn, opts) : null;
          if (found) {
            found.records.splice(found.index, 1);
            return origRemove.call(this, type, found.record.wrapped, opts);
          }
          return origRemove.call(this, type, fn, opts);
        };
      } catch (_) {}
    })();
    function startTick(mediaEl, s) {
      if (s.tickHandle !== null) return;
      s.tickHandle = setInterval(function () {
        if (!s.playing) return;
        var d = durationFor(mediaEl);
        var t = s.simCurrentTime + (monotonicNowMs() - (s.lastTickMs === null ? monotonicNowMs() : s.lastTickMs)) / 1000;
        if (t >= d) {
          s.simCurrentTime = d;
          s.lastTickMs = null;
          s.playing = false;
          s.ended = true;
          stopTick(s);
          try { mediaEl.dispatchEvent(new Event("timeupdate")); } catch (_) {}
          try { mediaEl.dispatchEvent(new Event("ended")); } catch (_) {}
          return;
        }
        try { mediaEl.dispatchEvent(new Event("timeupdate")); } catch (_) {}
      }, 250);
    }
    function stopTick(s) {
      if (s.tickHandle === null) return;
      clearInterval(s.tickHandle);
      s.tickHandle = null;
    }
    function durationFor(mediaEl) {
      var url = srcByEl.get(mediaEl);
      var d = url != null ? durationByUrl[url] : undefined;
      if (typeof d === "number" && isFinite(d) && d > 0) return d;
      if (typeof lastManifestDuration === "number" && lastManifestDuration > 0) return lastManifestDuration;
      return SYNTHETIC_DURATION_SEC;
    }
    function makeRange(end) {
      return {
        length: 1,
        start: function (i) { return i === 0 ? 0 : NaN; },
        end: function (i) { return i === 0 ? end : NaN; },
      };
    }
    function overrideAccessor(name, syntheticGet, syntheticSet) {
      var orig = Object.getOwnPropertyDescriptor(proto, name);
      var origGet = orig && orig.get;
      var origSet = orig && orig.set;
      try {
        Object.defineProperty(proto, name, {
          configurable: true,
          enumerable: orig ? orig.enumerable : true,
          get: function () {
            var s = STATE.get(this);
            if (s) return syntheticGet(this, s);
            return origGet ? origGet.call(this) : undefined;
          },
          set: function (v) {
            var s = STATE.get(this);
            if (s && syntheticSet) { syntheticSet(this, s, v); return; }
            if (origSet) origSet.call(this, v);
          },
        });
      } catch (_) {}
    }
    function overrideMethod(name, synthetic) {
      var orig = proto[name];
      try {
        proto[name] = function () {
          var s = STATE.get(this);
          if (s) return synthetic(this, s, arguments);
          return orig ? orig.apply(this, arguments) : undefined;
        };
      } catch (_) {}
    }
    Object.defineProperty(proto, "src", {
      configurable: true,
      enumerable: srcDesc.enumerable,
      get: function () {
        var stored = srcByEl.get(this);
        if (typeof stored === "string") return stored;
        return origSrcGet ? origSrcGet.call(this) : "";
      },
      set: function (value) {
        // Skip the native src assignment so the native engine doesn't
        // start a load that will fail (missing CDM / decoder / segment
        // format) and surface stall or error states the EME chain
        // synthesis can't recover from.
        if (typeof value === "string" && (M3U8_REGEX.test(value) || BLOB_REGEX.test(value))) {
          activateSyntheticSrc(this, value);
          return;
        }
        deactivateSyntheticSrc(this);
        origSrcSet.call(this, value);
      },
    });
    (function () {
      var origSetAttribute = proto.setAttribute;
      var origGetAttribute = proto.getAttribute;
      var origRemoveAttribute = proto.removeAttribute;
      try {
        proto.setAttribute = function (name, value) {
          if (String(name).toLowerCase() === "src" && typeof value === "string" && (M3U8_REGEX.test(value) || BLOB_REGEX.test(value))) {
            // Some engines/player paths assign media URLs through the content
            // attribute rather than the WebIDL property. Route those through
            // the same synthetic path; otherwise Firefox starts a native HLS
            // load and later playback controls operate on native state.
            activateSyntheticSrc(this, value);
            return;
          }
          return origSetAttribute ? origSetAttribute.apply(this, arguments) : undefined;
        };
        proto.getAttribute = function (name) {
          if (String(name).toLowerCase() === "src") {
            var stored = srcByEl.get(this);
            if (typeof stored === "string") return stored;
          }
          return origGetAttribute ? origGetAttribute.apply(this, arguments) : null;
        };
        proto.removeAttribute = function (name) {
          if (String(name).toLowerCase() === "src") {
            deactivateSyntheticSrc(this);
          }
          return origRemoveAttribute ? origRemoveAttribute.apply(this, arguments) : undefined;
        };
      } catch (_) {}
    })();
    overrideAccessor("paused", function (el, s) { return !s.playing; });
    overrideAccessor("error", function () { return null; });
    overrideAccessor("readyState", function () { return 4; });
    overrideAccessor("networkState", function () { return 1; });
    overrideAccessor("seeking", function (el, s) { return !!s.seeking; });
    overrideAccessor("ended", function (el, s) { return !!s.ended; });
    overrideAccessor("duration", function (el) { return durationFor(el); });
    overrideAccessor("buffered", function (el) { return makeRange(durationFor(el)); });
    overrideAccessor("seekable", function (el) { return makeRange(durationFor(el)); });
    overrideAccessor("played", function (el) { return makeRange(durationFor(el)); });
    overrideAccessor("currentSrc", function (el) {
      var stored = srcByEl.get(el);
      return typeof stored === "string" ? stored : "";
    });
    overrideAccessor(
      "currentTime",
      function (el, s) {
        var t = s.simCurrentTime;
        if (s.playing && s.lastTickMs !== null) {
          t += (monotonicNowMs() - s.lastTickMs) / 1000;
        }
        var d = durationFor(el);
        return t > d ? d : t;
      },
      function (el, s, v) {
        var t = Number(v);
        if (!isFinite(t)) return;
        s.simCurrentTime = t;
        if (t < durationFor(el)) s.ended = false;
        if (s.playing) s.lastTickMs = monotonicNowMs();
        s.seeking = true;
        try { el.dispatchEvent(new Event("seeking")); } catch (_) {}
        Promise.resolve().then(function () {
          s.seeking = false;
          try { el.dispatchEvent(new Event("seeked")); } catch (_) {}
          try { el.dispatchEvent(new Event("timeupdate")); } catch (_) {}
        });
      }
    );
    overrideMethod("fastSeek", function (el, s, args) {
      var t = Number(args[0]);
      if (!isFinite(t)) return;
      s.simCurrentTime = t;
      if (t < durationFor(el)) s.ended = false;
      if (s.playing) s.lastTickMs = monotonicNowMs();
      s.seeking = true;
      try { el.dispatchEvent(new Event("seeking")); } catch (_) {}
      Promise.resolve().then(function () {
        s.seeking = false;
        try { el.dispatchEvent(new Event("seeked")); } catch (_) {}
        try { el.dispatchEvent(new Event("timeupdate")); } catch (_) {}
      });
    });
    overrideMethod("play", function (el, s) {
      // Native HTMLMediaElement semantics: play() at the end rewinds to 0.
      if (s.ended) {
        s.simCurrentTime = 0;
        s.ended = false;
      }
      if (!s.playing) {
        s.playing = true;
        s.lastTickMs = monotonicNowMs();
        startTick(el, s);
        Promise.resolve().then(function () {
          try { el.dispatchEvent(new Event("play")); } catch (_) {}
          try { el.dispatchEvent(new Event("playing")); } catch (_) {}
        });
      }
      return Promise.resolve();
    });
    overrideMethod("pause", function (el, s) {
      if (s.playing) {
        if (s.lastTickMs !== null) {
          s.simCurrentTime += (monotonicNowMs() - s.lastTickMs) / 1000;
          s.lastTickMs = null;
        }
        s.playing = false;
        stopTick(s);
        Promise.resolve().then(function () {
          try { el.dispatchEvent(new Event("pause")); } catch (_) {}
        });
      }
    });
    overrideMethod("load", function (el) {
      dispatchLoadProgression(el);
    });
    (function () {
      var origCanPlayType = proto.canPlayType;
      try {
        proto.canPlayType = function (type) {
          // MusicKit probes media support before assigning the manifest URL.
          // Firefox builds without native HLS/CDM support otherwise report an
          // empty result and MusicKit falls back to preview/native playback,
          // bypassing the mocked webPlayback + EME path entirely.
          if (typeof type === "string") {
            var mime = type.split(";")[0].trim().toLowerCase();
            if (mime === "application/vnd.apple.mpegurl" || mime === "audio/mpegurl" || mime === "audio/x-mpegurl" || mime === "application/x-mpegurl" || mime === "audio/mp4" || mime === "audio/aac") {
              return "probably";
            }
            if (isMusicKitStack() && /vnd\.apple\.mpegurl|x-mpegurl|mp4|aac/i.test(type)) {
              return "probably";
            }
          }
          return origCanPlayType ? origCanPlayType.apply(this, arguments) : "";
        };
      } catch (_) {}
    })();
    function maybeDispatchEncrypted(mediaEl, url) {
      if (typeof url !== "string" || (!M3U8_REGEX.test(url) && !BLOB_REGEX.test(url))) return false;
      if (mediaEl.__musickitEncryptedDispatched === url) return true;
      var key = keyByUrl[url];
      if (!key) return false;
      mediaEl.__musickitEncryptedDispatched = url;
      var event = new Event("encrypted");
      Object.defineProperty(event, "initDataType", { value: key.initDataType, configurable: true });
      Object.defineProperty(event, "initData", { value: key.initData, configurable: true });
      mediaEl.dispatchEvent(event);
      // The native engine never fires the standard load progression
      // because the synthetic src path skips its load.
      dispatchLoadProgression(mediaEl);
      return true;
    }
  }

  function installMusicKitPlaybackTimeBridge() {
    if (ns.__musicKitPlaybackTimeBridgeInstalled) return;
    ns.__musicKitPlaybackTimeBridgeInstalled = true;
    function currentSyntheticMediaElement() {
      var media = ns.__currentSyntheticMediaElement;
      return media && media.isConnected !== false ? media : null;
    }
    function patchInstance(mk) {
      if (!mk || mk.__musickitApiMockPlaybackTimePatched) return mk;
      mk.__musickitApiMockPlaybackTimePatched = true;
      var origSeekToTime = mk.seekToTime;
      var desc = Object.getOwnPropertyDescriptor(mk, "currentPlaybackTime");
      if (!desc && Object.getPrototypeOf(mk)) {
        desc = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(mk), "currentPlaybackTime");
      }
      var origCurrentPlaybackTimeGet = desc && desc.get;
      try {
        // MusicKit's native currentPlaybackTime does not track the synthetic
        // media element, so read the element clock directly: it advances during
        // playback, reflects seeks, and wraps to 0 when single-song repeat loops
        // past the end boundary. Fall back to the native value only when no
        // synthetic element is attached.
        Object.defineProperty(mk, "currentPlaybackTime", {
          configurable: true,
          enumerable: desc ? desc.enumerable : true,
          get: function () {
            var media = currentSyntheticMediaElement();
            if (media) {
              var t = media.currentTime;
              if (typeof t === "number" && isFinite(t)) return t;
            }
            return origCurrentPlaybackTimeGet ? origCurrentPlaybackTimeGet.call(this) : 0;
          },
        });
      } catch (_) {}
      if (typeof origSeekToTime === "function") {
        mk.seekToTime = function (time) {
          var t = Number(time);
          if (isFinite(t)) {
            try {
              var media = currentSyntheticMediaElement();
              if (media) media.currentTime = t;
            } catch (_) {}
          }
          return origSeekToTime.apply(this, arguments);
        };
      }
      return mk;
    }
    function patchMusicKit() {
      if (!window.MusicKit || window.MusicKit.__musickitApiMockConfigurePatched) return;
      var origConfigure = window.MusicKit.configure;
      if (typeof origConfigure !== "function") return;
      window.MusicKit.__musickitApiMockConfigurePatched = true;
      window.MusicKit.configure = function () {
        var result = origConfigure.apply(this, arguments);
        if (result && typeof result.then === "function") {
          return result.then(function (mk) { return patchInstance(mk); });
        }
        return patchInstance(result);
      };
    }
    patchMusicKit();
    document.addEventListener("musickitloaded", patchMusicKit, { once: true });
  }

  function installForFlavor(flavor) {
    if (flavor === "com.apple.fps") {
      // Force MusicKit JS to take the modern Fairplay EME path (which listens
      // for the standard "encrypted" event) instead of the legacy WebKitMediaKeys
      // path that depends on Safari's native FairPlay binary.
      try { localStorage.setItem("mk-safari-modern-eme", "1"); } catch (_) {}
      installWebKit();
    } else {
      // The init-script snapshot may have installed FairPlay sync paths for
      // a stale flavor; reset the localStorage signal so MusicKit JS doesn't
      // take the modern FairPlay path for a non-fps live value.
      try { localStorage.removeItem("mk-safari-modern-eme"); } catch (_) {}
      if (flavor === "com.microsoft.playready") {
        installMSMediaKeys();
      }
    }
    installSyntheticEncryptedDispatcher();
    installMusicKitPlaybackTimeBridge();
    clearOthers(flavor);
  }

  function setup() {
    // Install the modern EME shim synchronously so the override is in place
    // before MusicKit JS probes navigator.requestMediaKeySystemAccess; the
    // override fetches the configured flavor per-probe so the unset case
    // surfaces loudly instead of mimicking CDM-absent behavior.
    installModernEme();
    // Sync detection probes (WebKitMediaKeys.isTypeSupported,
    // MSMediaKeys.isTypeSupported, the mk-safari-modern-eme localStorage
    // flag) cannot await an async fetch. When the host adapter pre-seeded
    // a static snapshot of eme_flavor, install the legacy detection
    // globals synchronously so probes immediately after the init script
    // don't race the fetch and pick the wrong native path.
    var initialFlavor = ns.browser.eme_flavor || null;
    if (initialFlavor) {
      installForFlavor(initialFlavor);
    }
    // The snapshot can't capture a callable setter or a value the user
    // mutated after get_shim_script() ran; the live fetch covers both.
    fetchFlavor().then(
      function (flavor) {
        if (flavor === initialFlavor) return;
        ns.browser.eme_flavor = flavor;
        installForFlavor(flavor);
      },
      function (err) {
        var msg = err && err.message ? err.message : String(err);
        console.error("[musickit-api-mock] " + msg);
      }
    );
  }

  setup();
})();
