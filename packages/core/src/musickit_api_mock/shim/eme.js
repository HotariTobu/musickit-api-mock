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
    var SYNTHETIC_DURATION_SEC = 3600;
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
        s = { playing: false, seeking: false, simCurrentTime: 0, lastTickMs: null, tickHandle: null };
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
        if (s.playing) {
          try { mediaEl.dispatchEvent(new Event("timeupdate")); } catch (_) {}
        }
      }, 250);
    }
    function stopTick(s) {
      if (s.tickHandle === null) return;
      clearInterval(s.tickHandle);
      s.tickHandle = null;
    }
    var fullRange = {
      length: 1,
      start: function (i) { return i === 0 ? 0 : NaN; },
      end: function (i) { return i === 0 ? SYNTHETIC_DURATION_SEC : NaN; },
    };
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
    overrideAccessor("duration", function () { return SYNTHETIC_DURATION_SEC; });
    overrideAccessor("buffered", function () { return fullRange; });
    overrideAccessor("seekable", function () { return fullRange; });
    overrideAccessor("played", function () { return fullRange; });
    overrideAccessor("currentSrc", function (el) {
      var stored = srcByEl.get(el);
      return typeof stored === "string" ? stored : "";
    });
    overrideAccessor(
      "currentTime",
      function (el, s) {
        if (s.playing && s.lastTickMs !== null) {
          return s.simCurrentTime + (monotonicNowMs() - s.lastTickMs) / 1000;
        }
        return s.simCurrentTime;
      },
      function (el, s, v) {
        var t = Number(v);
        if (!isFinite(t)) return;
        s.simCurrentTime = t;
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
    function monotonicNowMs() {
      return window.performance && typeof window.performance.now === "function" ? window.performance.now() : Date.now();
    }
    function currentSyntheticMediaElement() {
      var media = ns.__currentSyntheticMediaElement;
      return media && media.isConnected !== false ? media : null;
    }
    function patchInstance(mk) {
      if (!mk || mk.__musickitApiMockPlaybackTimePatched) return mk;
      mk.__musickitApiMockPlaybackTimePatched = true;
      var seekBase = null;
      var seekBaseMs = null;
      var origSeekToTime = mk.seekToTime;
      var origChangeToMediaAtIndex = mk.changeToMediaAtIndex;
      var desc = Object.getOwnPropertyDescriptor(mk, "currentPlaybackTime");
      if (!desc && Object.getPrototypeOf(mk)) {
        desc = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(mk), "currentPlaybackTime");
      }
      var origCurrentPlaybackTimeGet = desc && desc.get;
      try {
        Object.defineProperty(mk, "currentPlaybackTime", {
          configurable: true,
          enumerable: desc ? desc.enumerable : true,
          get: function () {
            if (seekBase !== null && seekBaseMs !== null) {
              var media = currentSyntheticMediaElement();
              if (media && !media.paused) return seekBase + (monotonicNowMs() - seekBaseMs) / 1000;
              return seekBase;
            }
            return origCurrentPlaybackTimeGet ? origCurrentPlaybackTimeGet.call(this) : 0;
          },
        });
      } catch (_) {}
      if (typeof origSeekToTime === "function") {
        mk.seekToTime = function (time) {
          var t = Number(time);
          if (isFinite(t)) {
            seekBase = t;
            seekBaseMs = monotonicNowMs();
            try {
              var media = currentSyntheticMediaElement();
              if (media) media.currentTime = t;
            } catch (_) {}
          }
          return origSeekToTime.apply(this, arguments);
        };
      }
      if (typeof origChangeToMediaAtIndex === "function") {
        mk.changeToMediaAtIndex = function () {
          seekBase = null;
          seekBaseMs = null;
          return origChangeToMediaAtIndex.apply(this, arguments);
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

  function setup() {
    // Install the modern EME shim synchronously so the override is in place
    // before MusicKit JS probes navigator.requestMediaKeySystemAccess; the
    // override fetches the configured flavor per-probe so the unset case
    // surfaces loudly instead of mimicking CDM-absent behavior.
    installModernEme();
    // Sync WebKitMediaKeys.isTypeSupported / MSMediaKeys.isTypeSupported
    // cannot await an async fetch, so resolve the flavor once and cache it.
    // Sync-path install also gates on this fetch: don't override the legacy
    // detection globals when the configuration is missing or for a different
    // key system, otherwise MusicKit JS picks the wrong native path.
    fetchFlavor().then(
      function (flavor) {
        ns.browser.eme_flavor = flavor;
        if (flavor === "com.apple.fps") {
          // Force MusicKit JS to take the modern Fairplay EME path (which listens
          // for the standard "encrypted" event) instead of the legacy WebKitMediaKeys
          // path that depends on Safari's native FairPlay binary.
          try { localStorage.setItem("mk-safari-modern-eme", "1"); } catch (_) {}
          installWebKit();
        } else if (flavor === "com.microsoft.playready") {
          installMSMediaKeys();
        }
        installSyntheticEncryptedDispatcher();
        installMusicKitPlaybackTimeBridge();
        clearOthers(flavor);
      },
      function (err) {
        var msg = err && err.message ? err.message : String(err);
        console.error("[musickit-api-mock] " + msg);
      }
    );
  }

  setup();
})();
