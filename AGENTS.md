# RULE FOR EVERY AGENT IN THIS REPO (Nir, 4 Nov 2026): THE SITE FOLDER LAW

Nir serves all his websites from TWO computers, one at a time (laptop and desktop; the desktop half of the
time or more). Each serves what it pulled from GitHub. Everything the website serves (public/) must be
tracked by git and pushed. .gitignore holds only passwords and machine junk, never anything under public/.
Never say "pushed", "published" or "done" until `git status --porcelain --ignored public` is empty, nothing is
ahead of origin, and a fresh clone served locally loads with zero errors. Push only what Nir asks for, by name.
Details: BIBLE/part-08-publishing.md section 8.11. Shared rule: github.com/strulovitz/claude-memory
feedback_website_complete_on_github.md.
