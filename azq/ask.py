#!/usr/bin/env python
import pathlib, datetime, subprocess, shutil

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from pathlib import Path
from azq.openai_client import client
from azq.context_snapshot import get_repo_context
from azq.token_counter import count_tokens

def load_guidance():
    texts = []
    for file in Path("guidance").glob("*.md"):
        texts.append(file.read_text())
    return "\n\n".join(texts)

def run_uaskd(answer: str):
    uaskd = shutil.which("uaskd") or "./bin/uaskd"
    try:
        # Write answer to a temp file for uaskd to read
        import tempfile
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write(answer)
            tmp.flush()
            tmp_path = tmp.name

        # Launch uaskd with terminal stdin/stdout, passing file path
        subprocess.run([uaskd, tmp_path], check=False)
    except Exception as e:
        print(f"[azq] (note) uaskd not run: {e}")

def main():
    exec_mode, question = sys.argv[1], sys.argv[2]

    context = get_repo_context()
    guidance = load_guidance()

    # Save snapshot
    snap_dir = Path("logs/snapshots")
    snap_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    snap_file = snap_dir / f"snapshot-{ts}.txt"
    snap_file.write_text(context)

    # Token count
    total_input = f"{question}\n\n{context}"
    token_count = count_tokens(total_input, "gpt-4o-mini")
    print(f"[azq] Input length: ~{token_count} tokens")

    # Ask ChatGPT
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are azq, a CLI mentor. Always follow best practices.\n\n" + guidance},
            {"role": "user", "content": total_input}
        ]
    )
    answer = resp.choices[0].message.content
    #print(answer)
    print("\n--- ChatGPT Response ---\n")
    print(answer)
    print("\n--- End Response ---\n")


    # Decide on execution
    if exec_mode == "true":
        run_uaskd(answer)
    else:
        try:
            choice = input("[azq] Parse reply for commands and walk through them? [y/N]: ").strip().lower()
            if choice == "y":
                run_uaskd(answer)
            else:
                print("[azq] Skipping command execution.")
        except EOFError:
            print("[azq] Skipping command execution (no stdin).")

    # Log
    with open("logs/chatlog.md", "a") as f:
        f.write(f"USER: {question}\n")
        f.write(f"ASSISTANT: {answer.replace(chr(10), ' ')}\n")
        f.write(f"[snapshot: {snap_file}]\n")

if __name__ == "__main__":
    main()

