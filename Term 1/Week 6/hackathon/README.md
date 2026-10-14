# Transit Safety Pulse — Bluesky edition

See START_HERE.md for exact Mac/VS Code instructions.

## Problem and prototype
Some passengers feel unsafe around public transport at night. This student
prototype collects public English-tagged posts mentioning both transport and
safety-related terms, classifies their sentiment using pretrained RoBERTa, and
shows posts and trends in Streamlit. Intended user: a transport safety analyst
reviewing themes that may warrant further investigation with surveys or incident
data. This is a proposed user, not a validated customer or partnership.
SDG 9, Target 9.1: reliable, sustainable and accessible infrastructure.

## Architecture
Bluesky Jetstream → bounded receiver queue → keyword/language filter → Hugging
Face model → SQLite → Streamlit. A receiver thread keeps reading while inference
runs. The queue applies backpressure instead of deliberately dropping events;
if the connection is lost the receiver requests replay from the processed cursor.
Checkpoints only advance after processing. Deletions remove saved posts when
received; updates are reclassified or removed if they no longer match.
The collector stops on processing failures rather than silently skipping them.
SQLite WAL allows the dashboard to read while the collector writes.

This uses the legacy /subscribe protocol that successfully connected on the
user's Mac, with a second legacy host as fallback. Endpoint formats differ from
Jetstream v2; do not change hosts to v2 without adapting the protocol.

## Model
cardiffnlp/twitter-roberta-base-sentiment-latest, an English RoBERTa model trained
on social media and fine-tuned for three-way sentiment (negative/neutral/positive).
It was not specifically trained for transport safety. License: CC BY 4.0 per the
model card. No training or fine-tuning takes place here. The first run downloads
the model and later runs normally reuse the local cache. CPU inference is chosen
for predictable compatibility. Score = p_positive − p_negative. Confidence is
not accuracy and scores are not measured safety risks.

## Data and limitations
Only newly observed live posts are collected on first run. Unknown/missing
language tags are skipped; multilingual posts tagged English may still slip
through. Keyword matching has false positives (train can mean other things) and
false negatives. Posts may refer to buses/trams as well as rail. There is no
verified station-location extraction. Volume is not guaranteed, including a
300-item target. Humans must review relevance. Social-media users are not a
representative sample of passengers; people not posting, non-English speakers,
and many older passengers are missing. Bots and repeated text can skew results.
Post URIs deduplicate identical records, not different posts with copied text.

The dashboard reports recorded running time from heartbeats, NOT guaranteed
uninterrupted coverage. Replay has a bounded retention window and is best effort.
Downtime, queue pressure, or connection failure may lose events. Connection
notices are retained. Do not claim 48 hours unless the recorded duration supports
it. Runtime across overlapping collector instances is not a coverage metric: run
only ONE collector per project folder.

## Privacy and acceptable use
No separate handles, names or profiles are stored. Mentions are replaced with
@user, but text and public post links can identify people. Data is pseudonymous,
not anonymous. Keep raw data within the coursework team, limit retention to what
the assignment needs, and remove copies when no longer required. Deleted posts
are removed only when their deletion event is received; deletion while offline
or outside replay retention may be missed. Review current source policies before
publishing or redistributing content. A CSV/database may contain personal data.

## What this must not be used for
Emergency response, automatic security decisions, identifying suspicious people,
ranking individual stations from sparse posts, or claims about what all women or
all passengers feel. Negative sentiment may concern delays rather than danger.

## Sources
- Model card: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
- Jetstream: https://github.com/bluesky-social/jetstream
- Current Jetstream docs: https://bsky.network/docs/jetstream/
- Developer guidelines: https://bsky.network/docs/developer-guidelines/

## Validation delivered
See VALIDATION.md for the checks actually performed in the build environment.
