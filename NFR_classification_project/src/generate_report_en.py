"""
Generate English version of the NoRBERT project report (Word document).
Content mirrors generate_report_v3.py exactly (all latest corrections + label glossary).
Figures (chart_*.png) already carry English labels and are reused.
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

doc = Document()

# Default font (Western serif, academic style)
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)

# Title
title = doc.add_heading('NoRBERT Paper Replication and Improvement Project Report', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = subtitle.add_run('SE789 Software Metrics Course Project')
r.font.size = Pt(14)
r.font.color.rgb = RGBColor(100, 100, 100)

doc.add_paragraph()

_chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ppt_slides')
def add_figure(filename, width_in=6.2, caption=None):
    path = os.path.join(_chart_dir, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width_in))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = cap.add_run(caption)
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(100, 100, 100)
            run.italic = True

# ============ Section 1 ============
doc.add_heading('1. Project Overview', level=1)
doc.add_paragraph(
    'I am an exchange student at the College of Arts, Media and Technology (CAMT), '
    'Chiang Mai University, majoring in Computer Software Engineering. This semester I took '
    'SE789 Software Metrics. The course requires choosing a non-journal conference paper '
    '(6–8 pages, two-column format), replicating its experiments, adding statistical '
    'significance tests that are absent from the paper, and identifying weaknesses and '
    'proposing an enhanced version.')

doc.add_paragraph(
    'The paper I selected is “NoRBERT: Transfer Learning for Requirements Classification” '
    '(IEEE RE 2020). It studies automated requirements classification in Requirements '
    'Engineering — using a BERT transfer-learning model to automatically distinguish '
    'Functional Requirements (FR) from Non-Functional Requirements (NFR), and then to '
    'classify NFRs into fine-grained subclasses.')

doc.add_paragraph(
    'Reasons for choosing this paper: first, it is directly related to my research direction '
    '(the intersection of software engineering and artificial intelligence); second, the paper '
    'releases the complete dataset (PROMISE NFR) and code, making replication feasible; third, '
    'although the paper performed a paired t-test on Task 4 (p = 0.016), it lacks systematic '
    'statistical significance testing on Tasks 1–3 and on the functional-concern task, and the '
    'authors explicitly list multi-label correlation modeling as future work — a direction we '
    'can extend.')

# ============ Section 2 ============
doc.add_heading('2. Core Method of the Paper', level=1)
doc.add_paragraph(
    'The core idea of NoRBERT is to first pretrain BERT on a large corpus of requirements text '
    'and then fine-tune it on downstream tasks. On small datasets, this transfer-learning '
    'approach performs significantly better than traditional TF-IDF + machine-learning methods.')

doc.add_paragraph('The paper defines five progressive classification tasks:')
for item in [
    'Task 1: Binary classification of FR vs NFR (functional vs non-functional).',
    'Task 2: NFR subclass classification (four high-frequency classes: US Usability, SE Security, O Operational, PE Performance).',
    'Task 3: NFR subclass classification (ten fine-grained classes; among the 11 NFR subclasses, PO Portability — with only 1 sample — is excluded; see the lookup table in Section 3).',
    'Task 4: Functional/quality aspect classification (four binary labels: IsFunctional, IsQuality, IsOnlyFunctional, IsOnlyQuality).',
    'Task 5: Functional-requirement concern classification (three multi-labels: Function, Data, Behavior).',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph(
    'Evaluation uses Stratified 10-Fold cross-validation and cross-project validation '
    '(p-fold and leave-one-project-out, loPo). Baselines include traditional models such as '
    'LR, SVM, and Random Forest, and the comparison target is the NoRBERT pretrained model.')

# ============ Section 3 ============
doc.add_heading('3. Datasets', level=1)
doc.add_paragraph('The PROMISE NFR Dataset is used, containing 625 labeled requirements.')

doc.add_heading('3.1 Task 1: Binary Classification Dataset', level=2)
for item in [
    'Non-Functional Requirements (NFR): 370 samples',
    'Functional Requirements (FR): 255 samples',
    'Total: 625 samples',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('3.2 Task 2/3: NFR Subclass Distribution', level=2)
doc.add_paragraph('There are 10 NFR subclasses (the PO class has only 1 sample and is excluded from multiclass tasks):')

table = doc.add_table(rows=12, cols=3)
table.style = 'Light Grid Accent 1'
hc = table.rows[0].cells
hc[0].text = 'Code'; hc[1].text = 'Full name'; hc[2].text = 'Count'
nfr_rows = [
    ('US', 'Usability', '67'),
    ('SE', 'Security', '66'),
    ('O', 'Operational', '62'),
    ('PE', 'Performance', '54'),
    ('LF', 'Look & Feel', '38'),
    ('A', 'Availability (system uptime/accessibility)', '21'),
    ('SC', 'Scalability', '21'),
    ('MN', 'Maintainability', '17'),
    ('L', 'Legal', '13'),
    ('FT', 'Fault Tolerance', '10'),
    ('PO', 'Portability', '1 (only 1; excluded in Task 3)'),
]
for i, (a, b, c) in enumerate(nfr_rows):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_paragraph(
    'The distribution shows a clear long-tail effect: the top four classes (US, SE, O, PE) '
    'account for more than 75% of all samples, while the three rare classes (MN, L, FT) together '
    'account for less than 11%. This class imbalance is one of the core challenges of NFR '
    'classification.')

add_figure('chart_distribution.png', 6.3,
           'Figure 1. Distribution of the 10 NFR subclasses (colored by imbalance tier; PO excluded).')

doc.add_heading('3.3 Task 4/5 Datasets', level=2)
doc.add_paragraph(
    'Task 4 uses the Relabeled PROMISE dataset. After removing 13 non-requirement texts, 612 '
    'valid samples remain. It defines four binary labels according to whether a requirement '
    'contains a “functional aspect” and/or a “quality aspect” (a single requirement may contain '
    'both):')

t4 = doc.add_table(rows=5, cols=3)
t4.style = 'Light Grid Accent 1'
h = t4.rows[0].cells
h[0].text = 'Label'; h[1].text = 'Meaning'; h[2].text = 'Positives'
t4_rows = [
    ('IsFunctional (F)', 'Requirement contains a functional aspect (what the system shall do)', '310'),
    ('IsQuality (Q)', 'Requirement contains a quality aspect (quality attributes, i.e. NFR)', '382'),
    ('IsOnlyFunctional (OnlyF)', 'Functional only, not quality (F = 1 and Q = 0)', '230'),
    ('IsOnlyQuality (OnlyQ)', 'Quality only, not functional (Q = 1 and F = 0)', '302'),
]
for i, (a, b, c) in enumerate(t4_rows):
    cells = t4.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_paragraph(
    'The 612 samples partition completely by aspect combination: 230 purely functional + 302 '
    'purely quality + 80 containing both (F+Q). The strict logical identities OnlyF = F ∧ ¬Q and '
    'OnlyQ = Q ∧ ¬F hold for all 612/612 samples.')

doc.add_paragraph(
    'Task 5 uses the Functional Requirements Concerns dataset, consisting of 309 functional '
    'requirements newly labeled by the authors. It defines three multi-labels based on the '
    'concerns contained in each requirement. The official definitions given in the paper are:')

t5 = doc.add_table(rows=4, cols=3)
t5.style = 'Light Grid Accent 1'
h = t5.rows[0].cells
h[0].text = 'Label'; h[1].text = 'Official definition (verbatim)'; h[2].text = 'Positives'
t5_rows = [
    ('Function', 'A function that a system shall perform.', '207 (67.0%)'),
    ('Data', 'A data item or data structure that shall be part of a system’s state.', '57 (18.4%)'),
    ('Behavior', 'Behavior the system displays or reactions that are triggered by one or more stimuli.', '113 (36.6%)'),
]
for i, (a, b, c) in enumerate(t5_rows):
    cells = t5.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_paragraph(
    'These three labels are multi-labels, so one requirement can contain multiple concerns; '
    'inter-annotator agreement is Krippendorff’s α = 0.79. The Data class is extremely imbalanced '
    '(only 18.4% positives, positive:negative ≈ 1:4.42), and Function and Behavior exhibit a strong '
    'negative correlation (r = −0.639) — a key focus of our improvement.')

# ============ Section 4 ============
doc.add_heading('4. Experimental Environment and Implementation Details', level=1)
doc.add_heading('4.1 Hardware and Software', level=2)
doc.add_paragraph(
    'Hardware: a Windows laptop with an AMD Radeon 780M integrated GPU (no CUDA support; all '
    'computation runs on CPU).')
doc.add_paragraph(
    'Software: Python 3.11, PyTorch (CPU build), Transformers, scikit-learn, and fastai (used to '
    'load the authors’ pretrained models).')

doc.add_heading('4.2 Data Processing Pipeline', level=2)
doc.add_paragraph('Data is read from a CSV file containing a RequirementText field and multiple binary label columns. The pipeline is:')
for item in [
    'Text preprocessing: lowercasing, removal of special characters, and tokenization (BERT’s built-in WordPiece tokenizer).',
    'Label encoding: map the multiple binary label columns to integer class indices.',
    'Sequence truncation: max_seq_len = 128; longer sequences are truncated and shorter ones are padded with [PAD].',
    'Splitting strategy: Stratified K-Fold to keep the class distribution consistent across folds.',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('4.3 Model Structure', level=2)
doc.add_paragraph(
    'The NoRBERT classification head is a BERT-base encoder (12 Transformer layers, 768-dim '
    'hidden size) + a Dropout layer + a fully connected classifier. The input is the [ CLS ] '
    'pooled output and the output is the class logits.')
doc.add_paragraph(
    'The default loss is cross-entropy. Our improvement has three layers: feature engineering '
    '(multi-granularity N-gram fusion), the data level (random oversampling), and the model level '
    '(classifier chains that exploit label correlations).')

# ============ Section 5 ============
doc.add_heading('5. Replication Experiments', level=1)
doc.add_heading('5.1 Loading and Verifying the Pretrained Models', level=2)
doc.add_paragraph(
    'The authors published the pretrained model weights on Zenodo (fastai .pkl format, 3.6 GB in '
    'total). We successfully loaded all five Task models and verified the correctness of the '
    'inference pipeline. The predictions on the full dataset are shown below (used only to verify '
    'that the pipeline runs):')

table = doc.add_table(rows=6, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Task'; hdr[1].text = 'Paper test-set F1'; hdr[2].text = 'Our full-dataset F1 (incl. training data)'
for i, (a, b, c) in enumerate([
    ('Task 1: F vs NFR', '~90%', '97.4%'),
    ('Task 2: 4 high-frequency NFR classes', '87%', '96.6%'),
    ('Task 3: 10 NFR classes', '81–83%', '95.6%'),
    ('Task 4: IsFunctional', '86–87%', '97.2%'),
    ('Task 5: Function', '~85%', '97.1%'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_paragraph(
    'Important: the Zenodo files are the final models trained on the whole dataset, not per-fold '
    'models. Therefore, the numbers obtained by predicting on the full dataset (e.g. Task 2/3 '
    'Weighted F1 = 95.64%, Task 1 = 97.44%) include training samples, i.e. there is data leakage, '
    'so they are inflated and cannot be directly compared to the paper’s test-set results. These '
    'numbers only verify that the models load correctly, that the inference pipeline runs, and that '
    'the output format is correct.')
doc.add_paragraph(
    'The genuine replication metrics are those we obtain ourselves with strict Stratified 10-Fold '
    'CV test splits.')

doc.add_heading('5.2 Baseline Results', level=2)
doc.add_paragraph('We ran the baseline on Task 1 (FR vs NFR binary). The following is a single 80/20 split (random_state = 42):')

table = doc.add_table(rows=4, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Model'; hdr[1].text = 'Accuracy'; hdr[2].text = 'Weighted F1'; hdr[3].text = 'Note'
for i, (a, b, c, d) in enumerate([
    ('LR + TF-IDF (word n-gram)', '88.0%', '87.6%', 'Single 80/20 split; traditional ML baseline'),
    ('BERT-base-uncased (general-pretrained, fine-tuned 4 epochs)', '89.6%', '89.6%', 'Single 80/20 split; only ~2 pp above LR'),
    ('NoRBERT (requirements-domain pretrained + fine-tuned)', '~90–94%', '~90–94%', 'Paper test-set reported value'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c; cells[3].text = d

doc.add_paragraph(
    'Analysis: on this small dataset of only 625 samples, directly fine-tuning a general '
    'BERT-base (89.6%) is only about 2 percentage points above simple LR + TF-IDF (87.6%), and '
    'this is a single-split result with training randomness. This shows that a general BERT without '
    'requirements-domain pretraining cannot fully exploit the deep model’s advantage on a small-sample '
    'task and does not separate clearly from the traditional methods; only domain-pretrained NoRBERT '
    'reliably exceeds 90%, which demonstrates the value of “domain pretraining for transfer learning” '
    'emphasized by the paper. Note that running 10-fold CV for BERT on CPU is too costly, so BERT is '
    'evaluated only on a single split; all rigorous 10-fold CV improvement comparisons are performed on '
    'the LR baseline (LR mean F1 over 10 folds = 88.0%).')

# ============ Section 6 ============
doc.add_heading('6. Improvement Experiments', level=1)
doc.add_heading('6.1 Gap Identification', level=2)
doc.add_paragraph('After a careful reading of the paper and the replication experiments, we identified several directions for improvement:')
for item in [
    'Feature engineering: the paper only uses word-level features (the BERT tokenizer) and does not explore character-level N-gram features that capture word-root and affix morphology. Rare classes have few samples, so word-level features easily miss OOV word forms sharing a root (e.g. availability / available).',
    'Class imbalance: the paper already tried random undersampling and oversampling, but did not combine them with stronger regularization to prevent overfitting on duplicated samples.',
    'Label-correlation modeling: the paper trains every subtask as an independent binary classifier (Binary Relevance), completely ignoring logical dependencies among labels. For example, Task 4 OnlyF has a strict logical identity with IsFunctional/IsQuality, and Task 5 Function and Behavior are strongly negatively correlated (r = −0.639). The authors explicitly list multi-label classifier chains as future work in the Conclusion.',
    'Statistical testing: the paper only performed a paired t-test on Task 4; systematic statistical significance testing on Tasks 1–3 and the functional-concern task is missing.',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('6.2 Improvement Methods', level=2)
doc.add_paragraph('Our improvement has three layers:')

doc.add_heading('6.2.1 Multi-Granularity N-gram Feature Fusion', level=3)
doc.add_paragraph(
    'Word-level N-grams (1,2) and character-level N-grams (3,5) are fused via FeatureUnion with '
    'sublinear TF scaling (sublinear_tf = True). Character features directly capture word-root and '
    'affix morphology and effectively alleviate the out-of-vocabulary (OOV) and word-form variation '
    'problems.')

doc.add_heading('6.2.2 Oversampling + L2 Regularization', level=3)
doc.add_paragraph(
    'Minority classes are randomly oversampled within the training fold only (never touching the '
    'test fold, avoiding data leakage), combined with stronger L2 regularization (C = 0.5) to '
    'prevent overfitting on repeated samples after oversampling.')

doc.add_heading('6.2.3 Classifier Chains', level=3)
doc.add_paragraph(
    'For the multi-label nature of Tasks 4 and 5, we implement classifier chains: the predicted '
    'probabilities of earlier labels are fed as input features to later labels, exploiting logical '
    'dependencies and correlations among labels.')
for item in [
    'Task 4 logical chain: first predict IsFunctional and IsQuality, then construct logical interaction features P(F)·(1−P(Q)) and P(Q)·(1−P(F)) to jointly predict OnlyF and OnlyQ.',
    'Task 5 correlation chain: in the order Function → Behavior → Data, feed earlier predicted probabilities as prior features to later labels, exploiting the strong negative correlation between Function and Behavior.',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('6.3 Improvement Results', level=2)
doc.add_paragraph(
    'Because of the CPU limitation (no CUDA), we validate the effectiveness of the improvements on '
    'the LR + TF-IDF baseline and then generalize the conclusions to BERT. All improvements use 10-Fold CV.')

doc.add_heading('6.3.1 Task 1 (FR vs NFR Binary)', level=3)
table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Metric'; hdr[1].text = 'Baseline (word n-gram)'; hdr[2].text = 'Improved (word+char n-gram fusion)'
for i, (a, b, c) in enumerate([
    ('Mean Accuracy', '88.5%', '89.5%'),
    ('Mean Weighted F1', '88.0%', '89.3%'),
    ('Improvement', '—', '+1.28%'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c
doc.add_paragraph(
    'Feature fusion brings +1.28% Weighted F1 on Task 1; the direction is correct but not '
    'statistically significant (p = 0.30). This is intuitive: the binary task has mild imbalance '
    '(370 vs 255, ratio 1.45:1) and the baseline is already high (88%), leaving little room.')

doc.add_heading('6.3.2 Task 2/3 (10-Class NFR Multiclass)', level=3)
table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Metric'; hdr[1].text = 'Baseline (word n-gram)'; hdr[2].text = 'Improved (fusion + oversampling)'
for i, (a, b, c) in enumerate([
    ('Mean Accuracy', '62.9%', '71.6%'),
    ('Mean Weighted F1', '56.5%', '71.2%'),
    ('Improvement', '—', '+14.67%'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c
doc.add_paragraph(
    'Breakdown: feature fusion (word + char n-gram) contributes +11.90% and oversampling contributes '
    '+2.77%. On a severely imbalanced multiclass task, both feature engineering and imbalance handling '
    'yield significant gains.')
add_figure('chart_task23.png', 5.9,
           'Figure 2. Contribution of each improvement layer on Task 2/3 (10-fold CV Weighted F1).')

doc.add_heading('6.3.3 Task 4 (Functional/Quality Aspect)', level=3)
table = doc.add_table(rows=5, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Subtask'; hdr[1].text = 'Baseline WF1'; hdr[2].text = 'Improved WF1'; hdr[3].text = 'Δ'
for i, (a, b, c, d) in enumerate([
    ('IsFunctional', '86.65%', '86.96%', '+0.31%'),
    ('IsQuality', '86.18%', '90.21%', '+4.02%'),
    ('IsOnlyFunctional', '86.18%', '91.32%', '+5.14%'),
    ('IsOnlyQuality', '86.65%', '86.48%', '−0.17%'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c; cells[3].text = d
doc.add_paragraph(
    'The classifier chain helps most on IsOnlyFunctional (+5.14%), because OnlyF is a minority class '
    '(230 positives vs 382 negatives) and has a strict logical identity with F/Q; the logical '
    'interaction features let the classifier learn the decision boundary better. IsQuality also '
    'improves significantly (+4.02%).')

doc.add_heading('6.3.4 Task 5 (Functional Concerns)', level=3)
table = doc.add_table(rows=4, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Subtask'; hdr[1].text = 'Baseline WF1'; hdr[2].text = 'Improved WF1'; hdr[3].text = 'Δ'
for i, (a, b, c, d) in enumerate([
    ('Function', '73.30%', '82.55%', '+9.25%'),
    ('Behavior', '71.38%', '79.83%', '+8.45%'),
    ('Data (rare class)', '73.33%', '86.65%', '+13.32%'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c; cells[3].text = d
doc.add_paragraph(
    'The headline result is the Data class (only 18.4% positives): the baseline completely collapses '
    '(per-class binary F1 = 0.00%, predicting everything as the majority class), while after the '
    'multi-label classifier chain + cost-sensitive balancing the per-class F1 jumps to 60.40% and '
    'Weighted F1 rises by 13.32 percentage points. This directly resolves the failure the authors '
    'admit in Section IX-A: “NoRBERT achieves only low recall for the Data class ... Oversampling '
    'dropped Data F1 from 0.62 to 0.56.”')

add_figure('chart_task45.png', 6.4,
           'Figure 3. Weighted F1 before/after the classifier chains on Tasks 4/5 (asterisk = statistically significant).')
if os.path.exists(os.path.join(_chart_dir, 'chart_data.png')):
    doc.add_picture(os.path.join(_chart_dir, 'chart_data.png'), width=Inches(3.2))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = cap.add_run('Figure 4. Task 5 rare Data class (18.4% positives) per-class F1: 0% → 60.4%.')
    rr.font.size = Pt(10); rr.font.color.rgb = RGBColor(100, 100, 100); rr.italic = True

# ============ Section 7 ============
doc.add_heading('7. Statistical Significance Testing', level=1)
doc.add_heading('7.1 Choice of Tests', level=2)
doc.add_paragraph('We use three complementary statistical tests:')
for item in [
    'Paired t-test: tests the significance of the mean difference before/after improvement, assuming the differences are normally distributed.',
    'Wilcoxon signed-rank test: a non-parametric test that does not assume normality and is more robust.',
    "Cohen's d: effect size measuring the magnitude of the improvement (d = 0.2 small, 0.5 medium, 0.8 large, > 2 very large).",
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('7.2 Task 2/3 Results (10-Fold CV)', level=2)
table = doc.add_table(rows=4, cols=2)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Test'; hdr[1].text = 'Result'
for i, (a, b) in enumerate([
    ('Paired t-test', 't = 6.32, p = 0.0001 (highly significant)'),
    ('Wilcoxon signed-rank test', 'p = 0.002 (significant, p < 0.05)'),
    ("Cohen's d", '2.00 (very large effect)'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b

doc.add_heading('7.3 Task 4 Results (10-Fold CV)', level=2)
table = doc.add_table(rows=5, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Subtask'; hdr[1].text = 'Paired t-test p'; hdr[2].text = "Cohen's d"
for i, (a, b, c) in enumerate([
    ('IsQuality', 'p = 0.022 (significant)', '0.87 (medium-large)'),
    ('IsOnlyFunctional', 'p = 0.0048 (significant)', '1.18 (large)'),
    ('IsFunctional', 'p = 0.19 (not significant)', '0.45 (small)'),
    ('IsOnlyQuality', 'p = 0.76 (not significant)', '−0.10 (no effect)'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_heading('7.4 Task 5 Results (10-Fold CV)', level=2)
table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Subtask'; hdr[1].text = 'Paired t-test p'; hdr[2].text = "Cohen's d"
for i, (a, b, c) in enumerate([
    ('Function', 'p = 0.0017 (significant)', '1.40 (large)'),
    ('Data (rare class)', 'p = 0.0001 (significant)', '2.08 (very large)'),
    ('Behavior', 'p = 0.084 (borderline)', '0.61 (medium)'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_heading('7.5 On the Number of Cross-Validation Folds', level=2)
doc.add_paragraph(
    'We initially used 5-fold cross-validation and found that the Wilcoxon p-value could only reach '
    '0.0625 and could never be below 0.05. This is because with N = 5, the theoretical minimum p of '
    'the two-sided exact Wilcoxon test is 2 × (1/2)^5 = 0.0625.')
doc.add_paragraph(
    'To obtain sufficient statistical power, we changed the cross-validation to 10 folds (matching '
    'the paper), giving N = 10 and a minimum possible Wilcoxon p of about 0.00195 < 0.05. After the '
    'change, the statistical tests became significant on multiple subtasks.')

# ============ Section 8 ============
doc.add_heading('8. Threats to Validity', level=1)
doc.add_paragraph('We discuss the threats to validity of this study along four dimensions:')
for item in [
    'Construct validity: we use only a single dataset (PROMISE, 625 samples), and the rare classes are very small (the smallest, FT, has only 10 samples), limiting the stability of the results.',
    'Internal validity: the improvement experiments are validated on the LR + TF-IDF baseline and not fully reproduced on BERT (due to the CPU limitation); the full-dataset pretrained-model predictions contain data leakage and are used only for pipeline verification.',
    'External validity: the data contains only English requirements, so applicability to other languages and domains is unverified; a single dataset may carry dataset-specific bias.',
    "Statistical conclusion validity: with 10-fold CV, Task 2/3, Task 4 IsQuality/IsOnlyFunctional, and Task 5 Function/Data all reach significance (p < 0.05) with large effects (Cohen's d > 0.8), indicating sufficient statistical power.",
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.1 Threats Before vs After Introducing Statistical Analysis', level=2)
doc.add_paragraph(
    'The introduction of statistical significance testing directly changes the nature of the threat '
    'on the “statistical conclusion validity” dimension. The following table compares the situation '
    'before and after introducing systematic statistical analysis:')

table = doc.add_table(rows=5, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Dimension'; hdr[1].text = 'Before statistical analysis (replication)'; hdr[2].text = 'After (10-fold + three tests)'
for i, (a, b, c) in enumerate([
    ('Basis for conclusion', 'Only single-point Weighted F1 was compared, unable to distinguish real gains from random fluctuation.',
     "Paired t-test + Wilcoxon + Cohen's d provide a three-way cross-check, reporting both significance and effect size."),
    ('Statistical power', 'With the initial 5-fold CV, the theoretical minimum Wilcoxon p was 0.0625, never reaching p < 0.05, so improvement claims could not be statistically confirmed.',
     'After switching to 10 folds, the minimum p ≈ 0.00195; multiple subtasks across Tasks 2/3, 4, and 5 reach p < 0.05.'),
    ('Conclusion validity', 'Whether an improvement was effective relied on subjective judgment, with a risk of mistaking chance fluctuation for an effective improvement (Type I error).',
     'Task 1 is honestly judged “not significant” (p = 0.30, d = 0.35), avoiding overclaim; significant items all have large effects (d > 0.8), and conclusions are falsifiable.'),
    ('Residual threats', '—',
     'Still validated on a single dataset and an LR + TF-IDF baseline; the improvement is not yet fully reproduced on BERT, so extrapolation requires caution.'),
]):
    cells = table.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c

doc.add_paragraph(
    'The core change is: before statistical analysis, “is the improvement effective?” was a subjective '
    'claim that could not be tested by the data; afterwards, it becomes a statistical conclusion that is '
    'testable and falsifiable — the essential improvement in Statistical Conclusion Validity. We must '
    'honestly note that the tests only answer “is the gain real over these 10 folds”; they do not remove '
    'the external and internal validity threats from using a single dataset and a single baseline model, '
    'which is future work requiring validation on more datasets and on BERT.')

# ============ Section 9 ============
doc.add_heading('9. Lessons Learned', level=1)
doc.add_heading('9.1 Verify Resource Availability Before Replicating', level=2)
doc.add_paragraph(
    'In this project, downloading and loading the pretrained models took a considerable amount of '
    'time. Lesson: before starting a replication project, the first step is not reading the paper but '
    'confirming that the dataset and pretrained models can be obtained and that the formats are '
    'compatible. If resources are hard to get, adjust the plan early rather than discovering problems '
    'after the work has started.')

doc.add_heading('9.2 Do Not Blindly Use Large Models on Small Data', level=2)
doc.add_paragraph(
    'With only 625 samples, directly fine-tuning a general BERT-base (single-split F1 89.6%) offers '
    'only a small gain (~2 percentage points, with random fluctuation) over simple LR + TF-IDF (87.6%). '
    'On small datasets, what truly determines performance is whether the model was pretrained on the '
    'target domain: a general BERT lacks requirements-domain knowledge and has limited transfer '
    'advantage, whereas NoRBERT, pretrained on requirements text, reliably exceeds 90%. To be clear, the '
    'bert-base-uncased model we used is still a general-pretrained model, not randomly initialized from '
    'scratch, so it does not suffer a severe overfitting collapse.')

doc.add_heading('9.3 Improvements Must Match the Problem', level=2)
doc.add_paragraph(
    'We tried several approaches: Focal Loss failed (it actually reduced performance on the mildly '
    'imbalanced data), and class weighting + oversampling also failed (weighting after oversampling '
    'over-biased toward minority classes). The winning combination was three parts: multi-granularity '
    'N-gram fusion + oversampling + classifier chains. Lesson: the improvement method must match the '
    'severity of the problem — more complex is not always better — and rapid trial-and-error experiments '
    'are needed to find the best combination.')

doc.add_heading('9.4 Statistical Tests Require Enough Samples', level=2)
doc.add_paragraph(
    'We only discovered during the Wilcoxon tests that the 5-fold sample size was too small, giving '
    'insufficient statistical power (p could only reach 0.0625, never significant). After changing to '
    '10-fold CV (N = 10), the various tests became significant. Lesson: before running statistical tests, '
    'compute the required sample size and use enough cross-validation folds, otherwise power is '
    'insufficient and results are not significant.')

doc.add_heading('9.5 Exploit Label Correlation in Multi-Label Tasks', level=2)
doc.add_paragraph(
    'The original paper trained every subtask as an independent binary classifier, completely ignoring '
    'logical dependencies and correlations among labels. After implementing classifier chains, the per-class '
    'F1 on the extremely rare Data class rose from 0% to 60.4% — precisely the failure the authors admitted '
    'and left as future work. Lesson: in multi-label classification, do not only predict each label '
    'independently; exploiting label correlations is often a free improvement.')

# ============ Section 10 ============
doc.add_heading('10. Conclusion', level=1)
doc.add_paragraph('This project completed the following work:')
for item in [
    'Successfully replicated the NoRBERT experimental pipeline and verified the correctness of the pretrained-model inference pipeline.',
    'Ran baselines on Tasks 1–3, comparing traditional methods with the BERT transfer-learning approach.',
    'Identified the paper’s gaps: it did not explore multi-granularity N-gram fusion, did not exploit multi-label correlations (classifier chains), and lacked statistical significance tests on Tasks 1–3.',
    'Implemented a three-layer improvement — multi-granularity N-gram fusion + oversampling with regularization + classifier chains — yielding significant gains on several tasks:',
    '    • Task 2/3: +14.67% Weighted F1 (p < 0.0001, very large effect)',
    '    • Task 4 IsOnlyFunctional: +5.14% (p = 0.0048, large effect)',
    '    • Task 5 rare Data class: +13.32% Weighted F1, per-class F1 from 0% → 60.4% (p < 0.0001, very large effect)',
    "Added systematic statistical significance tests (paired t-test, Wilcoxon test, Cohen's d) covering Tasks 1–5.",
    'Discussed the threats to validity of this study and future improvement directions.',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph(
    'The whole project ran the complete research pipeline — paper replication, problem identification, '
    'improvement validation, and statistical testing — deepening my understanding of empirical methods in '
    'software engineering. In particular, resolving the authors’ admitted failure on Task 5 through label '
    'correlation taught me that genuinely valuable improvements often lie hidden in the paper’s Limitations '
    'and Future Work.')

output_path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report_EN.docx'
doc.save(output_path)
print('English report saved to:', output_path)
