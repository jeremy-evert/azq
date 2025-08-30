import subprocess
import pathlib

def run_azq(*args: str) -> str:
    """Run azq with given args and return stdout as text."""
    result = subprocess.run(
        ["./bin/azq"] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True
    )
    return result.stdout.strip()

def test_ask_generates_reply(tmp_path):
    # Run azq ask
    output = run_azq("ask", "What is 2+2?")
    
    # Check that output is non-empty
    assert output, "azq gave no reply"
    
    # Be flexible: look for "4" or "four" in output
    normalized = output.lower()
    assert "4" in normalized or "four" in normalized, f"Unexpected reply: {output}"
    
    # Verify logs were updated
    log_file = pathlib.Path("logs/chatlog.md")
    text = log_file.read_text()
    assert "USER: What is 2+2?" in text
    assert "ASSISTANT:" in text

