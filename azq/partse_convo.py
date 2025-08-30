#!/usr/bin/env python3
import os, sys, json

def parse_convo(json_file, outdir):
    with open(json_file) as f:
        data = json.load(f)

    os.makedirs(outdir, exist_ok=True)

    count = 1
    for msg in data.get("messages", []):
        role = msg.get("role", "unknown")
        content = msg.get("content", "").strip()
        fname = f"{outdir}/{count:03d}-{role}.txt"
        with open(fname, "w") as out:
            out.write(content + "\n")
        count += 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: parse_convo.py raw.json outdir")
        sys.exit(1)
    parse_convo(sys.argv[1], sys.argv[2])

