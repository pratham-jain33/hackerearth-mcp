# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

Only the latest minor release line receives security fixes.

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, email **hello@prathamjain.com** with:

- a description of the vulnerability,
- steps to reproduce it,
- the version you tested against.

You can expect an acknowledgement within 7 days. If the issue is confirmed,
a fix will be released and credited in the release notes (unless you ask to
stay anonymous).

## Scope notes

- This server executes code on **HackerEarth's** sandboxed servers using **your**
  HackerEarth API key. Never commit your key; pass it via the `HACKEREARTH_KEY`
  environment variable.
- Nothing untrusted is executed on your local machine by this server.
