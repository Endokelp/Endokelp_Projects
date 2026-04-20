# Pre-push vibe pass

Run this before `git push`. Cursor may stop the command until you confirm—that’s intentional.

## Detective subagent (paste into Task / another agent)

You’re the prosecution: argue this repo was **vibe coded** (AI slop, sterile templates, zero personal voice). Scan the repo; skip `node_modules` and build artifacts.

Return:

1. Verdict: `fine` / `meh` / `yikes`
2. Exhibits: path + what looks wrong
3. Ship blockers vs nitpicks

Only cite what you actually opened or grepped.

## Five-minute human version

- Search the template for obvious template junk (dummy names, fake jobs, filler Latin).
- README: does it read like a person wrote it?
- `index.html`: giant keyword meta blocks are a red flag (this site shouldn’t have those).

Then push again.
