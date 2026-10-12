# Response-link languages

Requests carrying a valid `l` parameter propagate their effective language to
all `href` and `next` fields in successful catalog and personal-library/me JSON
responses, including nested relationships. Pagination links put `l` before the
offset. Existing query values and fragments are preserved; existing `l` values
are replaced rather than duplicated.

Requests without `l` do not gain it. Empty values and values containing an
underscore retain the existing absent-language treatment. Invalid language
inputs retain the existing validation errors. This does not translate fixture
attributes: data callbacks continue to receive the request's existing locale.
Following a normalized link naturally supplies that emitted locale on the next
request.

## Storefront selection and fallback

Catalog requests use the storefront in their path. Library/me requests use the
configured `mock.endpoints.storefront`; its callable is resolved at most once
per request so catalog relationships and response languages stay consistent.
The next request resolves it again.

The lookup first applies narrowly scoped observed aliases, then matches a
supported language tag case-insensitively, then uses the storefront's default.
It deliberately does not strip arbitrary region or script subtags. For example,
US `es` falls back to `en-US`, although `es-MX` is supported; Canadian `fr`
falls back to `en-CA`, whereas `fr-CA` stays `fr-CA`.

For unknown or unverified storefronts, the original request tag is preserved
and URL-encoded. Explicitly configured language metadata can supply an exact
match or default for an unknown library storefront. An unset storefront is not
fabricated merely to localize a link.

## Evidence and coverage

An authenticated catalog probe on **2026-10-11**, from 15:15:16Z through
16:09:37Z, fetched live `/v1/storefronts` metadata and queried genre `34` on
`api.music.apple.com` across **172 storefronts**. The captured matrix includes:

- Every listed supported tag, its lowercase/uppercase forms, and its primary
  language subtag, with duplicate inputs removed
- Shared candidates `ja`, `ja-JP`, `en`, `en-US`, `en-GB`, `en-AU`, `fr`,
  `fr-CA`, `es`, `es-MX`, `de`, `zh`, `zh-TW`, `pt-BR`, and `ko`
- Absent, empty, and `invalid-control` inputs

The **3,795 observations** comprise 3,600 successful responses, 172 invalid-input
400 responses, and 23 Russian-storefront 404 responses. Successful explicit
language inputs provide **3,258 observed mappings across 171 storefronts**.
All planned pairs are present, with no duplicate pairs or conflicting
case-insensitive outcomes. The implementation expresses those outcomes with
171 language profiles and 38 narrowly scoped alias overrides, rather than
storing thousands of repeated default mappings.

France's `en-GB` response remains `en-GB`; this is a measured exception to
interpreting the earlier issue's “every tag tried” note as a universal rule.
Other examples include Japanese `en` to `en-US`, Swiss `de` to `de-DE`, and
Hong Kong `zh-TW` to `zh-Hant-TW`.

The credential-free capture is checked into
`packages/core/tests/fixtures/apple_language_observations.json`. Tests replay
every successful captured link and every storefront's invalid-input control.
The capture includes statuses, input/output tags, public API links, timestamps,
and storefront metadata, with no authentication headers or credentials.

## Limits

- **Russia is unverified:** all 23 non-invalid requests returned 404. Its
  normalization is not guessed from metadata. The mock does not reproduce a
  live storefront-availability 404 merely because the probe saw one; fixture
  availability remains controlled by the caller.
- This is a finite matrix on one catalog resource and date, not every possible
  BCP 47 string, resource, subscription, or account. Case handling and fallback
  outside the observed inputs are conservative mock rules, not newly verified
  Apple behavior.
- Broad library/me and nested-link propagation is supported by the earlier
  [issue #49 observations](https://github.com/HotariTobu/musickit-api-mock/issues/49).
  The new sweep did not separately repeat authenticated library probes for all
  storefronts.
- Apple's supported tags and normalization can change. Extend profiles and
  narrowly scoped aliases together with credential-free observations and tests;
  do not infer a universal primary-language matching rule.

Apple documents supported/default storefront languages in
[Storefronts and Localization](https://developer.apple.com/documentation/applemusicapi/storefronts-and-localization)
and the [storefront attributes](https://developer.apple.com/documentation/applemusicapi/storefronts/attributes-data.dictionary).
Those documents describe metadata, not the complete normalization algorithm.
