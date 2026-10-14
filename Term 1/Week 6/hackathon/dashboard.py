import time
import pandas as pd
import streamlit as st
import config
import db

st.set_page_config(page_title="Transit Safety Pulse", page_icon="🚉", layout="wide")
st.title("🚉 Transit Safety Pulse")
if config.DEMO:
    st.error("DEMO — SYNTHETIC EXAMPLES ONLY. These are not collected posts or evaluation results.")
st.caption("Live Bluesky posts about public transport safety • English • Hugging Face sentiment analysis")
st.warning("Post sentiment is not a measure of actual safety. Keyword matches can be off-topic. This sample does not represent all passengers. Do not use it for emergency response or station safety rankings.")
if st.button("Refresh results"):
    st.rerun()
con = db.connect()
posts = pd.read_sql_query("SELECT * FROM posts ORDER BY created_utc DESC", con)
runs = pd.read_sql_query("SELECT * FROM runs", con)
events = pd.read_sql_query("SELECT * FROM events ORDER BY time DESC LIMIT 100", con)
con.close()
if not runs.empty:
    start = int(runs.started.min())
    end = int(runs.heartbeat.max())
    active = (runs.heartbeat.fillna(runs.started) - runs.started).clip(lower=0).sum() / 3600
    st.info("Recorded running time: %.2f hours across %d run(s). This is not verified uninterrupted stream coverage." % (active, len(runs)))
    st.caption("First start: %s • Last heartbeat: %s" % (pd.to_datetime(start, unit="s", utc=True), pd.to_datetime(end, unit="s", utc=True)))
    if time.time() - end > 90:
        st.warning("The collector heartbeat is older than 90 seconds. It may be stopped or loading/processing slowly.")
if posts.empty:
    st.info("No matching posts saved yet. In another terminal run: caffeinate -i python collector.py. Narrow topics can take time; check the received count in the terminal.")
else:
    posts["created"] = pd.to_datetime(posts.created_utc, unit="s", utc=True)
    labels = st.sidebar.multiselect("Sentiment", ["negative", "neutral", "positive"], default=["negative", "neutral", "positive"])
    needle = st.sidebar.text_input("Search saved text")
    freq = st.sidebar.selectbox("Group time by", ["Hour", "Day"])
    minimum = st.sidebar.slider("Minimum posts per chart point", 1, 20, 1)
    data = posts[posts.label.isin(labels)].copy()
    if needle:
        data = data[data.text.str.contains(needle, case=False, regex=False)]
    a,b,c = st.columns(3)
    a.metric("Matching posts", len(data))
    b.metric("Average sentiment", "%.2f" % data.score.mean() if len(data) else "—")
    c.metric("Negative share", "%.0f%%" % (100 * data.label.eq("negative").mean()) if len(data) else "—")
    st.caption("Sentiment score = positive probability minus negative probability (−1 to +1). Model probabilities are not measured accuracy.")
    if not data.empty:
        data["period"] = data.created.dt.floor("h" if freq == "Hour" else "D")
        agg = data.groupby("period").agg(posts=("uri", "count"), sentiment=("score", "mean"))
        full = pd.date_range(agg.index.min(), agg.index.max(), freq="h" if freq == "Hour" else "D")
        agg = agg.reindex(full)
        agg["posts"] = agg.posts.fillna(0)
        agg.loc[agg.posts < minimum, "sentiment"] = float("nan")
        left,right = st.columns(2)
        with left:
            st.subheader("Sentiment over time")
            st.line_chart(agg[["sentiment"]])
        with right:
            st.subheader("Posts per period")
            st.bar_chart(agg[["posts"]])
        st.subheader("Read the posts behind the results")
        st.dataframe(data[["created", "label", "score", "text", "permalink"]], hide_index=True,
                     column_config={"permalink": st.column_config.LinkColumn("Original post")}, use_container_width=True)
    st.download_button("Download filtered results (CSV)", data.to_csv(index=False).encode("utf-8"), "transit_results.csv", "text/csv")
with st.expander("Connection and processing log"):
    st.dataframe(events, use_container_width=True)
st.caption("Refresh manually to read the latest saved results. You can reopen this dashboard after stopping the collector.")
