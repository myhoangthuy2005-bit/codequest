# CodeQuest · Campus Codebreakers — Web Edition

One target. Six cards. Can you find every match?

A browser interface for the COMP9001 Python revision game. Python handles question
selection, scoring, lives, duel turns, timers, persistence and Code Lab evaluation.
HTML, CSS and JavaScript provide the responsive interface. The desktop edition is
preserved separately; this folder is a complete, independent web edition.

## Start in three steps

1. Install Python 3.10 or newer if it is not installed.
2. Open a terminal inside this extracted `codequest-web` folder.
3. Run `python3 server.py` (Windows: `py server.py`), then open
   **http://127.0.0.1:8000** in your browser.

Keep the terminal running while playing. Ctrl+C stops the server. No pip, Node,
npm or Tkinter is required. Do not open index.html directly; it needs Python.
If port 8000 is occupied, run `python3 server.py --port 8001` and open port 8001.

## Features

- 54 card questions / 324 cards across nine topics and three difficulty levels.
- Free topic practice, mixed revision, adaptive progression and five-question
  daily challenges. Topic changes during ordinary practice preserve session lives.
- Guided tutorial with an unscored practice round.
- Local two-player duels: 5, 15 or 54 rounds per player, same topic/difficulty with
  different question variants. Both players finish each numbered round before
  evaluating zero lives. Ties use points. Two individual summaries appear.
- Three lives per session. Exact value AND type matching, server-side scoring,
  concept/count/eliminate hints with cumulative point costs.
- A 45/90-second optional Python-controlled timer. Pause, hints and lessons stop
  it. A timeout costs one life and produces an explanation.
- 27 Code Lab expression exercises evaluated by a bounded Python AST interpreter,
  not arbitrary eval/exec. Imports, attributes and arbitrary calls are disabled.
- Nine mini-lessons, answer explanations, saved mistake notebook, targeted
  practice, strengths/practice summaries, wins/losses and accuracy.
- Named local profiles, five achievement badges with progress, earned coins,
  Campus Shop themes and consistent monospaced code typography.
- An ornate gold target card and clear spacing above and below its value.
- Larger text, high contrast, labelled states, reduced-motion support, keyboard
  controls and layouts that stack on narrow screens.
- Looping original Campus evening instrumental, volume control and action chimes.
  Browsers may require a click before allowing audio: Settings → Start music.
- TXT and CSV report downloads. Daily replay scores can improve; coin rewards
  apply only to the first attempt at each daily question for that date.

## Progress and privacy

Completed rounds, profiles, settings, notebooks, coins and daily records save to
`~/.codequest/profiles.json` on the computer RUNNING THE PYTHON SERVER. This is the
same format and default location as the desktop edition, so existing profiles can
be reused. Do not run both editions simultaneously against the same save file.

To use a separate save file: `python3 server.py --data ./local-data/profiles.json`.
The data folder is excluded by .gitignore. JSON writes use atomic replacement;
damaged saves are preserved and a warning is displayed. Back up your data.

The browser has an HttpOnly session cookie. Current uncompleted rounds are kept
in server memory; restarting Python ends them, while completed progress survives.
Tabs in the same browser share that cookie and should not run simultaneous games.
There are no online logins: local profile names are selectors, not authentication.

## GitHub and hosting

Upload this folder's CONTENTS into a repository, including static/assets, tests
and README.md. Exclude caches and local-data. No ZIP extraction is needed in the
repository itself. A repository URL shows source code; it is not a live game URL.
**GitHub Pages cannot run this Python backend.**

This release is intended to run on localhost on a trusted computer. It is not
publicly hosted. Online deployment requires Python hosting and a production server
setup. Before opening it to unrelated visitors, add visitor-isolated storage or
authentication: the current local profile list, progress and exports are shared
by people using the same server. It is not an account-based multi-user service.

Do not change --host to 0.0.0.0 for public deployment without adapting that data
model and deployment setup. The included development command is for preview only.
The project remains predominantly Python in its game and persistence logic.

## Controls and rules

Click cards or use 1–6; Enter submits. Escape opens pause/back. Each card starts
fresh: evaluate its final expression after its setup lines. Hints cost 40 (count),
20 (concept) and 30 (eliminate) points, once each; combined hints leave at least
20 perfect-round points. Code Lab hints leave 80. Wrong rounds award zero points.
Three incorrect rounds end a solo session. Ending a duel early declares no winner.

Main menu returns directly from rules/statistics/settings. During play, use Pause
and End session to see your saved results. Keep the Python server running.
The COMP9001 exam sentence and pictured clock are story context, not an exam date.

## Structure

- server.py: standard-library HTTP server and browser session controller.
- game.py: interface-independent Round and Duel rules reused from the desktop app.
- questions.py: authored question data and study tips.
- academy.py: profiles, progress, coins, badges, exports and daily selection.
- statistics.py: feedback/statistics helpers.
- expression_lab.py: guided exercises and recursive bounded expression interpreter.
- lessons.py: worked mini-lessons.
- static/index.html, style.css, app.js: responsive presentation and browser actions.
- static/assets/: optimised campus/title artwork and original synthesised audio.
- tests/: question validation, persistence, interpreter, web controller and HTTP tests.

## Validation

Run `python3 -m unittest discover -s tests -v` from this folder.
30 automated tests validate the card bank, expression solutions, file handling,
profile isolation, daily rewards, scoring, topic continuity, duel fairness, timeout,
paused clocks, hidden current answers, actual HTTP cookies/endpoints, origin checks,
path traversal rejection and export downloads.

Browser checks exercise the menu, onboarding, a scored round, feedback, summaries,
shop and Code Lab. Responsive CSS includes tablet/phone breakpoints; check on your
own phone/browser before presenting. Speaker output cannot be verified remotely.

## Credits

CodeQuest is an educational Python revision game inspired by matching/association
card games. Campus and title artwork are generated illustrations; Campus evening
is an original synthesised soundtrack. This is a student project, not an official
University of Sydney product.
