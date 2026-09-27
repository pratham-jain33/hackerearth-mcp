"""hackerearth-mcp: give any AI assistant a code "run button".

This is a small server that sits between an AI assistant (like Claude)
and HackerEarth's computers. The assistant asks this server to run code,
this server forwards the request to HackerEarth, waits for the result,
and hands it back. Unofficial community project, not made by HackerEarth.
"""

import os
import time

import requests
from fastmcp import FastMCP


# ---------------------------------------------------------------------------
# The waiter is born. This names our server. The name is what shows up
# in the assistant's list of connected tools.
# ---------------------------------------------------------------------------
mcp = FastMCP("hackerearth-mcp")


# ---------------------------------------------------------------------------
# The menu of languages, copied from HackerEarth's own documentation.
# There is no API endpoint that lists languages, so we keep this table
# in the code. If HackerEarth adds a language, this table gets updated.
# Keys are the exact identifiers the API expects.
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = {
    "C": "C",
    "C++14": "CPP14",
    "C++17": "CPP17",
    "Clojure": "CLOJURE",
    "C#": "CSHARP",
    "Go": "GO",
    "Haskell": "HASKELL",
    "Java 8": "JAVA8",
    "Java 14": "JAVA14",
    "JavaScript (Node.js)": "JAVASCRIPT_NODE",
    "Kotlin": "KOTLIN",
    "Objective-C": "OBJECTIVEC",
    "Pascal": "PASCAL",
    "Perl": "PERL",
    "PHP": "PHP",
    "Python 2": "PYTHON",
    "Python 3": "PYTHON3",
    "Python 3.8": "PYTHON3_8",
    "R": "R",
    "Ruby": "RUBY",
    "Rust": "RUST",
    "Scala": "SCALA",
    "Swift": "SWIFT",
    "TypeScript": "TYPESCRIPT",
}

# Friendly nicknames people actually type, mapped to the exact identifiers
# above. "python" becomes PYTHON3 (modern Python), not PYTHON (Python 2).
LANGUAGE_ALIASES = {
    "python": "PYTHON3",
    "python2": "PYTHON",
    "python3": "PYTHON3",
    "python3.8": "PYTHON3_8",
    "py": "PYTHON3",
    "javascript": "JAVASCRIPT_NODE",
    "js": "JAVASCRIPT_NODE",
    "node": "JAVASCRIPT_NODE",
    "nodejs": "JAVASCRIPT_NODE",
    "typescript": "TYPESCRIPT",
    "ts": "TYPESCRIPT",
    "c": "C",
    "c++": "CPP17",
    "cpp": "CPP17",
    "cpp14": "CPP14",
    "cpp17": "CPP17",
    "c#": "CSHARP",
    "csharp": "CSHARP",
    "java": "JAVA8",
    "java8": "JAVA8",
    "java14": "JAVA14",
    "go": "GO",
    "golang": "GO",
    "rust": "RUST",
    "rs": "RUST",
    "ruby": "RUBY",
    "rb": "RUBY",
    "php": "PHP",
    "perl": "PERL",
    "r": "R",
    "kotlin": "KOTLIN",
    "kt": "KOTLIN",
    "scala": "SCALA",
    "swift": "SWIFT",
    "haskell": "HASKELL",
    "clojure": "CLOJURE",
    "pascal": "PASCAL",
    "objective-c": "OBJECTIVEC",
    "objc": "OBJECTIVEC",
}


# ---------------------------------------------------------------------------
# Addresses of HackerEarth's API, taken from their official v4 docs.
# ---------------------------------------------------------------------------
SUBMIT_URL = "https://api.hackerearth.com/v4/partner/code-evaluation/submissions/"
STATUS_URL_TEMPLATE = "https://api.hackerearth.com/v4/partner/code-evaluation/submissions/{}/"

# How long we keep asking "ready yet?" before giving up (seconds).
POLL_TIMEOUT_SECONDS = 60
# How long we wait between each "ready yet?" check (seconds).
POLL_INTERVAL_SECONDS = 2


def _get_api_key() -> str | None:
    """The key drawer: read the key from the computer's config.

    The key lives in an environment variable called HACKEREARTH_KEY.
    It is never written in this code and never shown in the chat.
    Returns None if nobody set it.
    """
    key = os.environ.get("HACKEREARTH_KEY", "").strip()
    return key or None


def _normalize_language(language: str) -> str | None:
    """Turn what the user typed into the exact identifier the API wants.

    Accepts friendly names ("python"), exact identifiers ("PYTHON3"),
    any mix of upper/lowercase. Returns None if we don't recognize it.
    """
    cleaned = language.strip().lower()
    if cleaned in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[cleaned]
    upper = language.strip().upper()
    if upper in SUPPORTED_LANGUAGES.values():
        return upper
    return None


def _check_api_error(data: dict) -> str | None:
    """Look at a response from HackerEarth and spot the known error cases.

    Returns a plain-words message if something is wrong, None if all good.
    """
    message = str(data.get("message", ""))
    if "UnregisteredClientError" in message:
        return (
            "Your HackerEarth API key was rejected (client not registered). "
            "Check that HACKEREARTH_KEY is set to the client-secret from "
            "your HackerEarth dashboard."
        )
    if "QuotaExceededError" in message:
        return (
            "HackerEarth says the free API quota for this key is used up. "
            "Wait for it to reset or contact HackerEarth support to raise it."
        )
    if "ArgumentMissingError" in message:
        return f"HackerEarth refused the request: {message}"
    return None


@mcp.tool()
def run_code(code: str, language: str) -> str:
    """Executes a snippet of code on HackerEarth's cloud servers in any of 24 languages. Use when the user wants to test code, see real output instead of predicted output, or check whether a program works. Needs the code and the language identifier, call list_languages if unsure of the exact name. Returns the program's printed output and any error messages."""
    # -- Step 0: do we even have a key? No key, no kitchen call. --
    api_key = _get_api_key()
    if not api_key:
        return (
            "HACKEREARTH_KEY is not set. Get a free client-secret by "
            "registering your app at https://www.hackerearth.com, then set "
            "it as the HACKEREARTH_KEY environment variable and try again."
        )

    # -- Step 1: translate the language name into the exact identifier. --
    lang_id = _normalize_language(language)
    if not lang_id:
        return (
            f"Unknown language '{language}'. Call list_languages to see "
            "the exact identifiers this tool accepts."
        )

    headers = {"client-secret": api_key, "Content-Type": "application/json"}

    # -- Step 2: hand the order to the kitchen. We get back a token. --
    try:
        submit_resp = requests.post(
            SUBMIT_URL,
            headers=headers,
            json={"source": code, "lang": lang_id, "time_limit": 5},
            timeout=15,
        )
    except requests.RequestException:
        return (
            "Could not reach HackerEarth's servers. Check your internet "
            "connection and try again."
        )

    try:
        submit_data = submit_resp.json()
    except ValueError:
        return (
            "HackerEarth sent back something unexpected (not valid data). "
            "Try again in a moment."
        )

    api_error = _check_api_error(submit_data)
    if api_error:
        return api_error

    he_id = submit_data.get("he_id")
    status_url = submit_data.get("status_update_url") or (
        STATUS_URL_TEMPLATE.format(he_id) if he_id else None
    )
    if not he_id or not status_url:
        return (
            "HackerEarth accepted the code but did not return a tracking "
            "token. Try again in a moment."
        )

    # -- Step 3: polling. Keep asking "ready yet?" until the food is done. --
    deadline = time.time() + POLL_TIMEOUT_SECONDS
    final_data = None
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_SECONDS)
        try:
            status_resp = requests.get(status_url, headers=headers, timeout=15)
            status_data = status_resp.json()
        except (requests.RequestException, ValueError):
            continue  # a hiccup while asking; just ask again
        api_error = _check_api_error(status_data)
        if api_error:
            return api_error
        request_code = status_data.get("request_status", {}).get("code", "")
        if request_code == "REQUEST_COMPLETED":
            final_data = status_data
            break
        if request_code == "REQUEST_FAILED":
            return (
                "HackerEarth could not process the request (internal error "
                "on their side). Try again in a moment."
            )
        # Otherwise it's still QUEUED / COMPILING: keep asking.

    if final_data is None:
        return (
            "HackerEarth took too long to finish running the code "
            f"(over {POLL_TIMEOUT_SECONDS} seconds). Try again in a moment."
        )

    # -- Step 4: read the result and translate it into plain words. --
    result = final_data.get("result", {})
    compile_status = result.get("compile_status", "")
    run_status = result.get("run_status", {}) or {}
    run_code_status = run_status.get("status", "")
    stderr = (run_status.get("stderr") or "").strip()

    if compile_status and compile_status != "OK":
        detail = f" HackerEarth says: {compile_status}" if compile_status else ""
        return f"The code did not compile.{detail}"

    if run_code_status == "AC":
        # AC = Accepted, the program ran fine. The actual printed output
        # lives at a download link; fetch it.
        output_url = run_status.get("output", "")
        output_text = ""
        if output_url:
            try:
                output_text = requests.get(output_url, timeout=15).text
            except requests.RequestException:
                output_text = ""
        answer = output_text if output_text.strip() else "(the program ran but printed nothing)"
        if stderr:
            answer += f"\n\nStderr:\n{stderr}"
        return answer

    if run_code_status == "TLE":
        return (
            "The program ran longer than the 5-second limit, so HackerEarth "
            "stopped it (time limit exceeded)."
        )
    if run_code_status == "MLE":
        return (
            "The program used more memory than allowed, so HackerEarth "
            "stopped it (memory limit exceeded)."
        )
    if run_code_status == "RE":
        detail = run_status.get("status_detail", "")
        msg = "The program crashed while running."
        if detail and detail != "NA":
            msg += f" Reason: {detail}."
        if stderr:
            msg += f"\n\nError output:\n{stderr}"
        return msg

    # Anything else we didn't expect: say so honestly, with what we got.
    return (
        "HackerEarth finished but returned a status I don't recognize "
        f"('{run_code_status}'). Try again, and if it repeats, report it."
    )


@mcp.tool()
def list_languages() -> str:
    """Returns the list of programming languages HackerEarth can execute, with the exact identifiers to pass to run_code. Use this when you are unsure which language name to use, or when the user asks what languages are available. Takes no inputs."""
    # No API key needed here: this list comes from HackerEarth's own
    # documentation table, kept in this file as SUPPORTED_LANGUAGES.
    lines = [
        "Languages HackerEarth can run, with the exact identifier to pass to run_code:"
    ]
    for name, identifier in sorted(SUPPORTED_LANGUAGES.items()):
        lines.append(f"- {name}: {identifier}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Start the server. When an assistant (like Claude Desktop) launches this
# file, it talks to the server through standard input/output. That's all
# this one line does: open for business.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
