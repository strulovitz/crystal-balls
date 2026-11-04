# HANDOFF FOR THE LAPTOP AI: CRYSTAL BALLS public/ WAS NEVER ON GITHUB (4 Nov 2026)
Written by Claude Sonnet 5.5 on Nir's desktop-linux. Nir is NOT your messenger: after `git pull`
read this yourself and do only what it says. Emojis on every line to Nir, short messages, the
important thing LAST. Never `pkill -f`. Never say "published" before checking the real URL.
Nir was furious about this exact class of mistake. It happened on 3 projects today.

## WHAT WAS WRONG
The live page www.strulovitz.org/crystal-balls/ is served by Caddy straight from
`~/crystal-balls/public/` (strulovitz-website/hosting/Caddyfile). `.gitignore` contained the line
`public/`, so ALL 359 files of the website (16 MB) existed only on the desktop. Nir serves from
two PCs (desktop and laptop, one at a time). A `git pull` on the laptop produced NO website:
`/crystal-balls/` would have been 404 there. Same disease as Second Opinion (site/data/ ignored)
and the Demoscene Museum (landing folder never served).

## WHAT THE DESKTOP AI DID (pushed)
1. `.gitignore`: removed `public/`. Left ONLY secrets and machine junk: config/settings.env,
   .venv/, __pycache__, *.pyc, logs/*.tmp, data/tmp/. Nir's rule: the forbidden list contains
   passwords and junk ONLY, never anything the website serves.
2. `git add` of all 359 public/ files, committed and pushed.
3. `scripts/publish.sh` now ends by committing public/ and pushing it, and EXITS WITH AN ERROR if
   the push fails or if anything under public/ is ignored or untracked. It must never again say
   "Publish done" while the other computer cannot get the files.

## WHAT YOU DO, IN ORDER
1. `git -C ~/crystal-balls pull`. Confirm `ls ~/crystal-balls/public` shows index.html, app.js,
   style.css, about.html, assets/, data/ (NO publish.sh run needed: that is the whole point).
2. Prove it from a blank slate: `git clone https://github.com/strulovitz/crystal-balls.git /tmp/cb-test`,
   serve `/tmp/cb-test/public` with `python3 -m http.server` and with headless Chrome (CDP, use
   127.0.0.1) confirm the page loads, the country data loads and there are zero console errors.
   Delete /tmp/cb-test afterwards.
3. Write the rule into the BIBLE of Crystal Balls (you are the only one allowed to edit it; the
   desktop AI was told not to): a section in Part 8 (publishing) "The Site Folder Law": everything
   the website serves is tracked by git; the forbidden list holds secrets and junk only; a pull on
   any computer gives a working site; publish.sh enforces it; the clone test above is how a new
   session proves it. Also add it to AGENTS.md and the handoff file at the top of BIBLE/HANDOFF-FOR-FABLE.md.
   Mention the same law exists in second-opinion (Law 16).
4. If the laptop is the one serving: `systemctl --user restart site-caddy.service`, then curl
   `http://127.0.0.1:8081/crystal-balls/` and the public URL. (Never both tunnels at once.)
5. Tell Nir the real results in two short lines.

## FOR EVERY FUTURE PUBLISH
Run `scripts/publish.sh`. If it prints a push failure, the round is NOT published. Fix first.
