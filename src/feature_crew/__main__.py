"""Allow running the package as a module: `python -m feature_crew`."""

from feature_crew.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
