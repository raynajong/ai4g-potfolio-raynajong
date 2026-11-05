# Term 1 - Week 1: Python Basics & Flow Control

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

**Project title:** Campus Dutch

**My pair partner:** Felix Reichle

**Tool we had to use:** Bolt.new

**SDG we had to address:** SDG 4 – Quality Education (target 4.5: equal access to education; target 4.3: equal access to quality tertiary education)

**Live app:** https://campus-dutch-learnin-gf93.bolt.host/ · **Demo video:** https://youtu.be/0QLnrnBSYq0?si=SPjnhd8SDPF-OeT3 · **Code:** [`hackathon/campus-dutch-main/`](hackathon/campus-dutch-main/)


### The problem

International students in the Netherlands can study in English, but the institution around them often still runs in Dutch: student regulations, administrative emails, portal pages, grading terms and the way teachers phrase instructions. A student who misreads a word like *herkansing* (resit), *inschrijven* (register) or *uiterste inleverdatum* (final deadline) can miss a resit registration or a deadline without realising it.

**Evidence and what still needs to be checked**
[Nuffic's report on international students](https://www.nuffic.nl/en/node/2102) provides background on the international student population in the Netherlands. A [2019 survey reported by DutchNews](https://www.dutchnews.nl/news/2019/06/three-in-four-foreign-students-miss-contacts-with-the-dutch) also gives background on students' interest in learning Dutch and barriers to accessing courses. These sources help explain the context, but they do not directly establish how often students misunderstand Dutch administrative messages or miss deadlines because of them.

Our specific problem is therefore a hypothesis: international students with limited Dutch may benefit from learning common academic terms before encountering them in important messages. We have not yet validated the frequency or consequences of this problem through structured user research. A useful next step would be to ask international students for examples of confusing messages and ask student advisers which terms regularly lead to questions. This would help us check whether we chose the right vocabulary and whether a learning app is useful alongside translated information.

**The proposed gap.** General language apps and courses cover a wider range of Dutch. Campus Dutch focuses on a small set of academic terms that students may encounter during their first weeks. We have not systematically compared every course or app, so we do not claim that this vocabulary is unavailable elsewhere. Our intended advantage is having it together in short, focused lessons.

### Who it is for

**Intended users:** first- and second-year international students on an English-taught programme at a Dutch university or university of applied sciences.
* **Dutch level:** none to A2. The same practical content works for both, because it is vocabulary for recognising words, not grammar for speaking.
* **Situation:** comfortable in English, busy with a full study load, often also new to the country (housing, registration, bank). They do not have time for a full language course.
* **Conditions of use:** on a phone, in short sessions of 5–10 minutes between classes or on the train. No account, no installation.
* **Motivation:** they stick with something that pays off immediately ("now I understand that email"), not with a long course.

**Not intended for:**
* students on Dutch-taught programmes (they need academic writing in Dutch, not word recognition);
* people who want to *speak* Dutch in daily life (Duolingo or a language course fits them better);
* students already at B1 or higher (the content will be too easy);
* staff, and students who need to understand legal documents in detail (for example an appeal against an exam board decision): the app helps them *recognise* that a message is important, not replace the official text or an adviser.

### What we built

A web app that teaches the Dutch words and phrases of academic life with flashcards, quizzes and spaced repetition.

**Content.** 2 categories → 6 topics → 3 levels each (Beginner, Developing, Confident) = 18 lessons with 104 flashcards and 91 quiz questions in total.

| Category | Topics |
|---|---|
| School Systems and Assignments | Grades and Assessments · Deadlines and Submissions · Course Platforms and Schedules |
| Classroom and Teachers | Classroom Instructions · Talking to Lecturers · Asking Questions and Requesting Help |

**What the user does, step by step:**
1. **Pick a lesson.** The Beginner level of every topic is open from the start.
2. **Study the flashcards.** Each card shows the Dutch word, the English meaning, a short explanation of how it works at a Dutch university and an example sentence. Example: *Herkansing* – "Resit / retake" – "A second chance to pass an exam you failed the first time" – *Ik doe mee aan de herkansing van het tentamen.*
3. **Take the quiz the next day.** The quiz of a lesson opens one day after you first study it, so you have   to *recall* the words instead of reading them back. Each question shows an explanation after you answer.
4. **Unlock the next level.** A score of 80% or more opens the next level. 60% or more opens the other lessons at the same level in that category.
5. **Review daily.** Every card sits in one of 5 Leitner boxes. A correct answer moves it up a box, and it comes back after 1 → 3 → 7 → 14 → 30 days. A wrong answer sends it back to box 1 (tomorrow). "Today's Review" mixes all due cards from all topics.
6. **Track progress.** A progress page, a "word of the day" and 6 badges (for example *First Lesson*, *Perfect Score*).

**Output:** the student recognises the key words in a real email, portal page or exam notice, and the review schedule keeps them from forgetting them after a week.

Progress is stored in the browser (`localStorage`): no account, no server, no personal data leaves the device.


**Why the locks?** Quizzes open the day after a lesson is first studied, and higher levels open only after the level below is passed. This is deliberate: spread-out practice is remembered much longer than cramming in one session. To see the app as a student a few days in, switch on **Demo** (top right). Demo mode fills in realistic progress, so you see completed lessons, open quizzes, a review queue and earned badges; some higher levels are still locked, just as they would be for a real student at that point. The demo video shows what taking a quiz looks like in demo mode.

### How Bolt was used

Bolt.new generated and deployed the whole app (React, TypeScript, Tailwind) from our prompts. We decided what it should do: the topics and levels, the learn → next-day quiz → review loop, the unlock thresholds, the Leitner intervals and the demo mode. We then described each of these to Bolt step by step and tested the result after every change, asking for fixes where it did not behave as intended.

What did not work: we started adding support for more interface languages, but generating all content in several languages used too many Bolt tokens. The language selector is therefore not functional yet; the app is English → Dutch only.

### Why this solution fits the problem

* **Why not a glossary or Google Translate?** They only help once you already know that a message is important and stop to look it up. The risk is the email you skim and do not recognise as a deadline. Recognising the words *at a glance* needs repeated practice, and spaced repetition is a well-known way to make vocabulary stick.
* **Why not Duolingo or a Dutch course?** General Dutch learning has a broader purpose. Our prototype puts academic vocabulary first, so students can practise these terms without following a full general-language course. Whether students prefer this approach still needs user testing.
* **Why this format for this user?** Short lessons and one daily review queue fit the 5–10 minute gaps of a busy student; no account means no barrier to start; a phone browser is enough.

### How would it scale?

The app is static and stores progress on the user’s device, so it does not currently need a separate progress database for each user. Hosting capacity and costs would still need to be checked before a wider rollout. The real work is the content: terms differ between universities and universities of applied sciences, and between institutions. A next version would offer content packs per institution, written or checked by its international office or student advisers, with each phrase linked to the official source (for example the institution's Teaching and Examination Regulations). An account would let progress move between devices.

### How do I run it?

* **Online:** open https://campus-dutch-learnin-gf93.bolt.host/ and switch on **Demo** (top right) to see a student with a few days of progress. Switch it off to start as a new student.
* **Locally:** in [`hackathon/campus-dutch-main/`](hackathon/campus-dutch-main/) run `npm install` and then `npm run dev`, and open the address it prints (usually http://localhost:5173). Requires Node.js 18 or newer.

### Who did what?

Felix and I created the base of the project together on Friday. We both suggested changes to improve the app. I implemented those improvements in Bolt while Felix focused on creating our slides. We both contributed to the final polish of the project.

### Ethical reflection

**Who is excluded, and what does the app assume?**
* **Language:** the interface and explanations are English only. Students who are less confident in English face an additional barrier because both the explanations and the Dutch vocabulary may be unfamiliar.
* **Device and internet:** it assumes a smartphone or laptop with internet. Progress is saved in one browser, so a student who switches devices, uses a shared computer or clears their browser data loses their progress.
* **Prior knowledge:** it assumes the Dutch higher-education system is the one described. Words and procedures differ between universities and universities of applied sciences and between institutions, and our phrases were chosen by us, not checked against any one institution's regulations. A student can learn a term that their own school uses differently.
* **Accessibility:** there is no audio and we did not test it with screen readers, so visually impaired students may not be able to use it.

**How can it be used for the wrong reasons?**
* **As an excuse not to translate.** A university could point to an app like this instead of making its regulations and emails available in English. That shifts the burden onto the students with the least power, and makes the exclusion described above worse.
* **As a replacement for the official text.** A student who finished the app may feel ready and skip reading the regulations or asking an adviser. The highest-stakes moments (resit registration, appeals, the binding study advice) are exactly where a half-understood word costs the most: a missed resit can delay graduation, and for non-EU students a study delay can affect their residence permit.

**What we did and would do next:**
* **Done:** the app teaches *recognition* ("this is a resit message, act on it"), not legal detail, and it stores no personal data (no account, nothing leaves the browser).
* **Next:** add a visible note on high-stakes cards (resit, deadline, appeal, binding study advice): "Always check the official regulations or ask your study adviser"; link each phrase to the official source of the institution it was checked against; have a student adviser or international office review the content before real use; state clearly on the welcome page that the app supports, and does not replace, translated information from the university.

### Checklist
- [x] Prototype code (or export / workflow file) is in `hackathon/`
- [x] This week's slides are in `presentation/`
- [x] The prototype actually runs, and I wrote down how to run it
- [x] Ethical reflection written above

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

I learned that using Bolt is not only about writing a prompt and accepting what it generates. I still need to decide what the user actually needs, explain the features clearly and check whether the result works as intended. When I implemented our improvements, I had to translate our ideas into specific instructions. This helped me understand why a focused prompt is more useful than asking for many features at once, especially when working with a limited number of tokens.

I also learned that the learning flow needs to make sense to someone opening the app for the first time. We had reasons for delaying quizzes and locking levels, but those choices also made it harder for someone to explore the prototype quickly. Explaining the restrictions and providing a demo mode helps make the app easier to assess. A feature can have a clear purpose and still need better explanation for the user.

**What would I do differently next time?**

I would check the problem with students earlier, before spending as much time on the features. Our sources give useful background, but they do not prove that the specific vocabulary we selected causes difficulties. I would ask students to show examples of messages they found confusing and use those examples to decide what belongs in the lessons. I would then let them try a short lesson and check whether they can understand a similar message afterwards. That would give us more useful evidence than only checking whether the buttons and quizzes work.

I would also decide on a smaller first version and a clear demo route from the beginning. We tried to add more interface languages, but did not have enough tokens to finish that properly. Next time, I would prioritise one complete learning flow before adding extra options, and make unfinished features clearly recognisable.

**Where does this connect to "AI for Good"?**

For me, the connection is using an AI development tool to build something that could make studying more accessible. Bolt helped us turn our idea into a working prototype, but that does not automatically mean the app has a positive impact. We still need to check the content, test it with the intended users and be honest about what it can and cannot do.

Campus Dutch connects to SDG 4 because it aims to reduce a language barrier in education. However, an app like this should support students without making them responsible for fixing unclear university communication. Learning a few Dutch terms can be helpful, but important information should still be accessible in a language students understand. I learned that designing for a good cause also means thinking about who could be excluded and what could happen if someone relies too heavily on the app.
