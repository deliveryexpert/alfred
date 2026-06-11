# 🧠 Run history — the permanent scoreboard

This folder is Alfred's memory. Every saved benchmark run lands here as a
`run-<timestamp>.json` file, and `alfred history` reads them all to build the
all-time standings.

**These files are committed to git on purpose.** That's what makes the
scoreboard permanent — it travels with the project, so a contest you run today
is still on the all-time leaderboard in any future session.

To keep a run forever: make sure its `run-*.json` file is committed and pushed.
(Files ending in `.local.json` are treated as throwaway scratch and ignored.)
