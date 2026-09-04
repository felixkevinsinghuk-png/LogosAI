# Ngrok & Server Management Guide

This guide explains how to start, stop, and troubleshoot the RhemaLight AI server and `ngrok` tunnel, especially when encountering the "Address already in use" error.

## 1. Starting the System

### Step A: Start the RhemaLight AI Server
Always start the backend server first.
```bash
# Activate the environment
conda activate logosai

# Run the main application
python3 main.py
```

### Step B: Start Ngrok
Open a **new terminal tab** and run:
```bash
ngrok http 8000
```
*Note: Copy the `https://...ngrok-free.app` URL provided in the terminal.*

---

## 2. Terminating the System

### Stop RhemaLight AI
Press `Ctrl + C` in the terminal where `main.py` is running.

### Stop Ngrok
Press `Ctrl + C` in the terminal where `ngrok` is running.

---

## 3. Troubleshooting: "Address already in use"

If you get an error saying `[Errno 48] error while attempting to bind on address ('0.0.0.0', 8000)`, it means a previous server instance is still "leaking" on that port.

### How to Fix:
1. **Find the Process ID (PID):**
   ```bash
   lsof -i :8000
   ```
   *Look for the number in the `PID` column.*

2. **Kill the Process:**
   Replace `<PID>` with the actual number you found:
   ```bash
   kill -9 <PID>
   ```

3. **Restart:**
   Now you can run `python3 main.py` again without the error.

---

## 4. Useful Commands Summary

| Task | Command |
| :--- | :--- |
| **Check Port 8000** | `lsof -i :8000` |
| **Check Ngrok Status** | Go to [http://localhost:4040](http://localhost:4040) in your browser |
| **List Tunnels via CLI** | `curl http://localhost:4040/api/tunnels` |
| **Force Close Port** | `npx kill-port 8000` (Alternative to kill -9) |
