"""Command-line entry point for the feature crew."""

import argparse
import os
import sys

from feature_crew.crew import Crew


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Use a multi-agent crew (via marvincode serve) to draft a feature.",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Natural-language description of the feature to build.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name forwarded to marvincode serve (default: server default).",
    )
    parser.add_argument(
        "--server",
        default=None,
        help="Marvincode server URL (default: http://127.0.0.1:4097 or MARVINCODE_SERVER_URL).",
    )
    args = parser.parse_args(argv)

    if args.server:
        os.environ["MARVINCODE_SERVER_URL"] = args.server

    if not os.environ.get("MARVINCODE_SERVER_URL"):
        print(
            "Error: MARVINCODE_SERVER_URL is not set and no --server given.\n"
            "Start marvincode serve first, then either:\n"
            "  export MARVINCODE_SERVER_URL=http://127.0.0.1:4097\n"
            "  or pass --server http://127.0.0.1:4097",
            file=sys.stderr,
        )
        return 1

    crew = Crew(model=args.model)
    plan, code, review = crew.run(args.description)

    print("\n=== PLAN ===\n")
    print(plan.summary)
    print("\nTasks:")
    for task in plan.tasks:
        print(f"  - {task}")

    print(f"\n=== CODE ({code.filename}) ===\n")
    print(code.code)

    print("\n=== REVIEW ===\n")
    print(f"Passed: {review.passed}")
    print(review.feedback)

    return 0 if review.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
