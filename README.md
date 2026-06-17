LittleMiner — Instructions for All (Simple Step-by-Step Guide)

This guide explains, in plain language, how to run and use your LittleMiner app.

------------------------------------------------------------
1) What you now have
------------------------------------------------------------

You have a working app with TWO ways to run:

1. Interactive Menu Mode (default)
   - This is a forms-style command menu in the terminal.
   - Good for normal users.

2. Server Mode
   - Starts the API server directly.
   - Good for advanced use or API testing.

Your built app file is:
dist\littleminer.exe

------------------------------------------------------------
2) Before you start
------------------------------------------------------------

- Open the project folder:
  c:\Users\plumb\OneDrive\Documents\miner

- Make sure no old LittleMiner app is still running.
  If needed, close old terminal windows running LittleMiner.

------------------------------------------------------------
3) Run the app in Interactive Menu Mode (recommended)
------------------------------------------------------------

Step 1:
Open Command Prompt or PowerShell in:
c:\Users\plumb\OneDrive\Documents\miner

Step 2:
Run:
dist\littleminer.exe

Step 3:
You should see this menu:

1) Start API server
2) Register miner
3) List miners
4) Get miner by ID
5) Profitability (all)
6) Profitability stats
7) Best profitability
8) Switch recommendation by miner ID
9) Exit

Step 4:
Type a number and press Enter to choose what you want.

------------------------------------------------------------
4) What each menu option does
------------------------------------------------------------

1) Start API server
- Starts the web API on port 8000.
- Also opens docs in your browser at:
  http://127.0.0.1:8000/docs

2) Register miner
- Adds a miner profile.
- You will be asked for:
  - Wallet address
  - Hardware type (cpu/gpu/asic)
  - Hardware name (or press Enter for generic)
  - Electricity cost (default 0.10)
  - Min profit threshold (default 0.05)

3) List miners
- Shows all miners currently registered.

4) Get miner by ID
- Shows one miner using its ID.

5) Profitability (all)
- Shows profit info from all configured pools.

6) Profitability stats
- Shows summary numbers (average, min, max, etc.).

7) Best profitability
- Shows the current best opportunity.

8) Switch recommendation by miner ID
- Suggests whether a miner should switch pools based on profitability.

9) Exit
- Closes the app menu.

------------------------------------------------------------
5) Run in Server Mode (advanced)
------------------------------------------------------------

If you want only the API server (no menu), run:

dist\littleminer.exe --serve

Then visit:
http://127.0.0.1:8000/docs

------------------------------------------------------------
6) If you get “port already in use” error
------------------------------------------------------------

This means something else is already using port 8000.

Fix:
1. Close old LittleMiner windows.
2. In Command Prompt, run:
   taskkill /IM littleminer.exe /F
3. Start again.

------------------------------------------------------------
7) Rebuild the EXE (only if code changed)
------------------------------------------------------------

If you edit code and need a fresh EXE:

1. Stop all running LittleMiner processes:
   taskkill /IM littleminer.exe /F

2. Rebuild:
   python -m PyInstaller --clean --noconfirm littleminer.spec

3. New EXE will be in:
   dist\littleminer.exe

------------------------------------------------------------
8) Quick sanity check list
------------------------------------------------------------

After launching dist\littleminer.exe:
- [ ] Menu appears
- [ ] Option 1 starts server
- [ ] Browser can open /docs
- [ ] You can register a miner (option 2)
- [ ] You can list miners (option 3)

If all checked, app is working correctly.

------------------------------------------------------------
9) Important note about saved data
------------------------------------------------------------

Current miner storage is in memory while app is running.
If app restarts, miner list resets unless persistent storage is later added.

------------------------------------------------------------
10) One-line “just run it” reminder
------------------------------------------------------------

Normal use:
dist\littleminer.exe

Advanced server use:
dist\littleminer.exe --serve
