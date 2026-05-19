(function () {
  // Polyfill navigator.connection (NetworkInformation API) for browsers where
  // it is absent. MusicKit JS reads connection.downlink to derive the initial
  // playback bitrate; without it, only STANDARD-bitrate flavors are accepted
  // from webPlayback responses.
  if (navigator.connection && typeof navigator.connection.downlink === "number") {
    return;
  }
  try {
    Object.defineProperty(navigator, "connection", {
      configurable: true,
      get: function () {
        return { downlink: 10, effectiveType: "4g" };
      },
    });
  } catch (_) {}
})();
