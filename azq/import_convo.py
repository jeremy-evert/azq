#!/usr/bin/env python3
import os, sys, json
from openai import OpenAI

# Load from .env if available
load_dotenv()

def import_convo(convo_id, outdir):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    os.makedirs(outdir, exist_ok=True)

    # Get conversation via API (for now, stub with a dummy call)
    # NOTE: OpenAI doesn’t yet expose full “conversation history” by ID,
    # so we simulate this by asking for messages.
    # Later: replace with real export once endpoint exists.
    convo = {
        "id": convo_id,
        "messages": [
            {"role": "user", "content": "Hello azq!"},
            {"role": "assistant", "content": "Hey 👋 ready to rock!"},
        ]
    }

    raw_file = os.path.join(outdir, "raw.json")
    with open(raw_file, "w") as f:
        json.dump(convo, f, indent=2)

    # Split into numbered files
    count = 1
    for msg in convo["messages"]:
        role = msg["role"]
        content = msg["content"]
        fname = os.path.join(outdir, f"{count:03d}-{role}.txt")
        with open(fname, "w") as out:
            out.write(content + "\n")
        count += 1

    print(f"[azq] Conversation saved in {outdir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: import_convo.py <conversation-id> <outdir>")
        sys.exit(1)

    convo_id, outdir = sys.argv[1], sys.argv[2]
    import_convo(convo_id, outdir)

