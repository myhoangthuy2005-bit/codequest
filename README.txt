CODEQUEST: CAMPUS CODEBREAKERS
COMP9001 final project - Python-powered web edition

MAIN FILE
main.py

HOW TO RUN
1. Keep all Python files together in the project folder.
2. Keep the complete static folder beside main.py, including static/assets.
3. Open a terminal in that folder.
4. Run: python3 main.py
   On Windows, run: py main.py
5. Open http://127.0.0.1:8000 in your browser.
6. Keep the terminal running. Press Ctrl+C to stop.

Python 3.10 or newer is required. No pip packages, Node, npm or Tkinter are needed.
If port 8000 is busy, run python3 main.py --port 8001 and open port 8001.
GitHub Codespaces: run python3 main.py and use Open in Browser for forwarded port 8000.

PYTHON FILES TO INCLUDE WITH THIS README.TXT ON ED
main.py
server.py
academy.py
campus_shop.py
expression_lab.py
game.py
lessons.py
questions.py
statistics.py

Tests are in tests/test_academy.py, tests/test_campus_shop.py,
tests/test_game.py and tests/test_web.py. To run the tests from the project folder:
python3 -m unittest discover -s tests -v

EXTERNAL FILES AND FULL PROJECT
Repository: https://github.com/myhoangthuy2005-bit/codequest
The static folder contains the required HTML, CSS, JavaScript, images and music.
The game will not run with the Python files alone; include or retrieve static too.

Fixed reference for the required static files (version already uploaded):
https://github.com/myhoangthuy2005-bit/codequest/tree/a82404ce423ddfd629d0dde42a1fb8b2586c753d/static

Download that fixed version using this archive link, extract it, and copy its
static folder beside the submitted Python files:
https://github.com/myhoangthuy2005-bit/codequest/archive/a82404ce423ddfd629d0dde42a1fb8b2586c753d.zip

The fixed archive's Python files predate the main.py launcher; use the Python
files submitted to Ed. Its static folder is the matching required external content.
README.md in the repository has the full feature guide and credits.

SAVING
Completed progress saves locally to ~/.codequest/profiles.json on the computer
running Python. 

AI ACKNOWLEDGEMENT

ChatGPT/Codex (OpenAI) assisted with planning, generating and revising the Python backend and web interface, debugging, testing, documentation and GitHub setup. OpenAI image generation created the campus illustrations and title artwork. The soundtrack was synthesised using AI-assisted Python code.
