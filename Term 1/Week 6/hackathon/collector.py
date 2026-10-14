"""Continuous live collection. Ctrl+C stops safely; rerun to resume."""
import json
import logging
import queue
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
import websocket
import config
import db
from filters import relevant
from sentiment import Analyzer, clean

log = logging.getLogger("collector")

def timestamp(value, fallback):
    try:
        result = int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
        return result if abs(result - fallback) <= 86400 * 7 else fallback
    except (ValueError, TypeError, AttributeError):
        return fallback

def apply(con, analyzer, event):
    commit = event.get("commit") or {}
    if event.get("kind") != "commit" or commit.get("collection") != "app.bsky.feed.post":
        return False
    uri = "at://%s/app.bsky.feed.post/%s" % (event["did"], commit["rkey"])
    op = commit.get("operation")
    if op == "delete":
        con.execute("DELETE FROM posts WHERE uri=?", (uri,)); con.commit()
        return False
    if op not in ("create", "update"):
        return False
    record = commit.get("record") or {}
    if not relevant(record):
        if op == "update":
            con.execute("DELETE FROM posts WHERE uri=?", (uri,)); con.commit()
        return False
    if op == "create" and con.execute("SELECT 1 FROM posts WHERE uri=?", (uri,)).fetchone():
        return False
    text = clean(record["text"])
    now = int(time.time())
    row = dict(uri=uri, text=text,
               permalink="https://bsky.app/profile/%s/post/%s" % (event["did"], commit["rkey"]),
               created_utc=timestamp(record.get("createdAt"), event["time_us"] // 1000000),
               collected_utc=now, **analyzer.analyze(text))
    db.save(con, row)
    log.info("SAVED %s | %s", row["label"], text[:100])
    return True

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    log.info("Loading Hugging Face model; first run may download files...")
    if config.DEMO:
        raise SystemExit("Collector refuses demo mode. Unset TRANSIT_DEMO for real collection.")
    analyzer = Analyzer()
    con = db.connect()
    now = int(time.time())
    run = con.execute("INSERT INTO runs(started,heartbeat) VALUES (?,?)", (now, now)).lastrowid
    con.commit()
    inbox = queue.Queue(maxsize=2000)
    stop = threading.Event()
    state = {"cursor": int(db.meta(con, "cursor") or 0), "received": 0}

    def put(item):
        while not stop.is_set():
            try:
                inbox.put(item, timeout=0.5)
                return
            except queue.Full:
                pass

    def receive():
        attempt = 0
        while not stop.is_set():
            ws = None
            try:
                params = {"wantedCollections": "app.bsky.feed.post"}
                if state["cursor"]:
                    params["cursor"] = max(0, state["cursor"] - 2000000)
                endpoint = config.ENDPOINTS[attempt % len(config.ENDPOINTS)]
                ws = websocket.create_connection(endpoint + "?" + urlencode(params), timeout=30)
                put(("notice", "Connected/reconnected; requesting replay from saved cursor where available."))
                attempt = 0
                while not stop.is_set():
                    raw = ws.recv()
                    if not raw:
                        raise ConnectionError("Stream closed")
                    event = json.loads(raw)
                    state["received"] += 1
                    put(("post", event))
            except Exception as exc:
                put(("notice", "Connection interrupted: %s. Coverage during disconnect is not guaranteed." % exc))
                attempt += 1
                stop.wait(min(60, 2 ** min(attempt, 6)))
            finally:
                if ws:
                    ws.close()

    thread = threading.Thread(target=receive, daemon=True)
    thread.start()
    saved, last_report = 0, 0
    try:
        while True:
            try:
                kind, value = inbox.get(timeout=1)
            except queue.Empty:
                kind, value = None, None
            if kind == "notice":
                log.info(value); db.event(con, value)
            elif kind == "post":
                cursor = value.get("time_us", 0)
                try:
                    saved += int(apply(con, analyzer, value))
                except Exception:
                    # Stop instead of advancing past a post that failed processing.
                    log.exception("Processing failed. Restart to replay from the last saved checkpoint.")
                    db.event(con, "Processing failed; collector stopped. Restart required.")
                    raise
                if cursor > state["cursor"]:
                    state["cursor"] = cursor
                if time.time() - last_report >= 10:
                    db.checkpoint(con, state["cursor"])
            if time.time() - last_report >= 10:
                total = con.execute("SELECT count(*) FROM posts").fetchone()[0]
                con.execute("UPDATE runs SET heartbeat=? WHERE id=?", (int(time.time()), run)); con.commit()
                log.info("Received=%d | saved this run=%d | total=%d | queue=%d", state["received"], saved, total, inbox.qsize())
                last_report = time.time()
    except KeyboardInterrupt:
        log.info("Stopping. Saved posts remain in %s", config.DB_PATH)
    finally:
        stop.set()
        db.checkpoint(con, state["cursor"])
        con.execute("UPDATE runs SET heartbeat=?,ended=? WHERE id=?", (int(time.time()), int(time.time()), run))
        con.commit(); con.close()

if __name__ == "__main__":
    main()
