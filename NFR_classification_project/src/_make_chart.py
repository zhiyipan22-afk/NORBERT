import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Use a clean sans-serif font (English labels)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#888888'

# Data (PO excluded, 10 classes)
classes = ['US', 'SE', 'O', 'PE', 'LF', 'A', 'SC', 'MN', 'L', 'FT']
counts = [67, 66, 62, 54, 38, 21, 21, 17, 13, 10]
full_names = ['Usability', 'Security', 'Operational', 'Performance',
              'Look & Feel', 'Availability', 'Scalability',
              'Maintainability', 'Legal', 'Fault Tolerance']

# Color by imbalance tier
colors = []
for c in counts:
    if c >= 50:
        colors.append('#1565C0')      # majority - blue
    elif c >= 20:
        colors.append('#5B9BD5')      # medium - light blue
    elif c >= 13:
        colors.append('#F4A261')      # minority - orange
    else:
        colors.append('#E76F51')      # rare - red

fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=150)
bars = ax.bar(range(len(classes)), counts, color=colors, width=0.72, edgecolor='white')

ax.set_xticks(range(len(classes)))
ax.set_xticklabels(classes, fontsize=12)
ax.set_ylabel('Number of requirements', fontsize=12)
ax.set_title('NFR Subclass Distribution (PO excluded, 369 samples, 10 classes)', fontsize=12.5, fontweight='bold', pad=10)
ax.set_ylim(0, 78)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.35)

for bar, n in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, n + 1.2, str(n),
            ha='center', va='bottom', fontsize=10.5, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend = [
    Patch(facecolor='#1565C0', label='Majority (>=50)'),
    Patch(facecolor='#5B9BD5', label='Medium (20-49)'),
    Patch(facecolor='#F4A261', label='Minority (13-19)'),
    Patch(facecolor='#E76F51', label='Rare (<=10)'),
]
ax.legend(handles=legend, loc='upper right', fontsize=9, frameon=False, ncol=2)

plt.tight_layout()
out = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\chart_distribution.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
print('saved', out)
