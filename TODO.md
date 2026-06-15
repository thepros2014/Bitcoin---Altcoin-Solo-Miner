# Improvement TODO

- [x] Update `profit_engine/calculator.py`
  - [x] Import `Optional` from `typing`
  - [x] Add structured logging setup
  - [x] Replace `print` error handling with logger calls
  - [x] Convert `get_profitability_stats` to `async def` and await executor result
- [x] Verify `main.py` compatibility with updated async stats method
- [x] Run syntax/import validation with `py_compile`

# GUI/UX Clarification TODO

- [x] Update `entry_point.py` to clarify API-server behavior on startup
- [x] Auto-open browser to API docs (`/docs`) on startup (best effort)
- [x] Re-run runtime check for updated entry point
- [x] Rebuild executable with PyInstaller
- [x] Confirm final executable location and behavior

# CLI Forms UI TODO

- [ ] Add interactive CLI menu/forms mode to `entry_point.py`
- [ ] Add `--serve` flag to keep direct-server mode
- [ ] Implement API client actions from CLI forms (miners + profitability + recommendation)
- [ ] Validate user input (hardware type, numeric fields, ids)
- [ ] Run compile checks
- [ ] Run CLI interaction smoke test
- [ ] Rebuild final executable
- [ ] Run final executable for user viewing
