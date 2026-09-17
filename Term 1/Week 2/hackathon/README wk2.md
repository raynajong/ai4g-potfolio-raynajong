# Term 1 - Week 2: Loops & Functions

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
Daily Mental Health Check-in
AI for Good - Hackathon 2: Flow State

**My pair partner:**
Evaldas Pocius

**Tool we had to use:**
n8n

**SDG we had to address:**
SDG: 3 - Good Health & Well-being

**What problem does it solve, and for whom?**
Many people do not regularly stop and think about how they are actually feeling. By the time they notice that they are stressed, overwhelmed or low on energy, it can already feel more difficult to deal with.

This tool is made for anyone who wants a simple, low-effort way to check in with their mental state every day. It is not a clinical or diagnostic tool, but a small daily reminder to become more aware of how you are feeling and take one manageable action.

**What did you build?**
We built an automated daily mental health check-in using n8n. Every day at 18:00, the user receives an email with a link to a short form. The form asks them to rate their mood, stress and energy from 1–10, choose their main concern and optionally write a short note about what is on their mind.

After the form is submitted, AI uses the answers to create a personal response containing an affirmation, a short reflection and one small, low-effort action for the day. The message is shown on-screen and also emailed to the user.

If the user reports a very low mood or very high stress level, support information such as 113 Zelfmoordpreventie and contacting their GP is added automatically. The answers are also saved in Google Sheets so the user can view their check-ins over time.

**Link to the live thing (if any):**
[_Deployed URL, workflow export, video demo - whatever proves it works._
](https://pancakemous.app.n8n.cloud/workflow/82bnOm3iVzrjYiQ3)

**How do I run it?**
1. Import Daily Mental Health Check-in.json into your own n8n instance (Cloud or self-hosted).
2. Set up credentials:
    - An OpenAI (or other supported) API credential for the OpenAI Chat Model node.
    - An SMTP credential for Email Reminder and Email Final Message (Gmail with an App Password is the most reliable option).
    - A Google Sheets OAuth2 credential for Log to Google Sheet, pointed at a sheet with columns: date, mood, stress, energy, concern, note, ai_response.
3. Update the fromEmail/toEmail fields in both email nodes to your own addresses.
4. Update the form link inside the Email Reminder node's message to match your own instance's form URL.
5. Activate the workflow (toggle top right). It will now run automatically every day at 18:00.

**Who did what?**
Evaldas and I brainstormed the concept together and discussed what problem we wanted to solve. I suggested that the response should include a personal affirmation, a reflection and one small action based on the user’s answers. I got this idea from another app I had used that shared daily quotes. I liked how something small like that could make the experience feel more personal instead of making the user feel like they were just filling in a form.

We both worked on the first version of the workflow, but it only ran up to a certain point. The AI-generated response was not being returned correctly. We were both still learning how n8n worked, but Evaldas was not at school, so we did not get the chance to troubleshoot it together in person. He later found and fixed the technical issue, completed the working version and wrote the first version of the README. He then sent the completed files to me. I adjusted my README and created the presentation slides.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
The tool handles sensitive information because users may share personal thoughts and mental health scores. This information is stored in Google Sheets, so it is important that the sheet is private and properly protected. There is also a risk that AI could misunderstand someone’s answers or generate a response that does not fit their situation. The tool should therefore never diagnose someone or replace professional help. Support resources are added when the answers suggest that someone may be struggling, but this is still only an extra safety measure and not a complete solution for someone in crisis.

### Checklist
- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [ ] The prototype actually runs, and I wrote down how to run it
- [ ] Ethical reflection written above

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
The most important thing I learned is how the different parts of an automated workflow depend on each other. A workflow is not just one piece of code. The trigger, form, AI, conditions, emails and Google Sheet all need to receive and pass on the correct information. If one node is not connected or configured correctly, the rest of the workflow may not work. I also learned that debugging a workflow means checking each step individually to find where the information stops or changes.

**Where does this connect to "AI for Good"?**
This project connects to AI for Good because it uses AI to make a simple mental health check-in feel more personal and supportive. Instead of only collecting scores, the AI acknowledges what the user shared and gives them one small action they can realistically do. It lowers the effort needed to regularly reflect on your mental well-being while also making safety, privacy and the limitations of AI clear.
