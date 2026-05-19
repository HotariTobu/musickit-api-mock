(function () {
  var ns = (window.__musickitApiMock = window.__musickitApiMock || {});
  ns.browser = ns.browser || {};

  var ORIGIN = "https://authorize.music.apple.com";
  var AUTHORIZE_PREFIX = ORIGIN + "/woa";
  var INTERNAL_URL =
    "https://musickit-api-mock.invalid/browser/authorize_response";

  function makeStubWindow() {
    var stub = {
      closed: false,
      postMessage: function (_msg, _target) {},
      focus: function () {},
      close: function () {
        stub.closed = true;
      },
    };
    Object.defineProperty(stub, "self", {
      get: function () {
        return stub;
      },
    });
    Object.defineProperty(stub, "window", {
      get: function () {
        return stub;
      },
    });
    return stub;
  }

  function dispatchMethod(method, params) {
    var ev = new MessageEvent("message", {
      data: { jsonrpc: "2.0", method: method, params: params },
      origin: ORIGIN,
      source: window,
    });
    window.dispatchEvent(ev);
  }

  function deliverResponse(stub) {
    fetch(INTERNAL_URL)
      .then(function (r) {
        if (!r.ok) {
          throw new Error("HTTP " + r.status);
        }
        return r.json();
      })
      .then(function (resp) {
        var kind = resp && resp.kind;
        if (kind === "AuthorizeSuccess") {
          dispatchMethod("authorize", [
            resp.user_token || "",
            String(resp.restricted == null ? 0 : resp.restricted),
            resp.cid || "",
          ]);
        } else if (kind === "AuthorizeDecline") {
          dispatchMethod("decline", []);
        } else if (kind === "AuthorizeClose") {
          dispatchMethod("close", []);
          stub.closed = true;
        } else if (kind === "AuthorizeSwitchUserId") {
          dispatchMethod("switchUserId", []);
        } else if (kind === "AuthorizeUnavailable") {
          dispatchMethod("unavailable", []);
        } else {
          console.error(
            "[musickit-api-mock] unknown authorize_response kind: " + kind
          );
        }
      })
      .catch(function (e) {
        console.error("[musickit-api-mock] " + (e && e.message ? e.message : e));
      });
  }

  var origOpen = window.open;
  window.open = function (url, ...rest) {
    if (typeof url === "string" && url.indexOf(AUTHORIZE_PREFIX) === 0) {
      var stub = makeStubWindow();
      deliverResponse(stub);
      return stub;
    }
    return origOpen.call(window, url, ...rest);
  };
})();
