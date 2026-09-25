# Recipes

Task-oriented snippets — pick the goal, read the snippet. For background on the surfaces these snippets configure, see [Surfaces overview](https://hotaritobu.github.io/musickit-api-mock/0.4.0/guide/surfaces/index.md).

## Recipe index

| Goal                                                                    | Recipe                                                                                                                             |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Stand up the "signed in, paid up" baseline before driving anything else | [Signed-in with subscription](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/signed-in-with-subscription/index.md)   |
| Trigger a subscription error from playback or license acquisition       | [Subscription expired mid-playback](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/subscription-expired/index.md)    |
| Force a DRM (FairPlay / Widevine / PlayReady) failure                   | [DRM license failure](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/drm-license-failure/index.md)                   |
| Serve different storefronts across tests reusing one mock               | [Multiple storefronts](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/multi-storefront/index.md)                     |
| Generate catalog resources on the fly instead of enumerating ids        | [Callable resolvers](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/callable-resolvers/index.md)                     |
| Play a song the user uploaded to their library (no catalog counterpart) | [Uploaded library song](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/uploaded-library-song/index.md)               |
| Cover popups and pages opened later in one binding                      | [Bind to a browser context](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/bind-to-context/index.md)                 |
| Vary the authorize result between tests without re-creating the page    | [Swap authorize between tests](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/swap-authorize-between-tests/index.md) |

Note

Got a scenario that's not covered? Open an issue with the snippet that worked — recipes here track real usage rather than speculative coverage.
