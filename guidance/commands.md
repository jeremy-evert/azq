# Command Extraction Guidance

When suggesting shell commands, always format them in a **machine-parsable block**.  
This ensures the `uaskd` tool can reliably extract and offer them for execution.

## ✅ Required Format

Wrap runnable commands between the markers:

<your command here> ::END_CMD ```
Example

Instead of writing:

git status


You must write:

::CMD
git status
::END_CMD


Or, for multiple commands:

::CMD
git add .
git commit -m "Update documentation"
git push origin main
::END_CMD

✅ Rules

One block per set of related commands.

Multiple commands are fine inside a block if they are logically run together.

Use separate blocks if they are independent choices.

Commands only.

Do not include prose, Markdown formatting, or explanations inside a ::CMD block.

Explanations belong above or below the block.

No decoration.

Do not prefix commands with !, $, or backticks.

Keep them exactly as you would type in the terminal.

Line separation.

Each command must be on its own line.

Blank lines inside the block are allowed but discouraged.

✅ Example Response Snippet

Here’s how ChatGPT should present instructions:

To check your Git status, run:

::CMD
git status
::END_CMD


Then, to commit and push changes:

::CMD
git add .
git commit -m "Refactor code"
git push origin main
::END_CMD


This ensures all commands are clearly marked, easy for the human to read, and easy for the tool to parse.
