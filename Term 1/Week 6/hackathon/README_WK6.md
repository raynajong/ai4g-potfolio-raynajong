# Term 1 - Week 6: Language Models

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

**What did I hand in?**
_List the files, or link to them. Notebook exports, screenshots, scripts._

**What did I find difficult, and how did I solve it?**

### Checklist
- [ ] My workshop / homework files are in `homework/`
- [ ] Everything runs without errors, or I explained what does not and why

---


## 2. Hackathon prototype -> [`hackathon/`](hackathon/)

> Your tool and your SDG for this hackathon are announced at the **start of Friday's class**.
> Write them down here once you know them.

**Project title:**
Transit Safety Pulse — Live Public Transport Safety Sentiment

**My pair partner:**
Ana Talg Wolf

**Tool we had to use:**
A pretrained sentiment transformer from Hugging Face, loaded and run locally through Python's transformers library. We used cardiffnlp/twitter-roberta-base-sentiment-latest. Claude and ChatGPT helped with coding and setup; they are not the sentiment engine in the running prototype.

**SDG we had to address:**
SDG 9 — Industry, Innovation and Infrastructure, specifically Target 9.1 on reliable, sustainable and resilient infrastructure with equitable access. Our prototype explores how public feedback could help identify concerns about public transport infrastructure. It does not itself establish that transport became safer.

**What problem does it solve, and for whom?**
Passengers can feel unsafe around stations and other public transport settings, including concerns about darkness, harassment and security. These experiences can affect confidence in using transport. The UK Department for Transport's National Travel Attitudes Study Wave 8, based on responses gathered in England in March–April 2023, reports gender differences in safety concerns. For example, 77% of female respondents considered how light or dark it might be when travelling, compared with 50% of male respondents. This provides context from England, not evidence about Dutch stations or our Bluesky sample.

Our intended dashboard user is a public transport safety analyst at a rail operator reviewing online feedback. This is a proposed user role, not a tested partnership. Their task is to notice themes that may deserve further investigation. For example, after seeing a negative period, the analyst reads the underlying posts and decides whether the concerns merit follow-up through surveys, customer feedback or incident reports. Our prototype does not identify or verify a station automatically, so any local follow-up requires checking the text and location first.

Passengers are potential indirect beneficiaries. The dashboard is not an emergency tool for individual passengers, an official reporting channel, or a verified guide to safe stations. It currently monitors English-tagged discussion across Bluesky, without restricting the stream to women, nighttime, the Netherlands or a particular operator. Its transport filters also include metro, tram and bus-stop terms, so the implemented scope is broader than train stations alone.

**What did you build?**
We built a Python pipeline that receives new public Bluesky posts continuously, filters for English-language discussion mentioning transport and safety, predicts sentiment with a Hugging Face transformer, and saves the results in SQLite. A Streamlit browser dashboard displays sentiment over time, post counts, the negative share, and the posts behind the results. Users can search or filter saved posts, refresh results and export a CSV.

**How the project works: input to output**
1. Input — Bluesky Jetstream. The collector connects to a public live WebSocket stream. Posts arrive automatically as they are published; the user does not need to enter text. No Reddit credentials are used in this version.
2. Language and relevance filtering. Posts must carry an English language tag and match both a transport term and a safety-related term. config.py contains the words; filters.py applies the checks and exclusions. This is an approximate relevance filter, not proof that each post describes a real safety incident.
3. Preprocessing. The code replaces text mentions with @user, normalizes whitespace, and replaces URLs with a placeholder before model inference. Model input is truncated to fit its token limit.
4. Hugging Face inference. sentiment.py downloads/loads the pretrained model once, then runs it locally on each matching post. Its three labels are negative, neutral and positive. It returns a probability for each label and selects the highest-probability label.
5. Storage. db.py writes text, timestamps, permalink, label, probabilities and sentiment score to bluesky_safety.db. The score is positive probability minus negative probability, ranging from −1 to +1. A stable Bluesky post URI is the primary key, preventing duplicate stored records. Observed updates are processed and observed deletions remove stored posts.
6. Continuous operation. A receiver thread and bounded queue separate network reception from model inference. The code retries dropped connections and requests replay from the processed cursor where available. Replay and uninterrupted coverage are not guaranteed. A processing failure stops collection so the user can investigate instead of silently advancing past it.
7. Output — Streamlit. dashboard.py reads the database and groups posts by hour or day. It shows the average score, post volume and underlying text with original links. Its Refresh results button rereads the saved data; collecting new posts does not depend on pressing this button.
   
Without the Hugging Face model, the prototype could still receive text, but it could not produce the transformer-based predictions required for its sentiment charts. The model therefore performs a necessary step, rather than being mentioned only in the presentation.

**Model choice and model card summary**
- Model: cardiffnlp/twitter-roberta-base-sentiment-latest.
- Training background: RoBERTa trained on approximately 124 million tweets from January 2018 to December 2021, then fine-tuned for sentiment with TweetEval.
- Language: English.
- Labels: Negative, neutral and positive.
- Licence: CC BY 4.0, as listed on the model card.
- Reason for selection: Its social-media background is relevant to short, informal posts, and its labels fit our dashboard.
- Limitations: It was not specifically trained on Bluesky transport-safety discussion. Sarcasm, negation, slang and mixed messages may cause mistakes. We must measure performance on our own sample; social-media training does not guarantee suitability.
- Training in this project: None. We use an existing pretrained model; we do not train or fine-tune it.

**Why use this approach?**
A continuous pipeline can organize more posts than our intended user could conveniently read one by one. Aggregation helps the analyst choose periods to inspect, while the underlying posts preserve context. Keyword counts alone identify mentions but do not distinguish their tone. However, the added value of this particular transformer compared with the simpler VADER baseline must be justified using our evaluation. We do not assume the transformer is better before measuring it.
This tool can support exploratory review, not establish causes, measure actual danger, or justify security decisions by itself. Human checking and other evidence are necessary.

**Link to the live thing (if any):**
http://localhost:8501/

**How do I run it?**
Open the project folder in VS Code, then Terminal → New Terminal. On Mac, run one command at a time:
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python selftest.py
caffeinate -i python collector.py
In a second terminal in the same folder:
source venv/bin/activate
python -m streamlit run dashboard.py
Leave Streamlit's optional email field blank and press Enter. Open the Local URL shown. Keep the collector terminal open, internet connected, the Mac plugged in and its lid open. Press Control+C in the collector terminal to stop. Saved results remain in bluesky_safety.db; restarting the collector attempts to resume from the saved cursor. Run only one collector per project folder.
Python 3.9+ is targeted by the package constraints. On a fresh installation the model must download first. Installation and runtime errors should be documented rather than treated as a successful collection run.

What each file does
File	              Purpose
collector.py	      Receives live events, coordinates analysis, reconnects and logs progress
config.py	          Model name, database path, endpoints and topic filters
filters.py	        Language and keyword relevance checks
sentiment.py	      Text cleaning, model loading and predictions
db.py	              Database tables, saving and progress bookkeeping
dashboard.py	      Browser interface, charts, saved post table and CSV download
evaluate.py	        Blind sample export and comparison with human labels and VADER
selftest.py         Offline code checks using fake predictions
demo.py	            Optional synthetic preview using a separate database
requirements.txt	  Python dependencies
START_HERE.md	      Detailed setup and sharing instructions
VALIDATION.md	      Checks performed during project preparation and their limits

**Who did what?**
Ana developed the initial idea, brainstormed the problem and researched the concept. She shared a document explaining the proposed solution, which we discussed and agreed on.

I used Claude and ChatGPT to generate much of the Python code and receive step-by-step setup guidance. I set up the project in VS Code, ran the supplied self-tests, and tested the Hugging Face model and Bluesky connection. The initial Reddit approach was blocked during API app creation, so the project was adapted to Bluesky. I then started the updated collector and opened the dashboard. So it did get delayed a bit.

I shared the project code with Ana, who is preparing the presentation slides. The coding assistance was substantial; our responsibility is to understand the final pipeline, review its limitations, and report only results supported by our actual collection and evaluation. 


**Ethical reflection - what are the risks of your tool? Who could it harm?**
Our sample reflects English-tagged Bluesky posts, not all passengers. Non-posters and people writing in other languages are excluded; people without language tags are also skipped. This could cause an analyst to overlook concerns outside the sample. We state this limitation and do not describe the chart as representative of women, Dutch passengers or a particular station. Keyword false positives and model mistakes could exaggerate a concern or hide one. We show post counts and underlying text, require human review, include a dashboard warning and plan a manual evaluation against VADER. These safeguards reduce risk but do not establish reliability. Bots and repeated text from different accounts may distort trends: our URI-based deduplication removes repeated records, not coordinated campaigns, so bot and content-level checks remain future work.
We do not store separate usernames or profile fields, and replace mentions in text with @user. However, public text and original post links can still identify authors, so the data is not anonymous. Observed deletion events remove stored posts, but deletions missed while offline may remain. Limit raw-data sharing to what the coursework needs, check source terms before redistribution, and keep data only as long as necessary. Public-source access does not mean unrestricted permission to publish personal text. The prototype must not be used for emergency response, identifying suspicious individuals, automatic security decisions or station rankings from sparse posts.

### Checklist
- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [ ] The prototype actually runs, and I wrote down how to run it
- [ ] Ethical reflection written above

**Development issue affecting collection:** We initially attempted Reddit, but app creation was blocked by the access/approval process. After testing an alternative connection, we changed the source to Bluesky and restarted setup with the new project. This delayed real collection. We will report the actual duration and dataset size and explain any unmet requirement. 

---

## 3. Presentation -> [`presentation/`](presentation/)

*Only fill this in for the week your group was selected to present. You need at least **one** of these across the whole term.*

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

---

## 4. Reflection

**What is the most important thing I learned this week?**
I learned that collecting data, analyzing it and displaying it are different parts of one system. Bluesky provides the posts, the Hugging Face model predicts sentiment, SQLite saves the results and Streamlit displays them. I also learned that code passing tests does not automatically mean the model is accurate on real posts. The Reddit access problem showed me why data-source access needs testing early, before relying on a long collection period.

**Where does this connect to "AI for Good"?**
The project explores how AI could help people review concerns about public transport infrastructure, supporting SDG 9. Its value depends on responsible interpretation: the tool should help an analyst decide what to investigate, while acknowledging missing voices, privacy risks and prediction errors. A chart should support careful human judgment rather than create false confidence about safety.
