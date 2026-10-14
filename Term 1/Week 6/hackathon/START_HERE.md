# Start here — Mac / VS Code

This is a complete replacement project. Keep your previous folder as a backup.
Unzip this folder, then VS Code → File → Open Folder → transit_safety_pulse_bluesky.
Do not put files inside venv. No Reddit keys, Hugging Face key or .env is needed.

## First terminal: setup (one command at a time)

Terminal → New Terminal, then:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python selftest.py
```

The self-test should finish with OK. It uses fake predictions and never fabricates
real collection results. Python 3.9+ is supported by the chosen package bounds.

## Start REAL collection in that terminal

```bash
caffeinate -i python collector.py
```

The model downloads on first use if not already cached. After loading, look for
Connected/reconnected and Received=... counts. SAVED means a relevant post was
analyzed and stored. No SAVED lines yet can simply mean no matching posts.
Keep this terminal open, your Mac plugged in, lid OPEN and internet connected.
The screen can turn off. Closing the lid can still suspend collection.

## Second terminal: open the browser dashboard

Click + in the terminal panel, then:

```bash
source venv/bin/activate
python -m streamlit run dashboard.py
```

If asked Email, press Enter with the field empty. Open the Local URL shown
(usually http://localhost:8501) in Chrome/Safari if no tab opens automatically.
Click Refresh results to read newly saved posts. You can view the dashboard
while collection continues. Nothing needs deploying for a laptop presentation.

## Stop / resume

Press Control+C in the collector terminal to stop. Keep bluesky_safety.db: it
contains the actual results and resume cursor. Run the same collector command to
resume. Replay is best effort; disconnects may leave gaps. Do not delete the folder
or database, recreate it, or replace files while collection is running.

48 hours means actual recorded runtime, not time since the ZIP was downloaded.
The script runs until stopped; it does not automatically stop after 48 hours.
The dashboard records runtime and connection notices, not guaranteed coverage.

## Optional: preview charts immediately using separate SYNTHETIC data

In another activated terminal:

```bash
python demo.py
TRANSIT_DEMO=1 python -m streamlit run dashboard.py --server.port 8502
```

Open http://localhost:8502. The red DEMO banner must remain visible. The demo uses
a separate database; never present these charts as real collected findings.
Close it with Control+C. Your normal dashboard/collector remain in real mode.

## Sharing with your teammate

Send this project ZIP. They run the same setup. For sharing your actual results,
stop the collector first, then include bluesky_safety.db and the code folder
(or export a CSV from the dashboard). Do not include venv or model downloads.
The database is local to each computer: yours and your teammate's do not sync.
Only one teammate needs to collect; both can open a copy of the saved database.

## Evaluation after at least 50 real posts

```bash
python evaluate.py sample
```

Open evaluation/labels.csv in a spreadsheet. Read each text without looking at
model predictions, and fill human_label with negative, neutral or positive.
Save as CSV, then:

```bash
python evaluate.py score
```

Results go to evaluation/metrics.json and evaluation/test_table.csv. Choose real
misclassified examples for the reflection. If fewer than 50 are collected, report
that honestly; do not substitute synthetic data.
