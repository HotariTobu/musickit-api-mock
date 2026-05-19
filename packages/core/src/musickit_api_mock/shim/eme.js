(function () {
  var ns = (window.__musickitApiMock = window.__musickitApiMock || {});
  ns.browser = ns.browser || {};

  function getFlavor() {
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
        var flavor = getFlavor();
        if (flavor !== keySystem) {
          return Promise.reject(
            new DOMException(
              "Unsupported keySystem: " + keySystem,
              "NotSupportedError"
            )
          );
        }
        return Promise.resolve(makeStubAccess(keySystem, configurations));
      },
    });
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
      var flavor = getFlavor();
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
      var flavor = getFlavor();
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

  function setup() {
    var flavor = getFlavor();
    // Always install the modern EME shim so navigator.requestMediaKeySystemAccess
    // resolves or rejects synchronously. Without it, browsers without a CDM
    // (e.g. Firefox playwright builds without Widevine) can hang ~120s before
    // the native call rejects.
    installModernEme();
    if (flavor === "com.apple.fps") {
      // Force MusicKit JS to take the modern Fairplay EME path (which listens
      // for the standard "encrypted" event) instead of the legacy WebKitMediaKeys
      // path that depends on Safari's native FairPlay binary.
      try { localStorage.setItem("mk-safari-modern-eme", "1"); } catch (_) {}
      installWebKit();
      clearOthers("com.apple.fps");
    } else if (flavor === "com.microsoft.playready") {
      installMSMediaKeys();
      clearOthers("com.microsoft.playready");
    } else {
      clearOthers(flavor);
    }
  }

  setup();
})();
