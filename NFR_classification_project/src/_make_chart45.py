import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'

# Task 4/5 Weighted F1 results
labels = ['F4:F', 'F4:Q', 'F4:OnlyF', 'F4:OnlyQ', 'F5:Function', 'F5:Behavior', 'F5:Data']
base = [86.65, 86.18, 86.18, 86.65, 73.30, 71.38, 73.33]
imp = [86.96, 90.21, 91.32, 86.48, 82.55, 79.83, 86.65]
sig = ['ns', 'p=.022', 'p=.005', 'ns', 'p=.002', 'p=.084', 'p<.001']

x = np.arange(len(labels))
w = 0.38

fig, ax = plt.subplots(figsize=(8.2, 4.0), dpi=150)
b1 = ax.bar(x - w/2, base, w, label='Baseline (independent LR)', color='#9E9E9E', edgecolor='white')
b2 = ax.bar(x + w/2, imp, w, label='Improved (classifier chain + balancing)', color='#1565C0', edgecolor='white')

ax.set_ylabel('Weighted F1 (%)', fontsize=12)
ax.set_title('Task 4 & 5: Classifier Chains Improve Weighted F1 (10-fold CV)', fontsize=12.5, fontweight='bold', pad=10)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10.5, rotation=12)
ax.set_ylim(60, 98)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.35)
ax.legend(fontsize=9.5, loc='upper right', frameon=False)

# annotate significant improvements
for i in range(len(labels)):
    if sig[i] != 'ns':
        ax.annotate('*', xy=(x[i]+w/2, imp[i]+0.6), ha='center', fontsize=15, color='#C62828', fontweight='bold')
        ax.text(x[i]+w/2, imp[i]+2.6, sig[i], ha='center', fontsize=7.5, color='#C62828')

plt.tight_layout()
out = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\chart_task45.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
print('saved', out)

# Second chart: Data class per-class F1 (the headline result)
fig2, ax2 = plt.subplots(figsize=(3.8, 3.6), dpi=150)
bars = ax2.bar(['Baseline', 'Improved'], [0, 60.4], color=['#9E9E9E', '#E76F51'], width=0.55, edgecolor='white')
ax2.set_ylabel('Data class per-class F1 (%)', fontsize=11)
ax2.set_title('Task 5 rare Data class\n(18.4% positives)', fontsize=11.5, fontweight='bold')
ax2.set_ylim(0, 75)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', linestyle='--', alpha=0.35)
for bar, v in zip(bars, [0, 60.4]):
    ax2.text(bar.get_x()+bar.get_width()/2, v+1.5, f'{v:.1f}%', ha='center', fontsize=13, fontweight='bold')
plt.tight_layout()
out2 = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\chart_data.png'
plt.savefig(out2, dpi=150, bbox_inches='tight', facecolor='white')
print('saved', out2)
