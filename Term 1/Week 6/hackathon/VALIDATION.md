# Validation — 14 October 2026

Passed:
- Python syntax compilation for all files.
- Offline tests: English/topic filtering and exclusions; deduplication; saving,
  updates, removal after an irrelevant update, deletion, cursor persistence and
  timestamp fallback. Predictions replaced with a fake model for these tests.
- Streamlit AppTest: empty dashboard, populated dashboard with five temporary
  synthetic fixture rows, refresh, charts/table/CSV controls, no app exceptions.
- Live WebSocket smoke test: connected to the primary Jetstream endpoint and received one message.
- Evaluation sample/label/score workflow with 50 temporary synthetic fixture rows;
  confirmed blind export omits predictions and metrics/output files are written.
  Those fixtures and metrics are not included as real assignment results.

Not verified end-to-end here:
- Real Hugging Face download and inference in this build environment.
- Continuous live collection on the user's Mac, 48-hour reliability or yield.
- Exact package resolution on macOS Python 3.9.6.

The user previously demonstrated a successful live connection to the primary
legacy Jetstream endpoint and successful inference with this model on her Mac.
That is useful setup evidence, not an end-to-end test of this new project.
