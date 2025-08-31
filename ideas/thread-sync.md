# 🧵 Thread Sync between CLI and Web

One limitation of `azq` today is that CLI questions (`azq ask`) don’t show up in the same conversation thread as the ChatGPT web app. This means we’re effectively running two separate histories:

- **CLI log** → stored in `logs/chatlog.md` with snapshots.
- **Browser log** → stored in OpenAI’s backend, tied to the conversation ID.

## 🔮 The Dream

- Every `azq ask` runs inside a *real ChatGPT thread ID*, so I can open the web UI later and see the exact same conversation (with CLI questions included).
- Conversely, I can **import/export** threads:
  - `azq import <thread-id>` → pull a browser chat into CLI logs.
  - `azq push-thread <thread-id>` → send local CLI history into a web thread.

## 🔧 Possible Approaches

- Use the **OpenAI Threads API** (still experimental) to persist CLI asks in the same thread as the browser.
- Or create an `azq`-managed JSONL thread format, then write adapters:
  - `azq thread export` → dump logs in JSONL.
  - `azq thread import` → pull JSONL back in.
- Git-style workflow:
  - `azq thread pull <id>` = get remote web conversation.
  - `azq thread push <id>` = sync CLI log into that conversation.

## 🌱 Benefits

- Unified history across CLI + browser.
- Easier debugging: “When I asked this on CLI, what did I see in the web?”
- Future training: build a dataset of cross-platform Q&A anchored in repo state + human narrative.

---

*Open question*: Do we want CLI logs to **be the source of truth** (pushed into web), or should web remain canonical (CLI pulls in)? Maybe both, like git remote vs local.


