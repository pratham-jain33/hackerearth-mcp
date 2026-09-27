"""Local tests for hackerearth-mcp v0.1. No real API key needed."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Make sure no key leaks in from the environment for the keyless tests.
os.environ.pop("HACKEREARTH_KEY", None)

import server  # noqa: E402

EXPECTED_RUN_CODE_DESC = (
    "Executes a snippet of code on HackerEarth's cloud servers in any of 24 languages. "
    "Use when the user wants to test code, see real output instead of predicted output, "
    "or check whether a program works. Needs the code and the language identifier, "
    "call list_languages if unsure of the exact name. Returns the program's printed "
    "output and any error messages."
)
EXPECTED_LIST_DESC = (
    "Returns the list of programming languages HackerEarth can execute, with the exact "
    "identifiers to pass to run_code. Use this when you are unsure which language name "
    "to use, or when the user asks what languages are available. Takes no inputs."
)


async def main():
    # Test 1: both tools registered with verbatim descriptions.
    tool_list = await server.mcp.list_tools()
    tools = {t.name: t for t in tool_list}
    assert set(tools) == {"run_code", "list_languages"}, f"tools: {set(tools)}"
    assert tools["run_code"].description == EXPECTED_RUN_CODE_DESC, "run_code desc mismatch"
    assert tools["list_languages"].description == EXPECTED_LIST_DESC, "list_languages desc mismatch"
    # Also check the order-slip (parameters).
    params = tools["run_code"].parameters
    assert set(params["properties"]) == {"code", "language"}, f"params: {params}"
    print("PASS 1: tools registered, descriptions verbatim, parameters correct")

    # Test 2: list_languages works with no key at all.
    out = server.list_languages()
    assert "PYTHON3" in out and "JAVASCRIPT_NODE" in out
    assert out.count("\n") >= 24, "expected 24 language lines"
    print("PASS 2: list_languages works keyless, 24 languages listed")

    # Test 3: run_code with no key -> clear message, no network call.
    out = server.run_code("print(1)", "python")
    assert "HACKEREARTH_KEY is not set" in out, f"got: {out[:120]}"
    print("PASS 3: missing key fails gracefully without network")

    # Test 4: run_code with unknown language -> helpful message, no network.
    os.environ["HACKEREARTH_KEY"] = "dummy"
    out = server.run_code("print(1)", "klingon")
    assert "Unknown language" in out and "list_languages" in out, f"got: {out[:120]}"
    print("PASS 4: unknown language fails gracefully without network")

    # Test 5: language alias normalization is pure logic (no network).
    assert server._normalize_language("python") == "PYTHON3"
    assert server._normalize_language("PYTHON3") == "PYTHON3"
    assert server._normalize_language("  JavaScript ") == "JAVASCRIPT_NODE"
    assert server._normalize_language("c++") == "CPP17"
    assert server._normalize_language("klingon") is None
    print("PASS 5: language normalization works")

    print("\nAll keyless tests passed.")


asyncio.run(main())
