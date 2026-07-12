# Contributing

Contributions are welcome for macOS compatibility, safer installation,
documentation, tests, and translation tooling.

Do not commit or attach:

- Civilization V text, assets, depots, or generated patches
- fonts or generated font atlases
- Steam account information or credentials
- backups, caches, crash reports, or private local paths

Before opening a pull request, run:

```sh
python -m unittest discover -s tests
python scripts/release_audit.py
```

By contributing, you agree that your original contribution is licensed under
the repository's MIT License and that you have the right to submit it.
