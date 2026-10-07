# Term 1 - Week 5: Machine Learning Basics

## 1. Homework & workshop assignments → [`homework/`](homework/)

**What was the assignment?**

This week's topic was machine learning basics. The hackathon applied these ideas by comparing classification models on a real dataset. The exact homework and workshop tasks should be listed here separately from the hackathon.

**What did I hand in?**

[Add the names and links of your Week 5 homework and workshop files. The supplied project files do not identify these submissions.]

**What did I find difficult, and how did I solve it?**

[Add your own example of something you found difficult and what you did to understand or fix it. For example, explain whether you needed help understanding recall, cross-validation or the Python code, and describe what actually helped.]

### Checklist

- [ ] My workshop / homework files are in `homework/`
- [ ] Everything runs without errors, or I explained what does not and why

---

## 2. Hackathon prototype → [`hackathon/`](hackathon/)

**Project title:** Model Showdown: Predicting Credit-Card Default

**My pair partner:** [Add your Week 5 partner's name.]

**Tool we had to use:** A Python Jupyter notebook with scikit-learn. The notebook can run in Google Colab. We compared K-Nearest Neighbours (KNN), Logistic Regression and Random Forest. [Add the AI assistant(s) you actually used to help develop or understand the code.]

**SDG we had to address:** SDG 8: Decent Work and Economic Growth.

### What problem does it solve, and for whom?

The project investigates whether machine learning can predict if a credit-card customer will default on their payment next month. Default means failing to make the required payment. The intended user is a credit-risk analyst at a bank or credit-card provider, who could use predictions to identify cases that need further review.

The affected people are the credit-card customers. A correct prediction could help an institution recognise financial risk, but an incorrect prediction could also lead to unnecessary restrictions for a customer. This prototype explores decision support. It does not demonstrate that it improves customer outcomes or that it is ready for real financial decisions.

The connection to SDG 8 is responsible financial services and economic security. In particular, target 8.10 concerns strengthening financial institutions and expanding access to financial services. A model like this would need safeguards to support that goal without unfairly limiting access to credit.

### What did you build?

We built a notebook that loads a real credit-card dataset, prepares the data and compares three classification models against a simple baseline. It includes model tuning, performance tables, confusion matrices, error analysis and a subgroup comparison. It also demonstrates a prediction for a fictional customer, returning both a predicted class and an estimated probability of default.

#### Dataset and preparation

We used the UCI **Default of Credit Card Clients** dataset. It contains 30,000 customers in Taiwan, 23 predictor features and a target indicating default in the following month. The records contain historical information from April to September 2005, including credit limits, repayment history, bill amounts and previous payments.

There are 23,364 non-default cases and 6,636 default cases. Approximately 22.1% of customers defaulted, so the classes are imbalanced. This matters because a model can achieve fairly high accuracy simply by predicting the more common outcome.

The notebook removes the `ID` column and separates the target from the predictors. It uses a stratified split with 80% of the data for training and 20% for testing, keeping a similar class balance in both sets. This gives 24,000 training rows and 6,000 test rows, with `random_state=42` to make the split reproducible.

Preprocessing happens inside scikit-learn pipelines. `StandardScaler` scales numerical features, while `OneHotEncoder` converts categorical values into columns the models can use. Keeping preprocessing inside the pipeline means the models fit these transformations using their training folds, which helps prevent information from leaking into the evaluation.

#### Why we chose recall

Our main metric is **recall for the default class**. Recall measures the proportion of customers who actually defaulted that the model correctly identified.

A **false negative** means a customer defaults, but the model predicts no default. We prioritised recall because these missed defaults underestimate financial risk. A **false positive** means the model predicts default for someone who does not default. Those errors also matter because they could cause unnecessary risk flags or restrictions.

The baseline always predicts the majority class: no default. It achieves 77.9% test accuracy but 0% recall for default. This shows why accuracy alone would give a misleading impression of success.

#### The three models and tuning

| Model | Simple explanation | Best settings in this experiment |
|---|---|---|
| KNN | Predicts using the outcomes of similar customers. | `n_neighbors=3`, `weights=distance` |
| Logistic Regression | Uses weighted features to estimate the probability of default. | `C=10` |
| Random Forest | Combines predictions from many decision trees. | `n_estimators=100`, `max_depth=None`, `min_samples_split=5` |

We used `GridSearchCV` with five-fold cross-validation and recall as the scoring metric. It tests different settings on splits of the training data and selects the settings with the highest average validation recall. The separate test set provides the final evaluation on unseen cases.

| Model | Training recall | Cross-validation recall | Test recall |
|---|---:|---:|---:|
| KNN | 99.8% | 35.5% ± 0.9 percentage points | 36.1% |
| Logistic Regression | 36.4% | 36.0% ± 1.2 percentage points | 35.3% |
| Random Forest | 89.2% | 37.3% ± 0.9 percentage points | 36.2% |

The cross-validation spread is the standard deviation across folds, not a confidence interval. KNN and Random Forest perform much better on their training data than on validation or test data. This suggests overfitting: they fit the training examples better than they generalise to new customers.

#### Final model comparison

The following results come from the saved notebook outputs. Values are rounded to one decimal place.

| Model | Accuracy | Precision | Recall | F1 score |
|---|---:|---:|---:|---:|
| Baseline | 77.9% | 0.0% | 0.0% | 0.0% |
| KNN | 77.2% | 47.9% | 36.1% | 41.2% |
| Logistic Regression | 81.7% | 66.1% | 35.3% | 46.0% |
| Random Forest | 81.6% | 65.3% | 36.2% | 46.6% |

Accuracy measures the proportion of all predictions that are correct. Precision measures how many customers flagged as defaulting actually defaulted. Recall measures how many actual defaults the model catches. F1 combines precision and recall into one score.

Random Forest is our preferred model for this experiment. It has the highest cross-validation recall and narrowly achieves the highest test recall and F1 score. Logistic Regression performs slightly better on accuracy and precision. The differences are small, and this experiment does not establish that Random Forest would consistently outperform the other models in other settings.

#### Error analysis and limitations

The Random Forest confusion matrix shows:

| Actual outcome | Predicted no default | Predicted default |
|---|---:|---:|
| No default | 4,417 correct predictions | 256 false positives |
| Default | 846 false negatives | 481 correct predictions |

The model catches only 481 of the 1,327 actual defaults in the test set. It misses approximately 63.8%, which is a major limitation despite its 81.6% overall accuracy.

The notebook compares the average characteristics of missed defaults with correctly detected defaults. Missed cases have less obvious repayment-delay patterns. This descriptive comparison helps investigate the errors, but it does not prove why each individual prediction failed.

We also compared recall across the dataset's two `SEX` groups: 35.8% for group 1 and 36.6% for group 2. These results are close, but one subgroup comparison cannot prove fairness. More groups and additional measures, including false-positive rates, would need examination.

#### Fictional customer demonstration

For a made-up customer, the saved Random Forest output predicts class `1`, meaning default, with an estimated default probability of approximately 53.3%. This demonstrates how a new case passes through the trained pipeline. The estimate is uncertain, and the notebook does not show whether the probabilities are well calibrated.

### Link to the live thing (if any)

The prototype is a notebook rather than a deployed website. Open [`Hackathon5-model showdown.ipynb`](hackathon/Hackathon5-model%20showdown.ipynb) to inspect the code and saved outputs. The notebook includes the fictional customer demonstration.

[Add a recording or Colab link if you have one. The relative notebook link assumes you place the file in `hackathon/`.]

### How do I run it?

1. Download the notebook from the `hackathon/` folder.
2. Open Google Colab and choose **File → Upload notebook**.
3. Upload `Hackathon5-model showdown.ipynb`.
4. Choose **Runtime → Run all** and run the cells from top to bottom.
5. The notebook downloads the dataset from UCI, prepares the data, trains and tunes the models, and produces the evaluation outputs.
6. Scroll to **New Customer Prediction** to view the fictional example. You can change its inputs and rerun that cell to try another case.

The notebook uses pandas, NumPy, scikit-learn and matplotlib. An internet connection is required for the dataset download, and model tuning may take some time. The saved outputs document the supplied run; a fresh run may vary with library versions. If Excel loading reports a missing `xlrd` dependency, install it in Colab with `%pip install xlrd` and rerun the loading cell.

### Who did what?

- **My contribution:** [Describe the research, notebook work, checking, README or presentation work you actually completed.]
- **My partner's contribution:** [Add your partner's actual tasks.]
- **Our collaboration with AI:** [Name the AI tool(s), explain what help you requested and describe how you checked or changed the output. Include a real example of a decision you made instead of accepting the generated result unchanged.]

### Ethical reflection: what are the risks of your tool? Who could it harm?

Incorrect predictions could harm credit-card customers if a bank treats them as high risk and restricts financial services unnecessarily. Missed defaults could also cause losses for the institution and overlook customers who may need further support. The dataset represents a historical population in Taiwan, so we cannot assume the model works accurately or fairly for current customers in the Netherlands or elsewhere. Demographic variables raise fairness concerns, and our comparison of two sex groups is too limited to establish fairness. The model also misses most actual defaults. For these reasons, this prototype should not automatically determine access to credit. Any future use would require further validation, broader fairness checks, appropriate protection of personal data and human review, with a way for affected customers to question consequential decisions.

### Checklist

- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [ ] The prototype actually runs, and I wrote down how to run it
- [x] Ethical reflection written above

The saved notebook contains execution outputs. Confirm a fresh run and the repository folder locations before checking the remaining boxes.

---

## 3. Presentation → [`presentation/`](presentation/)

Only complete this section if your group was selected to present this week.

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

[If you presented, describe how it actually went and one specific improvement. Otherwise, write: “Not applicable: our group was not selected to present this week.”]

---

## 4. Reflection

**What is the most important thing I learned this week?**

*Suggested wording to adapt to your own experience:*

I learned that a high accuracy score does not automatically mean a model is useful. Our baseline was correct about 78% of the time while missing every default case. Comparing recall, validation results and actual mistakes helped me understand why the evaluation metric needs to match the problem. I also learned that a model can perform very well on training data and still struggle with new cases.

**Where does this connect to “AI for Good”?**

This project connects to AI for Good through responsible financial services and economic security under SDG 8. Credit-risk predictions could support human review, but they could also unfairly restrict someone's financial opportunities. The potential benefit depends on testing the model's limitations, protecting customers and making sure a human remains accountable for consequential decisions.

### Sources

- Project evidence: `Hackathon5-model showdown.ipynb` and `README-Hackathon 5.md`.
- Desk research: `Hackathons 5 - Modal showdown.pdf`.
- UCI dataset: https://archive.ics.uci.edu/dataset/350/defaultofcreditcardclients
- Dataset citation: Yeh, I. C. (2009). *Default of Credit Card Clients*. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H
- SDG 8: https://sdgs.un.org/goals/goal8
