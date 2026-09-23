# Term 1 - Week 3: Lists & Dictionaries

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
RentBuddy

**My pair partner:**

**Tool we had to use:**
We used Base44 to build the web app and connected the Contract Helper to the platform’s built-in AI. The AI feature uses an API to send the contract text to an AI model and return the explanation to the app.

**SDG we had to address:**
SDG 10: Reduced Inequalities

**What problem does it solve, and for whom?**
RentBuddy is made for international students aged 18 to 30 who are searching for housing in The Hague. They may struggle to understand Dutch rental contracts, housing terminology, registration requirements and subletting rules. This puts them at a disadvantage compared with students who already speak Dutch and understand the Dutch rental system.

**What did you build?**
We built a web app where international students can find useful information about renting and subletting in The Hague. Users can explore housing resources, learn important Dutch rental terms and use the Contract Helper to translate and explain the most important parts of a Dutch rental contract in their preferred language.

**Link to the live thing (if any):**
_Deployed URL, workflow export, video demo - whatever proves it works._

**How do I run it?**
Open the live link in a browser and use the navigation menu to explore the different pages. To use the AI feature, open the Contract Helper, paste the text of a Dutch rental contract, choose a language and click “Analyse my contract.” The app then sends the text to the AI and displays the explanation.

**How does the API work?**
When someone uses the Contract Helper, the contract text and selected language are sent to a secure function inside the platform. This function gives the AI instructions about what information to find, such as the rent, deposit, notice period, service costs and subletting conditions. The AI sends its answer back to the app, where it is organised into clear sections for the user. The API key is kept securely on the backend and is not visible in the website or browser.

**Who did what?**
I worked on the idea and target audience, prompt with help from AI to build the app. My partner worked on helping me figure out the API, a bit of desk research and the powerpoint. We worked together on brainstorming and figuring out how the API works.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
The biggest risk is that the AI could misunderstand part of a rental contract, leave out important information or make a translation mistake. This could harm international students who rely on the explanation and cannot easily check the original Dutch contract themselves. To reduce this risk, RentBuddy shows which information was found in the contract, says when something is not clearly stated and warns users that the result is not legal advice. Users are encouraged to verify important information with organisations such as the Huurcommissie, Juridisch Loket or the Municipality of The Hague. Contracts can also contain private information, so users are warned to remove unnecessary names, addresses, signatures and bank details before submitting them.

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
The most important thing I learned is how an API allows a website to communicate with an AI model. I also learned that building an AI feature is not only about getting an answer. You also have to think about privacy, incorrect answers and how to make it clear when the AI is uncertain.

**Where does this connect to "AI for Good"?**
RentBuddy uses AI to reduce the information disadvantage experienced by international students in the Dutch housing market. It makes difficult rental information easier to understand, which can help students ask better questions, recognise possible risks and make more informed decisions before signing a contract.
