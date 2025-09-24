# Scheduling examples

## Linux/macOS (crontab)

Run the odds poller every 5 minutes and compute edges on the hour:

```cron
# m h  dom mon dow command
*/5 * * * * /usr/bin/env bash -lc 'cd /path/to/repo && source .venv/bin/activate && python jobs/poll_odds.py'
0 * * * * /usr/bin/env bash -lc 'cd /path/to/repo && source .venv/bin/activate && python jobs/compute_edges.py'
```

## systemd timer

```ini
# /etc/systemd/system/odds-poller.service
[Unit]
Description=The Odds API poller

[Service]
Type=simple
WorkingDirectory=/path/to/repo
ExecStart=/path/to/repo/.venv/bin/python jobs/poll_odds.py --interval 300
```

## Windows Task Scheduler

1. Open Task Scheduler and create a new basic task.
2. Trigger: Daily, repeat every 5 minutes for a duration of 1 day.
3. Action: Start a program.
4. Program/script: `C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe`
5. Add arguments: `-NoProfile -Command "cd C:/path/to/repo; .venv/Scripts/Activate.ps1; python jobs/poll_odds.py"`

## GitHub Actions (scheduled)

Use the provided workflow in `.github/workflows/poll_odds.yml` and add your API key as
an encrypted repository secret named `ODDS_API_KEY`.
