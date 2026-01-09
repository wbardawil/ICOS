import subprocess
import json
import sys
import os

def main():
    # Use the global n8n-mcp path we found
    cmd = ["npx", "-y", "n8n-mcp"]
    
    # Pass along environment variables
    env = os.environ.copy()
    
    # Start the n8n-mcp process
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        env=env,
        universal_newlines=True,
        bufsize=1,
        shell=True
    )

    # Thread to pipe stdin directly to the process
    import threading
    def pipe_stdin():
        for line in sys.stdin:
            if not line: break
            process.stdin.write(line)
            process.stdin.flush()
    
    stdin_thread = threading.Thread(target=pipe_stdin, daemon=True)
    stdin_thread.start()

    # Read stdout and filter for JSON
    try:
        for line in process.stdout:
            if not line: break
            line = line.strip()
            if not line: continue
            
            try:
                # Try to parse as JSON
                json.loads(line)
                # If it's JSON, print it to real stdout
                print(line, flush=True)
            except json.JSONDecodeError:
                # If it's not JSON (noise), print it to stderr so it doesn't break MCP
                sys.stderr.write(f"[RECOVERED NOISE]: {line}\n")
                sys.stderr.flush()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    main()
