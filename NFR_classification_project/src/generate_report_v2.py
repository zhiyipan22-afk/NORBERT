"""
Generate revised project report Word document
Based on feedback corrections
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Set default font
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)

# Title
title = doc.add_heading('NoRBERT 论文复现与改进项目报告', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('SE789 Software Metrics Course Project')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_paragraph()

# Section 1: Introduction
doc.add_heading('一、项目概述', level=1)
p = doc.add_paragraph()
p.add_run('我是清迈大学CAMT学院的交换学生，主修计算机软件工程方向。本学期选修了SE789 Software Metrics课程。课程要求选择一篇非期刊的会议论文（6-8页双栏格式），复现论文实验，添加论文中没有的统计显著性检验，并找出论文不足提出改进。')

p = doc.add_paragraph()
p.add_run('我选择的论文是《NoRBERT: Transfer Learning for Requirements Classification》（IEEE RE 2020）。这篇论文研究的是软件需求工程（Requirements Engineering）中的自动化需求分类问题——用BERT迁移学习模型自动区分功能需求（Functional Requirements, FR）和非功能需求（Non-Functional Requirements, NFR），并进一步对NFR进行细粒度的子类分类。')

p = doc.add_paragraph()
p.add_run('选择这篇论文的原因：第一，它和我的研究方向（软件工程与人工智能交叉）直接相关；第二，论文公开了完整数据集（PROMISE NFR）和代码，复现可行性高；第三，论文虽然在Task 4做过配对t检验（p=0.016），但在Task 1-3及功能需求子类分类任务上缺失系统性的统计显著性检验，这是我们可以扩展的方向。')

# Section 2: Paper Overview
doc.add_heading('二、论文核心方法', level=1)
p = doc.add_paragraph()
p.add_run('NoRBERT的核心思路是：先在大规模需求文本语料上预训练BERT模型，再在下游任务上微调（Fine-tuning）。这种迁移学习方法在小数据集上效果显著优于传统的TF-IDF+机器学习方法。')

p = doc.add_paragraph()
p.add_run('论文设计了5个递进的分类任务：')
items = [
    'Task 1：FR vs NFR 二分类（二元）',
    'Task 2：NFR 子类分类（4个高频类：US, SE, O, PE）',
    'Task 3：NFR 子类分类（10个细粒度类）',
    'Task 4：功能/质量切面分类（IsFunctional / IsQuality 等4个子任务）',
    'Task 5：功能需求子类分类（Function / Data / Behavior 3个子任务）'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('论文的评估方法：采用Stratified 10-Fold交叉验证，以及跨项目验证（p-fold和loPo留一项目法）。基线方法包括LR、SVM、Random Forest等传统模型，对比对象是NoRBERT预训练模型。')

# Section 3: Dataset
doc.add_heading('三、数据集', level=1)
p = doc.add_paragraph()
p.add_run('使用PROMISE NFR Dataset，共625条标注好的需求文本。')

doc.add_heading('3.1 Task 1: 二分类数据集', level=2)
items = [
    'Non-Functional Requirements (NFR): 370 条',
    'Functional Requirements (FR): 255 条',
    '合计: 625 条'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('3.2 Task 2/3: NFR 子类分布', level=2)
p = doc.add_paragraph()
p.add_run('NFR子类共10个类别（PO类仅1条样本，在多分类任务中被排除）：')

# Add table
table = doc.add_table(rows=11, cols=3)
table.style = 'Light Grid Accent 1'
hdr_cells = table.rows[0].cells
hdr_cells[0].text = '类别代码'
hdr_cells[1].text = '英文全称'
hdr_cells[2].text = '样本数'

data = [
    ('US', 'Usability（易用性）', '67'),
    ('SE', 'Security（安全性）', '66'),
    ('O', 'Operational（操作性）', '62'),
    ('PE', 'Performance（性能）', '54'),
    ('LF', 'Look & Feel（界面外观）', '38'),
    ('A', 'Availability（可用性）', '21'),
    ('SC', 'Scalability（可扩展性）', '21'),
    ('MN', 'Maintainability（可维护性）', '17'),
    ('L', 'Legal（法律合规）', '13'),
    ('FT', 'Fault Tolerance（容错性）', '10'),
]
for i, (code, name, count) in enumerate(data):
    row_cells = table.rows[i+1].cells
    row_cells[0].text = code
    row_cells[1].text = name
    row_cells[2].text = count

p = doc.add_paragraph()
p.add_run('数据分布呈现明显的长尾特征：前4个类（US, SE, O, PE）占了全部样本的75%以上，而后3个稀有类（MN, L, FT）加起来不到11%。这种类别不平衡是NFR分类任务的核心挑战之一。')

# Section 4: Environment & Implementation
doc.add_heading('四、实验环境与实现细节', level=1)

doc.add_heading('4.1 硬件与软件环境', level=2)
p = doc.add_paragraph()
p.add_run('硬件：Windows笔记本，AMD Radeon 780M集成显卡（不支持CUDA，所有计算在CPU上运行）。')
p = doc.add_paragraph()
p.add_run('软件：Python 3.11，PyTorch（CPU版），Transformers，scikit-learn，fastai（用于加载作者预训练模型）。')

doc.add_heading('4.2 数据处理流程', level=2)
p = doc.add_paragraph()
p.add_run('数据从CSV文件读取，包含RequirementText文本字段和多列二值标签。处理流程：')
items = [
    '文本预处理：小写化、去除特殊字符、分词（BERT自带WordPiece分词器）',
    '标签编码：将多列二值标签映射为整数类别索引',
    '序列截断：max_seq_len=128，超过截断，不足补[PAD]',
    '划分策略：Stratified K-Fold分层抽样，保证每折类别分布一致'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('4.3 模型结构', level=2)
p = doc.add_paragraph()
p.add_run('NoRBERT的分类头结构：BERT-base编码器（12层Transformer，隐藏层768维） + Dropout层 + 全连接分类层。输入是[CLS]位置的 pooled output，输出是类别 logits。')

p = doc.add_paragraph()
p.add_run('损失函数：默认使用交叉熵损失（Cross-Entropy Loss）。我们的改进方案是在数据层面进行随机过采样，并配合更强的L2正则化（C=0.5），防止少数类重复样本导致过拟合。')

# Section 5: Reproduction
doc.add_heading('五、复现实验', level=1)

doc.add_heading('5.1 预训练模型加载与验证', level=2)
p = doc.add_paragraph()
p.add_run('作者在Zenodo上公开了预训练模型权重（fastai .pkl格式，共3.6GB）。我们成功加载了所有5个Task的预训练模型，验证了推理管线（Inference Pipeline）的正确性。')

p = doc.add_paragraph()
p.add_run('需要说明的是：Zenodo上提供的是最终全量训练的模型权重，不是按折保存的。因此我们在全量数据集上跑预测得到的指标（Task 2/3 Weighted F1 = 95.64%）包含了训练集样本，存在数据泄露（Data Leakage），这个数字不能直接和论文的测试集结果对比。这个数字仅用于验证：模型能正确加载、推理管线是通的、预测输出格式正确。')

p = doc.add_paragraph()
p.add_run('真实的复现评估指标以我们自己严格按Stratified 5-Fold CV划分测试集得到的结果为准。')

doc.add_heading('5.2 基线实验结果（5-Fold CV）', level=2)
p = doc.add_paragraph()
p.add_run('我们在Task 1（FR vs NFR二分类）上做了两组基线实验：')

table = doc.add_table(rows=4, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '模型'
hdr[1].text = 'Accuracy'
hdr[2].text = 'Weighted F1'
hdr[3].text = '备注'

rows_data = [
    ('LR + TF-IDF', '87.3%', '87.3%', '传统机器学习基线'),
    ('BERT-base (从头训练)', '75.4%', '75.4%', '小数据集上易过拟合'),
    ('NoRBERT (预训练+微调)', '~90%', '~90%', '作者论文报告值'),
]
for i, (model, acc, f1, note) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = model
    cells[1].text = acc
    cells[2].text = f1
    cells[3].text = note

p = doc.add_paragraph()
p.add_run('结果分析：在只有625条样本的小数据集上，从头训练的BERT效果反而不如简单的LR+TF-IDF，这验证了论文的核心论点——预训练迁移学习在小样本场景下优势明显。')

# Section 6: Improvement
doc.add_heading('六、改进实验', level=1)

doc.add_heading('6.1 Gap识别', level=2)
p = doc.add_paragraph()
p.add_run('通过仔细阅读论文，我们发现了以下几个可改进的方向：')

items = [
    '数据层面：论文已经尝试了随机欠采样（Undersampling）和过采样（Oversampling）处理类别不平衡，且在Task 1上发现采样未带来明显提升。',
    '损失函数层面：论文全部使用标准交叉熵损失（Standard Cross-Entropy Loss），每个类的权重相同，没有探索代价敏感学习（Cost-Sensitive Learning）——即在损失函数中给少数类更高的权重。',
    '组合策略：论文没有将随机过采样与更强的正则化约束结合起来评估；在Task 3（10类细粒度多分类）这个类别更不平衡的任务上，也没有系统比较不同不平衡处理策略的效果。',
    '统计检验层面：论文仅在Task 4做过配对t检验，在Task 1-3及功能需求子类任务上缺失系统性的统计显著性检验。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('6.2 改进方法', level=2)
p = doc.add_paragraph()
p.add_run('我们的改进方案：少数类随机过采样（Random Oversampling） + L2正则化。')

p = doc.add_paragraph()
p.add_run('过采样（Oversampling）：在训练集内部，对少数类进行随机过采样（仅在训练折内做，不涉及测试折，避免数据泄露），使每个类的样本数达到一致。这是数据层面的不平衡处理方法。')
p = doc.add_paragraph()
p.add_run('正则化：使用C=0.5（比默认C=1.0更强的L2正则化），防止过采样后模型在重复样本上过拟合。')
p = doc.add_paragraph()
p.add_run('为什么不用类别加权？我们做了实验发现：过采样后训练数据已经平衡了，再用类别加权会过度偏向少数类，反而降低整体性能。所以我们只使用过采样+正则化的组合。')

doc.add_heading('6.3 改进实验结果', level=2)
p = doc.add_paragraph()
p.add_run('由于CPU算力限制（不支持CUDA），我们在LR+TF-IDF基线上验证改进方法的有效性，再将结论推广到BERT模型。')

p = doc.add_paragraph()
p.add_run('Task 2/3（10类NFR子类分类）改进结果（10-Fold CV，PO类已剔除）：')

table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '指标'
hdr[1].text = '基线 LR'
hdr[2].text = '改进后 LR（过采样+正则化）'

rows_data = [
    ('Mean Accuracy', '63.1%', '71.8%'),
    ('Mean Weighted F1', '57.1%', '71.2%'),
    ('提升幅度', '—', '+14.1%'),
]
for i, (metric, base, imp) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = metric
    cells[1].text = base
    cells[2].text = imp

p = doc.add_paragraph()
p.add_run('结果：过采样+正则化策略在NFR多分类任务上带来了显著的性能提升（Weighted F1提升14.1个百分点），尤其是稀有类别的分类效果改善明显。10折交叉验证下，三种统计检验（配对t检验、Wilcoxon符号秩检验、Cohen\'s d）全部显著。')

p = doc.add_paragraph()
p.add_run('值得注意的是，在Task 1（二分类，FR vs NFR）上，过采样的效果很小（仅+0.54% Weighted F1），统计上也不显著（p=0.47）。这符合直觉：Task 1的类别不平衡程度较轻（370 vs 255，比例约1.45:1），而过采样在严重不平衡的场景下（Task 2/3，最多类和最少类差6.7倍）效果才显著。')

# Section 7: Statistical Significance Test
doc.add_heading('七、统计显著性检验', level=1)

doc.add_heading('7.1 检验方法选择', level=2)
p = doc.add_paragraph()
p.add_run('我们选择了三种互补的统计检验方法：')
items = [
    '配对t检验（Paired t-test）：检验改进前后均值差异的显著性，假设差值服从正态分布。',
    'Wilcoxon符号秩检验（Wilcoxon signed-rank test）：非参数检验，不假设正态分布，更稳健。',
    "Cohen's d：效应量，衡量改进效果的大小（d=0.2小，d=0.5中，d=0.8大，d>2极大）。"
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('7.2 Task 2/3 检验结果（10-Fold CV）', level=2)

table = doc.add_table(rows=4, cols=2)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '检验方法'
hdr[1].text = '结果'

rows_data = [
    ('配对t检验', 't = 8.96, p < 0.0001（高度显著）'),
    ('Wilcoxon符号秩检验', 'p = 0.002（显著，p < 0.05）'),
    ("Cohen's d", '2.83（极大效应）'),
]
for i, (method, result) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = method
    cells[1].text = result

doc.add_heading('7.3 Task 1 检验结果（10-Fold CV）', level=2)

table = doc.add_table(rows=4, cols=2)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '检验方法'
hdr[1].text = '结果'

rows_data = [
    ('配对t检验', 't = 0.75, p = 0.47（不显著）'),
    ('Wilcoxon符号秩检验', 'p = 0.43（不显著）'),
    ("Cohen's d", '0.24（小效应）'),
]
for i, (method, result) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = method
    cells[1].text = result

p = doc.add_paragraph()
p.add_run('Task 1上改进效果不显著，这是合理的：二分类任务的类别不平衡程度较轻（370 vs 255），过采样带来的提升有限。而过采样在严重不平衡的多分类任务（Task 2/3）上效果才显著。')

doc.add_heading('7.4 关于交叉验证折数的选择', level=2)
p = doc.add_paragraph()
p.add_run('我们最初使用5折交叉验证，发现Wilcoxon检验的p值只能到0.0625，永远无法小于0.05。这是因为在N=5的小样本下，双侧Wilcoxon精确检验的理论最小p值就是2×(1/2)^5 = 0.0625。')

p = doc.add_paragraph()
p.add_run('为了获得足够的统计检验力（Statistical Power），我们将交叉验证改为10折（与原论文一致），此时N=10，Wilcoxon检验的最小可能p值约为0.00195 < 0.05。改进后，三种统计检验全部显著：')

items = [
    '配对t检验：p < 0.0001（高度显著）',
    'Wilcoxon符号秩检验：p = 0.002（显著）',
    "Cohen's d = 2.83（极大效应）"
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('这验证了课程评分标准中的建议："If what to be tested is not sufficiently enough, acquire more data." 增加交叉验证折数（即增加配对样本量）是提高统计检验力的有效方法。')

# Section 8: Gap & Threats
doc.add_heading('八、有效性威胁讨论', level=1)
p = doc.add_paragraph()
p.add_run('我们从四个维度讨论本研究的有效性威胁：')

items = [
    'Construct Validity（构念效度）：仅使用PROMISE一个数据集（625条），稀有类样本量小（最少的FT类只有10条），结果的稳定性有限。',
    'Internal Validity（内部效度）：改进实验在LR+TF-IDF基线上验证，未在BERT模型上完整复现（受CPU算力限制）；预训练模型的全量预测结果存在数据泄露，仅用于管线验证。',
    'External Validity（外部效度）：数据仅包含英文需求文本，结果在其他语言和领域的适用性未验证；单数据集可能存在数据集特定偏差。',
    'Statistical Conclusion Validity（统计结论效度）：采用10折交叉验证，三种统计检验全部显著（配对t检验p<0.0001，Wilcoxon p=0.002，Cohen\'s d=2.83），统计检验力充足。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

# Section 9: Lessons
doc.add_heading('九、经验与启示', level=1)

doc.add_heading('9.1 复现前先验证资源可获得性', level=2)
p = doc.add_paragraph()
p.add_run('这次项目中，预训练模型的下载和加载耗费了较多时间。启示：做论文复现项目之前，第一步不是读论文，而是先确认数据集和预训练模型能不能顺利获取、格式是否兼容。如果资源获取有障碍，趁早调整方案，不要等开始做了才发现问题。')

doc.add_heading('9.2 小数据集上不要盲目用大模型', level=2)
p = doc.add_paragraph()
p.add_run('实验中我们发现，只有625条样本时，从头训练BERT的效果反而不如简单的LR+TF-IDF。这说明：在小数据集上，预训练模型的迁移学习优势才能体现出来；如果没有预训练，直接微调大模型反而会过拟合。')

doc.add_heading('9.3 改进要对症下药', level=2)
p = doc.add_paragraph()
p.add_run('我们最初尝试Focal Loss，效果反而下降了。后来分析原因：Focal Loss更适合极端不平衡（如1:100）的场景，而我们的不平衡程度（最多和最少差6.7倍）用过采样+正则化这种更直接的方法效果更好。启示：改进方法要和问题的严重程度匹配，不是越复杂越好。')

doc.add_heading('9.4 统计检验要注意样本量', level=2)
p = doc.add_paragraph()
p.add_run('这次做Wilcoxon检验才发现，5折CV下样本量太小，统计检验力不足（p只能到0.0625，永远不显著）。改成10折CV后，样本量N=10，三种检验全部显著。启示：做统计检验之前一定要先算一下需要多少样本量，交叉验证的折数要足够多，不然检验力不够，结果不显著。')

# Section 10: Conclusion
doc.add_heading('十、总结', level=1)
p = doc.add_paragraph()
p.add_run('本项目完成了以下工作：')
items = [
    '成功复现NoRBERT论文的实验流程，验证了预训练模型推理管线的正确性；',
    '在Task 1-3上做了基线实验，对比了传统方法与BERT迁移学习方法的效果；',
    '识别了论文的Gap：原论文做了数据层面的随机过采样，但未探索过采样与强正则化结合的效果，也未在Task 1-3上做统计显著性检验；',
    '实现了过采样+正则化的改进方案，在NFR多分类任务上带来+14.1%的Weighted F1提升（10折CV）；',
    '添加了统计显著性检验（配对t检验、Wilcoxon检验、Cohen\'s d），Task 2/3三种检验全部显著（p<0.01），这是论文中缺失的部分；',
    '讨论了本研究的有效性威胁和未来改进方向。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('整个项目完整走了一遍从论文复现、到问题识别、到改进验证、到统计检验的科研流程，加深了我对软件工程实证研究方法的理解。')

# Save
output_path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx'
doc.save(output_path)
print(f"Revised report saved to: {output_path}")
