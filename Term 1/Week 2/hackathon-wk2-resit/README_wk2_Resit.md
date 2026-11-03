# Daily Mental Health Check-in
### AI for Good — Hackathon 2: Flow State
**By Rayna Jong and Evaldas Pocius**  
**Tool:** n8n  
**SDG:** 3 — Good Health & Well-being

**YouTube link:** https://youtu.be/qEo9BuKu5Cw

## Our idea
We made a daily mental health check-in that gives someone a moment to stop and think about how they are feeling. The user receives an email reminder, fills in a short form and gets a personal message based on their answers. Their check-in is also saved in Google Sheets so they can look back at earlier entries.

We wanted the response to feel like there was a reason for filling in the form. Instead of only collecting numbers or sending a random quote, it gives the user a short affirmation, a response to what they shared and one small action they can take that day.

## The problem
Our focus is on students who are dealing with study pressure, work and other things happening in their personal lives. After a busy day, it can be easy to keep going without taking a moment to notice how you actually feel. Writing a full journal entry can also feel like too much effort when you are already tired.

For example, a student might come home after classes and work, still have a deadline coming up and feel overwhelmed. They might know they are stressed, but not know where to start. Our check-in gives them a short moment to put that into words and receive one manageable suggestion.

Student mental well-being is a relevant issue in the Netherlands. The RIVM and Trimbos 2025 monitor collected responses from over 27,000 higher-education students. It found that, despite some improvements since 2021, many students still experience stress, loneliness, emotional exhaustion or pressure to perform. It also describes how students' well-being relates to their social environment, education and circumstances such as financial worries. This gives context to the problem we chose. It does not mean that a check-in can solve all of those problems.

**Our problem question:** How can we make it easier for students to reflect on how they feel after a busy day and choose one small action that fits their situation?

## Who it is for
The intended users are students aged 18 and over in Dutch higher education who want a simple, voluntary way to check in with themselves. This includes international students dealing with things such as being away from home, alongside the usual study and work pressures.

The form and responses are in English. The user needs access to email, the internet and a browser. We chose an evening reminder at 18:00 as a moment to reflect on the day. The questions are short, and the written note is optional so the user does not have to explain everything if they do not feel like it.

The current prototype is set up for one person: the email recipient and Google Sheet are configured in the workflow. It is not a public service where different people sign up and automatically receive their own private results. The form does not collect an email address or identify different users, so it should not be shared with people expecting that kind of service.

It is not intended for children, medical diagnosis, treatment or emergency support. It is also not a way for teachers or employers to monitor someone's mental health. The person filling it in is the intended beneficiary and should be choosing to use it themselves.

| What the student needs | How we designed for it |
| --- | --- |
| A reminder to pause after a busy day | A daily email arrives at 18:00 with a direct link to the check-in. |
| A way to reflect when they have little energy | Three ratings and a concern give them a starting point. They can leave the written note blank. |
| A suggestion that fits what they shared | The model uses the scores and concern together with the note. We ask for one action that takes under five minutes. |
| A way to look back | Each submission becomes a dated row in a private Google Sheet. The owner can compare entries themselves. |

We based these design choices on the student context and our brainstorm. The recording shows a walkthrough of the prototype.

## Why this connects to SDG 3
SDG 3 focuses on good health and well-being. More specifically, target 3.4 includes promoting mental health and well-being.

Our project connects to this through a daily moment of reflection and a small supportive action. The reminder helps the user remember to pause, the form helps them describe how they feel and the response gives them something manageable to do with that information.

We are not claiming that it treats mental health conditions or has been proven to reduce stress. Its purpose is smaller: making reflection easier and offering a personal response while keeping human support important.

## What the user does
The user receives a daily email with a link to the check-in form. The form asks:

| Question | Answer |
| --- | --- |
| How is your mood today? | 1–10, from very low to very good |
| How stressed do you feel? | 1–10, from calm to very stressed |
| How much energy do you have? | 1–10, from drained to energised |
| What is affecting you most today? | A choice such as work or study, relationships, sleep, health, money, loneliness, feeling overwhelmed or nothing in particular |
| Is there anything you want to add? | An optional written note |

After submitting, they receive three short things:

1. An affirmation for the day.
2. A reflection connected to their answers.
3. One small action that takes less than five minutes.

The response is displayed on the form ending page and sent by email. The answers and AI response are saved in Google Sheets.

If mood is 3 or lower, or stress is 8 or higher, the workflow adds a fixed support message. This is a simple numerical condition. It is not a diagnosis or a reliable way of recognising every person who needs help.

## How the n8n workflow works
There are two starting points in the same workflow. The schedule sends the reminder, while submitting the form starts the response process. These happen in separate executions: the reminder does not keep running while it waits for the person to fill in the form.

### Daily reminder
**Daily Reminder 18:00 → Email Reminder**

The Schedule Trigger is set to run daily at 18:00. The email node sends the configured user a link to the form.

### Form and response
**Daily Check-in → Edit Fields → Generate Response → Build Sheet Row → Log to Google Sheet → Needs Support? → response branch → email and form result**

| Node | What it does |
| --- | --- |
| Daily Check-in | Starts when the form is submitted and collects the answers. |
| Edit Fields | Organises the date, ratings, concern and note. If the note is empty, it uses “nothing added”. |
| OpenAI Chat Model | Supplies the AI model used by Generate Response. The export uses gpt-5-mini. |
| Generate Response | Uses the answers and our prompt to generate the personal message. |
| Build Sheet Row | Combines the original answers with the AI response in the format needed for the sheet. |
| Log to Google Sheet | Adds a row containing the date, ratings, concern, note and AI response. |
| Needs Support? | Checks whether mood ≤ 3 OR stress ≥ 8. |
| Add Support Resources | Adds the fixed support message when either condition is true. |
| Pass Response Through | Keeps the AI response without the extra threshold message when both conditions are false. |
| Email Final Message | Sends the selected response to the configured email address. |
| Show Response | Shows the selected response on the form ending page. |

There are **13 nodes in total**, including the two reminder nodes and the connected AI model. The form response path contains more than the six connected nodes required by the assignment.

The sheet contains these columns: `date`, `mood`, `stress`, `energy`, `concern`, `note` and `ai_response`. Because logging happens before the support branch, `ai_response` stores the original generated message rather than the support text added afterwards. The user can review entries in the sheet; there is no automatic trend analysis or weekly summary.

### How the data moves between nodes

1. **Start with the form answers.** Edit Fields gives the five answers consistent field names and adds the date in `yyyy-MM-dd` format. The model receives the mood, stress and energy ratings, the concern and the note. The date is used for the sheet.
2. **Generate the response.** Generate Response is an n8n LLM chain connected to OpenAI Chat Model. The prompt explains what low, medium and high scores mean and asks the model to read those ratings alongside the written context. It returns the message as `text`.
3. **Keep the answers with the response.** Build Sheet Row takes the original fields from Edit Fields and puts the generated `text` into `ai_response`. Log to Google Sheet appends the resulting row, using the column headers to map the values.
4. **Choose what the user sees.** Needs Support? reads the original mood and stress ratings. If either threshold is met, Add Support Resources takes the generated message and adds a fixed paragraph pointing the user toward human support. Otherwise, Pass Response Through returns the generated message on its own. Both branches put the final message in a field called `text`, which the email and form result nodes both read.

## What AI contributes
n8n connects the whole process, and the AI generates the personal response. It receives the three scores, the selected concern and the optional note.

Our prompt asks it to consider the answers together. Low energy should lead to something gentle and manageable. A note about missing home should lead to a different reflection from a note about a study deadline, even if the scores are the same.

We ask for a warm, grounded response rather than something clinical or overly cheerful. The prompt asks for an affirmation, a short reflection and one action taking under five minutes, with the complete response under 80 words. It also tells the model not to diagnose, judge or minimise what someone shared. These instructions guide the output, but do not guarantee that every response will follow them perfectly.

There are two different uses of AI in our process. We used the n8n AI Assistant to help build and fix parts of the workflow. Separately, the connected OpenAI model runs inside the prototype whenever a form is submitted. That second use is what creates the user's response. Our brainstorm document includes the build prompt and response instructions.

Without the model, the reminder and storage could still work, but the personalised reflection would be missing. We could use fixed messages for common answers, which would be more predictable. We chose AI because the optional note gives people room to explain their situation in their own words.

## Why this solution fits
A reminder alone would tell the student to check in, but would not help them reflect. A form alone would collect answers without giving much back. A random quote would not consider whether someone is tired, stressed or having a good day.

Combining these parts makes the interaction more useful. The user gets a reminder, a short form, a response connected to their situation and an action that is meant to feel achievable. For someone who is overwhelmed, that might mean choosing one priority instead of being told to complete a whole list. This is an example of the intended experience, not a measured health outcome.

## Demo and what we tried
The screen recording shows someone completing the form with mood 9, stress 3 and energy 7, selecting Money and adding a note about having received good news. It then shows the successful execution path in n8n. This demonstrates how the form input moves through the workflow and provides a concrete example of the prototype being used.

The slides explain the workflow and show an example of the generated response. The demo is the practical evidence of the interaction; the exported JSON shows the implementation behind it.

During development, our first version stopped because the AI response was not being returned correctly. Finding and fixing this helped us understand why the information passed between nodes matters just as much as connecting them on the canvas.

## How to run it
1. Import `Daily_Mental_Health_Check-in.json` into an n8n instance that supports the node versions in the export.
2. Connect an OpenAI or compatible gateway credential to OpenAI Chat Model and confirm access to the selected model. Model usage requires available credits.
3. Connect an SMTP credential to Email Reminder and Email Final Message. Set the sender and recipient to the addresses used for your own copy.
4. Create a private Google Sheet with the seven column headers listed above. Connect your Google Sheets account, select the document and tab in Log to Google Sheet, and check the column mapping.
5. Copy the production URL from Daily Check-in and use it as the form link in Email Reminder. The production form URL is different from the workflow editor link and the temporary test URL.
6. Check the workflow timezone and daily 18:00 schedule. For use in the Netherlands, select Europe/Amsterdam.
7. Publish or activate the workflow. Keep the n8n instance running so it can send scheduled reminders and receive form submissions.
8. Open the form through its production link. Submitting the form triggers the response process automatically; it does not require clicking Execute each time.

The export contains the workflow configuration, not transferable account access. Someone rebuilding it needs their own credentials, email settings and spreadsheet. Keep credentials and real check-in data private.

## Ethical reflection
The main concern is that someone could treat a supportive AI message as advice they should rely on. The model can misunderstand a note, give an unsuitable suggestion or sound reassuring when someone needs more help. Our prompt tells it to stay non-clinical and avoid diagnosis, but a prompt does not make it medically reliable. We would use this for reflection, not to make decisions about someone's health.

The support branch is another limitation. Someone can be struggling seriously even if their scores do not meet our threshold. A person having a difficult but ordinary day might also trigger the extra message. The condition does not assess the note, contact a professional or alert a trusted person. It adds information; it does not mean that someone is monitoring the user or taking responsibility for their safety. Assessment, treatment and urgent support should remain with people qualified to provide them.

If the workflow is late or down, the reminder or response might not arrive. The current sequence also depends on Google Sheets succeeding before reaching the result nodes. A model or storage failure can therefore stop the response. We would not trust it as the only source of support. Clear failure messages, a support notice that remains visible without AI and separating essential feedback from optional storage would be useful improvements.

Privacy is important because even a few ratings and a short note can reveal sensitive information. Answers pass through n8n, the model provider, Google Sheets and email. Copies may also remain in execution histories and inboxes. The optional note means the user can share less, but the workflow still stores the note if they write one. A real deployment would need a clear explanation before submission, restricted account access, a retention and deletion process and a choice about storage. Public demonstrations should use fictional answers.

We also need to consider whether the language and suggestions fit different users. Not everyone has the same energy, money, support network or home situation. Suggestions should not assume that someone can spend money or contact family. The English-only form and fixed-recipient setup also limit who can comfortably use this version.

## Who did what
Evaldas and I brainstormed the idea together. I suggested that the response should include a personal affirmation, a reflection and one small action based on the answers. This came from another app I had used that shared daily quotes. I liked how something small could make the experience more personal instead of making the user feel like they were just filling in a form.

We both worked on the first version, but it only ran up to a certain point. The AI response was not being returned correctly. We were both learning n8n, and because Evaldas was not at school, we did not get the chance to troubleshoot it together in person. He later fixed the technical issue, completed the working version and wrote the first README. I adjusted the README and created the presentation slides. For the resubmission, I expanded the explanation of the problem, users, SDG connection, implementation and ethical choices.

## How did it go? What would I do differently?

I liked that we ended up with something a person could actually interact with. My idea started with a daily quote, but adding the reflection and small action gave the check-in more purpose. The hardest part was getting the generated text from the AI node to the place where the user would see it.

If I did this again, I would follow one fictional submission through the workflow while building it. I would check which fields each node returns and record the form, inbox and spreadsheet for the same submission. That would make it easier for me to spot where a result gets lost and easier for someone else to follow the demo.

## What I learned
The most important thing I learned is how much the different parts depend on each other. A workflow can look connected but still fail if the next node receives the wrong field or cannot find the AI response. Debugging means looking at what each node actually receives and sends.

I also learned that the project needs to make sense without us standing next to it. Showing the tool is only one part. We also need to explain who it helps, why we chose this approach and where its limits are.

## Sources
- [RIVM and Trimbos — Monitor Mentale gezondheid en Middelengebruik Studenten hbo en wo 2025](https://www.rivm.nl/publicaties/monitor-mentale-gezondheid-en-middelengebruik-studenten-hbo-en-wo-2025). Used to support the student well-being context in this README.
- [United Nations — 2030 Agenda, target 3.4](https://sdgs.un.org/2030agenda). Explains the connection to promoting mental health and well-being.
- [n8n](https://n8n.io/). The required platform used to build the automation.
