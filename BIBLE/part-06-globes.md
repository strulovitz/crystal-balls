# Crystal Balls — The Bible
## Part 6 — The Three Nested Globes (the web page)

### 6.1 What the visitor sees

A full-screen dark scene. In the middle floats a large white wireframe globe with country outlines. Inside it, visible through the wires, a slightly smaller light-gray wireframe globe, and inside that a small dark-gray one. On each globe, the 32 countries carry a card: a large flag with three emojis in a row underneath. The outer globe's cards are bright and show the forecast for the coming week. The middle globe's cards are dimmed by one third and show what actually happened this past week. The inner globe's cards are dimmed by two thirds and show what happened the week before. The whole thing rotates slowly on its own until the visitor touches it; then it follows the finger or the mouse. All three globes rotate together, so each country's three cards stay in a vertical column: forecast on top, this week under it, last week under that. Hovering or tapping a country lights up its column and draws a thin line through its three cards. Clicking opens a panel with the headline, the emojis, and a TLDR; "Read more" opens the ELI5, the five scored statements, and the story of how we got here.

### 6.2 Layer definition (this supersedes the wording in Part 0.5)

For the selected round R (default: the latest complete round) and its previous round P:

Outer globe, layer 2: display.emojis of R, the Crystal forecast for the coming week. Legend text: "Next week, forecast".
Middle globe, layer 1: position.emojis of R, what happened in the window that just ended. Legend text: "This week, what happened".
Inner globe, layer 0: position.emojis of P, what happened the week before. Legend text: "Last week, what happened".

If P does not exist, the inner globe shows its wireframe only and the legend says "Last week: no data yet". If a country file is missing in a round, that country's card is omitted on that layer only.

### 6.3 Files

```
site/
  index.html
  app.js              ES module
  style.css
  about.html          placeholder for the marketing page (written later), linked from the header
  data -> ../data     a git-committed relative symlink, so the page finds data/index.json
  assets/
    icon.png
    og.png            1200x630 share image; placeholder copy of icon.png until a screenshot exists
    emoji/            Twemoji 72x72 PNGs, downloaded by build_site_data.py
    vendor/
      three.module.min.js
      OrbitControls.js
      topojson-client.min.js
    countries-110m.json
```

Vendored files are downloaded once by build_site_data.py if missing, from:

```
https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js
https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js
https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js
https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json
```

OrbitControls.js imports from 'three'; index.html therefore has an import map that maps three to ./assets/vendor/three.module.min.js. Deviation from Rule 9, stated plainly: the page uses the vendored files only, no CDN at runtime. Reason: fewer moving parts and the page works even when a CDN is blocked. Total weight is under 1.5 MB, acceptable.

Emoji PNGs come from the maintained Twemoji fork:

```
https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/[twemoji].png
```

build_site_data.py downloads every flag in config/countries.json and every emoji in config/emoji_vocabulary.json plus the question mark emoji, skipping files that already exist. If a file 404s, it retries the code with -fe0f appended, then reports the failure.

### 6.4 Data the page loads (produced by pipeline/build_site_data.py)

data/index.json as in Part 2.8.

data/meta.json: a copy of config/countries.json (without the keywords field), the full emoji vocabulary, and the group display names from Part 2.2.

data/rounds/[R]/bundle.json: one object with round (the content of round.json) and countries (an object keyed by country code containing the full country file). One fetch per round instead of 32. Built for every complete round; rebuilt every time build_site_data.py runs.

data/scorecard.json as in Part 2.9.

The page therefore makes at most five requests: index.json, meta.json, scorecard.json, bundle of R, bundle of P. All paths are relative (data/index.json), never absolute, so the page works both at /crystal-balls/ on the live site and on a local test server.

### 6.5 Scene construction

Camera: PerspectiveCamera, fov 38, initial distance 3.2 from the origin, looking at the origin. On narrow screens (width under 700 px) the distance is 3.9 so the outer globe fits the width with margin. Camera distance limits for zoom: 1.9 to 5.5.

Controls: OrbitControls with enablePan = false, enableDamping = true, dampingFactor = 0.06, rotateSpeed = 0.6, autoRotate = true, autoRotateSpeed = 0.35. Auto-rotation stops at the first user interaction and resumes after 25 seconds without interaction. Touch: one finger rotates, two fingers zoom.

Lat/lng to 3D (Three.js is Y-up). For radius r, latitude lat and longitude lng in degrees:

```js
function latLngToVector3(lat, lng, r) {
  const phi = (90 - lat) * Math.PI / 180;
  const theta = (lng + 180) * Math.PI / 180;
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  );
}
```

The same function is used for outlines and for cards, so they always align.

Three globes with radii and colors:

```
layer 2 outer:  radius 1.00, outlines color #ffffff opacity 0.85, graticule #ffffff opacity 0.10
layer 1 middle: radius 0.74, outlines color #b9c2cc opacity 0.55, graticule #b9c2cc opacity 0.07
layer 0 inner:  radius 0.50, outlines color #6b7078 opacity 0.50, graticule #6b7078 opacity 0.06
```

Country outlines: load countries-110m.json, convert with topojson.mesh(topology, topology.objects.countries) to a MultiLineString, then build one LineSegments per globe by mapping each coordinate through latLngToVector3. Use LineBasicMaterial with transparent = true and the opacity above (line width is always 1 px in WebGL; that is fine). Graticule: lines every 15 degrees of latitude and longitude, built procedurally, 72 segments per line.

Faint fill: each globe also gets a SphereGeometry with MeshBasicMaterial, color #0b1220, transparent = true, opacity 0.10 for the outer, 0.08 for the middle, 0.06 for the inner, depthWrite = false. This gives the glass feel without hiding the inner layers.

Background: CSS radial gradient on the body from #101a33 at the center to #05070d at the edges. Add 600 tiny star points (THREE.Points, size 1.2 px, white, opacity 0.6) on a sphere of radius 40 so the scene feels deep. On narrow screens use 300 stars.

Renderer: antialias = true, alpha = true, pixel ratio capped at 2, resized on window resize and on orientation change.

### 6.6 The cards (flag plus three emojis)

Each country on each layer is one THREE.Sprite whose texture is drawn once on an offscreen canvas:

Canvas size 256 x 232 pixels (drawn at device pixel ratio for crispness). Transparent background. The flag PNG is drawn centered at the top at 144 x 144 pixels (twice the size of the emojis). Under it, the three emoji PNGs at 72 x 72 each, with 8 px gaps, centered, so the row is 232 px wide. A soft shadow (shadowBlur = 12, black at 0.6 alpha) behind the flag and emojis keeps them readable over the white wires. No text on the card; the country name appears on hover and in the panel.

Sprite world sizes (width x height), tuned so the outer flag is about 44 px tall on a 1080p screen at the default distance:

```
layer 2 outer:  0.26 x 0.235
layer 1 middle: 0.21 x 0.19
layer 0 inner:  0.17 x 0.154
```

Dimming is done through the sprite material color, which multiplies the texture:

```
layer 2: color #ffffff   (not darkened)
layer 1: color #aaaaaa   (one third darkened)
layer 0: color #585858   (two thirds darkened)
```

Sprite position: the card's anchor is latLngToVector3(lat, lng, radius * 1.015) on its own globe. To make the three cards of a country form a vertical column on screen, use sprite.center: outer card center = (0.5, 0.0) so it sits above its anchor; middle card center = (0.5, 1.08) so it hangs just below its anchor; inner card center = (0.5, 2.55) so it hangs below the middle one. These values are starting points; the implementer tunes them until the three cards of a country directly facing the camera form a tight column with roughly 6 px gaps and no overlap.

All sprite materials use transparent = true, depthWrite = false, depthTest = false, and renderOrder 10 for inner, 20 for middle, 30 for outer, so the forecast card always draws on top.

Back-side culling and fading, every frame: for each sprite compute d = dot(normalize(anchor), normalize(cameraPosition)). Then:

```
outer:  visible when d > 0.02;  opacity = clamp((d - 0.02) / 0.25, 0, 1)
middle: visible when d > 0.30;  opacity = clamp((d - 0.30) / 0.25, 0, 1) * 0.95
inner:  visible when d > 0.45;  opacity = clamp((d - 0.45) / 0.25, 0, 1) * 0.90
```

So the inner layers appear only for countries near the center of the view, where their column reads clearly, and the limb of the globe shows forecasts only. Countries rotate into their columns as the visitor turns the globe.

Textures are built once per round load and disposed when the round changes. Build them asynchronously after all PNGs are loaded; show the loading screen until the first frame renders with cards.

### 6.7 Hover and selection

Raycasting: THREE.Raycaster against all visible sprites on pointermove (desktop) and pointerup (all devices, only if the pointer moved less than 6 px since pointerdown, so drags do not select). The raycaster reads sprite.userData.code and sprite.userData.layer.

Hover state (desktop only): the three cards of the hovered country go to full opacity and the hover color (#ffffff on all three layers), every other card drops to 0.3 of its computed opacity, a THREE.Line with color #6ee7f9 and opacity 0.8 is drawn through the three anchors, and a small HTML label with the country name and the forecast headline follows the cursor. The cursor becomes a pointer.

Selected state: same highlighting as hover, kept until the panel closes; plus the camera animates over 900 ms (ease in-out) so the country faces the camera. Implement the animation by rotating the whole globe group's quaternion toward the quaternion that brings the country's anchor to the camera direction. Auto-rotate pauses while a country is selected.

Selection also updates the URL hash to #round=[R]&country=[CODE]. On load, if the hash contains a country, the page selects it after the first render. If it contains a round that exists in index.json, that round is loaded.

### 6.8 The country panel

HTML, not 3D. On screens wider than 900 px it is a card 400 px wide docked to the right, full height minus margins, with the globe still visible and interactive on the left. On narrower screens it is a bottom sheet covering 55 percent of the height, draggable to full height, with the globe dimmed behind it. Glass look: background rgba(10, 16, 32, 0.78), backdrop-filter: blur(14px), 1 px border rgba(255,255,255,0.12), radius 18 px.

Panel content, top to bottom:

1. Header row: the flag PNG at 40 px, the country name (24 px, weight 600), the group display name as a small pill, and a close button.
2. Round line: "Forecast made [label of R] for the week to [horizon_end]". For legacy rounds: "Manual round, [label]".
3. The forecast headline in 20 px, weight 600, color #e8f0ff.
4. Three forecast emojis as 48 px PNGs in a row, each with its vocabulary meaning as a tooltip (title attribute) and the model's emoji_reasons sentence shown under the row in 13 px gray when the visitor taps or hovers an emoji.
5. TLDR paragraph, 16 px, line height 1.55.
6. "How we got here" block, three compact rows with a small colored dot each (dark gray, light gray, white): "Last week" with the inner emojis at 22 px and the first sentence of P's position summary; "This week" with the middle emojis and the first sentence of R's position summary; "Trend" with R's velocity.direction and velocity.summary first sentence. Rows with missing data say "no data".
7. Score line, shown only when R's wind exists and winner is not none: "Last week's forecast check: Crystal Balls [b_c] vs plain forecast [b_n], lower is better, winner: [winner]". Colored green when crystal won, amber when tie, red when naive won.
8. Buttons: "Read more" (primary), "Copy link", "Raw JSON" (opens data/rounds/[R]/countries/[CODE].json in a new tab).

"Read more" opens a full-screen modal (max width 760 px, scrollable, same glass style) containing:

1. The same header row and headline.
2. "In plain words" with the ELI5 paragraphs (the text contains blank lines; render each as a paragraph).
3. "Five things we are watching" with the five crystal statements. Each statement is a row: a horizontal probability bar (CSS, 8 px tall, filled proportionally, color from red at 0.05 through amber at 0.5 to green at 0.95), the percentage as text, the statement text, and the domain as a small pill. If outcomes exist for these statements (they will, once the next round is published and the visitor views an older round), a check mark or cross and the evidence sentence appear under the statement. Note for the implementer: outcomes for round R's statements live in round R+1's wind section; when the page has R+1 loaded in index.json, fetch its bundle lazily to show them. If not available, show nothing about outcomes.
4. "Why the Crystal forecast differs from a plain reading" with crystal_forecast.reasoning.
5. "The plain forecast, for comparison" with naive_forecast.summary and its five statements, same row style.
6. "What happened this week" with R's position.summary and the key events as a bulleted list with dates.
7. "What changed since last week" with velocity summary, then three short lists: rising, fading, new.
8. "Wind: how last week's forecasts missed" with wind.systematic_error and wind.correction_hint, when present.
9. Footer line with the model name and generated_at.

Never use HTML tables in the panel or modal; use flex rows.

### 6.9 Header, legend, round selector, scorecard badge

Header bar across the top, transparent background, content: left, the icon and the title "Crystal Balls" in 22 px with a subtle cyan glow, subtitle under it in 13 px: "Next week's news, forecast from this week's momentum". Center, a round selector: a native select element styled dark, listing index.json rounds by label, newest first, with "(manual)" suffix for legacy rounds. Right: a country picker (native select, options grouped by group display name with optgroup), a "How it works" link to about.html, and a "List view" toggle. On narrow screens the header collapses to the icon, the title, and a menu button that reveals the selectors and links as a dropdown.

Scorecard badge: directly under the header on the left, a pill reading "Crystal Balls beat the plain forecast in [crystal_wins] of [crystal_wins + naive_wins] country-weeks ([win rate]%)". Clicking it opens a small modal with: the sentence "A forecaster who always says 50 percent scores 0.25. Lower is better."; mean Brier crystal vs naive; the per-round numbers as compact rows; and a link to data/scorecard.json. When country_rounds_scored is 0, the badge reads "Scorecard starts after the second automated round".

Legend: bottom left, three small concentric ring icons drawn in CSS (white, light gray, dark gray) with the three legend texts from 6.2, one per line. On narrow screens the legend becomes a single line of three short items under the header: "Outer: next week", "Middle: this week", "Inner: last week".

Footer line: bottom right, 12 px gray: "Made at home with a free local AI by Nir Strulovitz · open source and open data on GitHub · strulovitz.org". Links open in a new tab.

Loading screen: full-screen overlay with three pulsing concentric rings and the text "Polishing the crystal balls..." until the first frame with cards renders. Error screen: if index.json fails to load, show "No forecast rounds published yet. Come back soon." If WebGL is not available, switch to list view automatically with a one-line note.

### 6.10 List view

A toggle hides the canvas and shows a scrollable list of all 32 countries for round R, grouped by group display name. Each item: flag PNG 32 px, country name, three forecast emojis at 24 px, the headline, and the TLDR; clicking opens the same panel. This view also serves screen readers and search engines; it is rendered into the DOM at load (hidden with CSS when the globe is shown), so the page has real text content.

### 6.11 Performance and mobile

Pixel ratio capped at 2. 96 sprites plus three line sets are cheap; target 60 fps on a mid-range phone. Build canvas textures in a requestIdleCallback chain (or setTimeout 0 batches of 8) so the loading screen stays smooth. Fonts: system stack only (-apple-system, Segoe UI, Roboto, Ubuntu, sans-serif), no web fonts. All tap targets at least 44 px. Test in Chrome and Firefox on Linux, in Chrome on Android, and in Safari on iPhone if available (iOS needs -webkit-backdrop-filter). Nothing on the page depends on flag emoji font support; every emoji is a PNG.

### 6.12 index.html essentials

The head contains: charset, viewport (width=device-width, initial-scale=1, viewport-fit=cover), title "Crystal Balls — next week's news, forecast from this week's momentum", a meta description of one sentence, OpenGraph and Twitter card tags pointing at assets/og.png and the canonical URL https://www.strulovitz.org/crystal-balls/, the favicon assets/icon.png, the stylesheet, and the import map:

```html
<script type="importmap">
{ "imports": { "three": "./assets/vendor/three.module.min.js" } }
</script>
<script type="module" src="./app.js"></script>
```

topojson-client is a classic script loaded with a plain script tag before the module, exposing the global topojson.

### 6.13 Demo data and the development server

pipeline/make_demo_data.py writes two complete synthetic rounds into demo/data/rounds/2000-01-01 and demo/data/rounds/2000-01-08 plus demo/data/index.json, meta.json, scorecard.json and bundles, using random vocabulary emojis, plausible placeholder sentences, random statements with probabilities, and a wind section in the second round so the score line and outcome marks can be tested. It copies the emoji PNGs it needs from site/assets/emoji. Demo data is committed so anyone can run the page without a model.

scripts/dev_server.sh [--demo] builds a staging folder in /tmp/crystal-balls-dev with a copy of site/ and a copy of either data/ or demo/data/ placed as data/, then runs python3 -m http.server 8090 there and prints the URL. It is for testing only; the real publishing is Part 8.

### 6.14 Visual polish checklist

The outer globe is clearly white, the middle clearly gray, the inner clearly dark; a stranger must see the nesting within one second. Cards never jitter: sprites are positioned once, only opacity and color change per frame. Hover reactions complete within 150 ms with CSS transitions on the HTML label. The panel slides in over 250 ms. The probability bars animate from zero to their width when the modal opens. Nothing flashes white during load; the background gradient is painted by CSS before any script runs. Screenshot the final result at 1920x1080 and at 390x844 and save them as site/assets/og.png (crop to 1200x630) and docs/screenshot-mobile.png.

### 6.15 Done criteria for Part 6

python3 pipeline/build_site_data.py downloads the vendor files, the world atlas, and all emoji PNGs (reporting any failures), and produces meta.json, index.json, scorecard.json and bundles from whatever rounds exist. python3 pipeline/make_demo_data.py produces the demo rounds. scripts/dev_server.sh --demo serves a page where: three nested wireframe globes rotate together; 32 countries show flag-plus-three-emoji cards on all three layers with the specified dimming; the cards of a country facing the camera form a column; hover highlights a column and draws the connector line; click opens the panel with headline, emojis, TLDR, the three "how we got here" rows, and the score line; "Read more" opens the modal with ELI5, probability bars, both forecasts, position, velocity and wind; the round selector switches between the two demo rounds; the country picker rotates the globe to the chosen country; list view works; the URL hash deep link works; the page works on a phone-sized viewport in the browser's device emulation. The implementer sends Nir the two screenshots and commits everything.
