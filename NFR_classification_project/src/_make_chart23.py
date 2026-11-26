import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'

# Task 2/3 three-stage improvement
fig, ax = plt.subplots(figsize=(7.6, 3.8), dpi=150)
stages = ['Word n-gram\n(baseline)', 'Word + Char\nN-gram fusion', 'Feature fusion\n+ Oversampling']
f1 = [56.50, 68.40, 71.16]
colors = ['#9E9E9E', '#5B9BD5', '#1565C0']
bars = ax.bar(stages, f1, color=colors, width=0.55, edgecolor='white')
for b, v in zip(bars, f1):
    ax.text(b.get_x()+b.get_width()/2, v+0.8, f'{v:.2f}%', ha='center', fontsize=12, fontweight='bold')
# gain arrows
ax.annotate('', xy=(1, 68.4), xytext=(1, 60), arrowprops=dict(arrowstyle='->', color='#C62828'))
ax.text(1, 63.5, '+11.9%', ha='center', fontsize=10, color='#C62828')
ax.set_ylabel('Weighted F1 (%)', fontsize=12)
ax.set_title('Task 2/3: Contribution of Each Improvement Layer (10-fold CV)', fontsize=12.5, fontweight='bold')
ax.set_ylim(0, 82)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.35)
plt.tight_layout()
out = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\chart_task23.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
print('saved', out)
