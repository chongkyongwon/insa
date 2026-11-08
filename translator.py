#!/usr/bin/env python3
"""Korean <-> Tagalog interpreter.

Korean input  -> Tagalog + English
Tagalog input -> Korean + English

Usage:
    export ANTHROPIC_API_KEY=...
    python3 translator.py            # interactive: type a line, get a translation
    python3 translator.py "매워 아니야?"   # one-shot
    echo "Ang anghang!" | python3 translator.py

Only the Python standard library is needed.
"""
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("TRANSLATOR_MODEL", "claude-sonnet-5-5")

SYSTEM = """You are a live interpreter between Korean, Tagalog (Filipino) and English.
Detect the language of the user's text.
- If it is Korean: output the Tagalog translation, then the English translation.
- If it is Tagalog or Taglish: output the Korean translation, then the English translation.
- If it is English: output Korean, then Tagalog.
Output format, nothing else:
한국어: ...
Tagalog: ...
English: ...
(Only include the two target languages, not the source language.)
The text may be informal speech or a rough speech-to-text transcript. Translate
the meaning naturally, keep the tone, and if a word is unclear or looks like a
transcription error, give your best guess and add a short line starting with
"메모:" saying what is uncertain. Never refuse to translate ordinary speech;
render slang and profanity faithfully but mildly."""


def translate(text: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ANTHROPIC_API_KEY 환경변수를 설정하세요.")
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": text}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        return f"[오류 {e.code}] {e.read().decode(errors='replace')}"
    except urllib.error.URLError as e:
        return f"[네트워크 오류] {e.reason}"
    return "".join(b.get("text", "") for b in data.get("content", []))


def main() -> None:
    if len(sys.argv) > 1:
        print(translate(" ".join(sys.argv[1:])))
    elif not sys.stdin.isatty():
        print(translate(sys.stdin.read()))
    else:
        print("한국어 ⇄ Tagalog 통역기 (종료: Ctrl+D)")
        while True:
            try:
                line = input("\n> ").strip()
            except EOFError:
                break
            if line:
                print(translate(line))


if __name__ == "__main__":
    main()
