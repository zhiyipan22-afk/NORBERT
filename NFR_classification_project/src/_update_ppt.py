"""
Extract and modify slide XML for updating PPT
"""
import re

# Read current XML
with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\current.xml", 'r', encoding='utf-8') as f:
    xml = f.read()

# Extract each slide
slides = re.findall(r'<slide id="([^"]+)">(.*?)</slide>', xml, re.DOTALL)

# Find slides we need to modify
target_slides = ['peE', 'peO', 'peQ']
slide_dict = {sid: content for sid, content in slides if sid in target_slides}

print("Found slides:", list(slide_dict.keys()))

# === Modify peE (Dataset Distribution) ===
pee = slide_dict['peE']
# Fix FR/NFR counts (they were reversed)
pee = pee.replace('Functional (F): 370 samples', 'Functional (F): 255 samples')
pee = pee.replace('Non-Functional (NFR): 255 samples', 'Non-Functional (NFR): 370 samples')

# Save peE
with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\peE_new.xml", 'w', encoding='utf-8') as f:
    f.write(f'<slide id="peE">{pee}</slide>')
print("peE saved")

# === Modify peO (Improvement Results) ===
peo = slide_dict['peO']
# Update subtitle: 5-fold -> 10-fold
peo = peo.replace('5-fold stratified cross-validation: Baseline LR vs Improved LR + Weighting + Oversampling',
                  '10-fold stratified cross-validation: Baseline LR vs Improved LR + Oversampling + Regularization')
# Update numbers
peo = peo.replace('>60.5%<', '>63.1%<')
peo = peo.replace('>70.3%<', '>71.8%<')
peo = peo.replace('>54.6%<', '>57.1%<')
peo = peo.replace('>69.5%<', '>71.2%<')
peo = peo.replace('>+14.9%<', '>+14.1%<')
# Update statistical tests
peo = peo.replace('Paired t-test: t = 8.91, p = 0.0009', 'Paired t-test: t = 8.96, p < 0.0001')
peo = peo.replace('Wilcoxon test: p = 0.0625', 'Wilcoxon test: p = 0.002')
peo = peo.replace("Cohen&apos;s d: 4.45 (large effect)", "Cohen&apos;s d: 2.83 (large effect)")
# Update key finding
peo = peo.replace('Standard classifiers achieve only 54.6% weighted F1, heavily biased toward majority classes. By combining class-weighted loss with minority class oversampling, we improve weighted F1 by 14.9 percentage points',
                  'Standard classifiers achieve only 57.1% weighted F1, heavily biased toward majority classes. By combining minority class oversampling with stronger L2 regularization, we improve weighted F1 by 14.1 percentage points')

# Save peO
with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\peO_new.xml", 'w', encoding='utf-8') as f:
    f.write(f'<slide id="peO">{peo}</slide>')
print("peO saved")

# === Modify peQ (Statistical Significance) ===
peq = slide_dict['peQ']
# Update subtitle: 5-fold -> 10-fold
peq = peq.replace('5-fold stratified cross-validation + paired t-test + Wilcoxon test:',
                  '10-fold stratified cross-validation + paired t-test + Wilcoxon test:')

# Save peQ
with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\peQ_new.xml", 'w', encoding='utf-8') as f:
    f.write(f'<slide id="peQ">{peq}</slide>')
print("peQ saved")

print("\nDone! Modified slides saved.")
