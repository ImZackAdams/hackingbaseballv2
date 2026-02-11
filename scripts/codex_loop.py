#!/usr/bin/env python3
import argparse
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone


DEFAULT_TEST_CMD = "pytest -q"


def _run_tests(test_cmd):
    return subprocess.run(
        test_cmd,
        shell=True,
        text=True,
        capture_output=True,
    )


def _write_artifact(text, out_dir, filename):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def _build_prompt(spec_text, test_output, iteration):
    return (
        "You are Codex. Fix the codebase until tests pass.\n\n"
        "SPEC:\n"
        f"{spec_text}\n\n"
        "TEST FAILURES (latest):\n"
        f"{test_output}\n\n"
        f"Iteration: {iteration}\n"
        "Rules:\n"
        "- Only make necessary changes to make tests pass.\n"
        "- Do not add new features beyond the spec.\n"
        "- If you change code, update or add tests as needed.\n"
        "- When done, stop."
    )


def _run_codex(codex_cmd, codex_args, prompt_file, prompt_text):
    if not codex_cmd:
        return 127

    stdin_payload = None
    if codex_args:
        if "{prompt}" in codex_args:
            arg_str = codex_args.format(prompt=prompt_text)
            args = [codex_cmd] + shlex.split(arg_str)
        else:
            arg_str = codex_args.format(prompt_file=prompt_file)
            args = [codex_cmd] + shlex.split(arg_str)
    else:
        args = [codex_cmd, prompt_file]

    if codex_args and "exec" in codex_args and "-" in codex_args:
        stdin_payload = prompt_text

    result = subprocess.run(args, text=True, input=stdin_payload, capture_output=True)
    if result.returncode == 2 and "--prompt-file" in " ".join(args):
        if "unexpected argument '--prompt-file'" in (result.stderr or ""):
            fallback_args = [codex_cmd, prompt_file]
            result = subprocess.run(fallback_args)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Codex in a loop until tests pass.")
    parser.add_argument("--spec", default="specs/v1.md", help="Path to spec file.")
    parser.add_argument("--test-cmd", default=DEFAULT_TEST_CMD, help="Test command to run.")
    parser.add_argument("--max-iter", type=int, default=10, help="Maximum iterations.")
    parser.add_argument(
        "--codex-cmd",
        default=os.environ.get("CODEX_CMD", ""),
        help="Codex CLI command (or set CODEX_CMD).",
    )
    parser.add_argument(
        "--codex-args",
        default=os.environ.get("CODEX_ARGS", ""),
        help="Codex CLI args with {prompt_file} placeholder (or set CODEX_ARGS).",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Directory for logs and prompts.",
    )

    args = parser.parse_args()

    if not os.path.exists(args.spec):
        print(f"Spec not found: {args.spec}")
        return 2

    with open(args.spec, "r", encoding="utf-8") as f:
        spec_text = f.read()

    for iteration in range(1, args.max_iter + 1):
        result = _run_tests(args.test_cmd)
        if result.returncode == 0:
            print("Tests passed. Stopping.")
            return 0

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        test_out = (result.stdout or "") + "\n" + (result.stderr or "")
        test_file = _write_artifact(
            test_out,
            args.artifacts_dir,
            f"test_fail_{timestamp}_iter{iteration}.txt",
        )

        prompt = _build_prompt(spec_text, test_out, iteration)
        prompt_file = _write_artifact(
            prompt,
            args.artifacts_dir,
            f"prompt_{timestamp}_iter{iteration}.txt",
        )

        print(f"Iteration {iteration} failed. Logs: {test_file}")

        if not args.codex_cmd:
            print("CODEX_CMD not set. Set it or pass --codex-cmd to continue.")
            return 3

        code = _run_codex(args.codex_cmd, args.codex_args, prompt_file, prompt)
        if code != 0:
            print(f"Codex command failed with exit code {code}. Stopping.")
            return code

    print("Reached max iterations without passing tests.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
