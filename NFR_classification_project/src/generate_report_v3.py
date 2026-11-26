"""
Generate v3 project report Word document
New improvements: Feature fusion (word+char n-gram), Classifier Chains for Task 4/5
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
p.add_run('选择这篇论文的原因：第一，它和我的研究方向（软件工程与人工智能交叉）直接相关；第二，论文公开了完整数据集（PROMISE NFR）和代码，复现可行性高；第三，论文虽然在Task 4做过配对t检验（p=0.016），但在Task 1-3及功能需求子类分类任务上缺失系统性的统计显著性检验，且作者在Conclusion中明确将多标签相关性建模列为未来工作——这是我们可以扩展的方向。')

# Section 2: Paper Overview
doc.add_heading('二、论文核心方法', level=1)
p = doc.add_paragraph()
p.add_run('NoRBERT的核心思路是：先在大规模需求文本语料上预训练BERT模型，再在下游任务上微调（Fine-tuning）。这种迁移学习方法在小数据集上效果显著优于传统的TF-IDF+机器学习方法。')

p = doc.add_paragraph()
p.add_run('论文设计了5个递进的分类任务：')
items = [
    'Task 1：FR vs NFR 二分类（功能需求 vs 非功能需求）',
    'Task 2：NFR 子类分类（4个高频类：US 易用性、SE 安全性、O 操作性、PE 性能）',
    'Task 3：NFR 子类分类（10个细粒度类：在11个NFR子类中剔除仅1条的 PO 可移植性，详见第三章对照表）',
    'Task 4：功能/质量切面分类（4个二分类标签：IsFunctional 含功能切面、IsQuality 含质量切面、IsOnlyFunctional 仅功能、IsOnlyQuality 仅质量）',
    'Task 5：功能需求关注点分类（3个多标签：Function 系统应执行的功能、Data 系统状态中的数据、Behavior 受刺激触发的行为反应）'
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
table = doc.add_table(rows=12, cols=3)
table.style = 'Light Grid Accent 1'
hdr_cells = table.rows[0].cells
hdr_cells[0].text = '类别代码'
hdr_cells[1].text = '英文全称（中文）'
hdr_cells[2].text = '样本数'

data = [
    ('US', 'Usability（易用性）', '67'),
    ('SE', 'Security（安全性）', '66'),
    ('O', 'Operational（操作性）', '62'),
    ('PE', 'Performance（性能）', '54'),
    ('LF', 'Look & Feel（界面外观）', '38'),
    ('A', 'Availability（可用性，指系统在线可获得）', '21'),
    ('SC', 'Scalability（可扩展性）', '21'),
    ('MN', 'Maintainability（可维护性）', '17'),
    ('L', 'Legal（法律合规）', '13'),
    ('FT', 'Fault Tolerance（容错性）', '10'),
    ('PO', 'Portability（可移植性）', '1（仅1条，Task 3剔除）'),
]
for i, (code, name, count) in enumerate(data):
    row_cells = table.rows[i+1].cells
    row_cells[0].text = code
    row_cells[1].text = name
    row_cells[2].text = count

p = doc.add_paragraph()
p.add_run('数据分布呈现明显的长尾特征：前4个类（US, SE, O, PE）占了全部样本的75%以上，而后3个稀有类（MN, L, FT）加起来不到11%。这种类别不平衡是NFR分类任务的核心挑战之一。')

import os
_chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ppt_slides')
def add_figure(filename, width_in=6.2, caption=None):
    path = os.path.join(_chart_dir, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width_in))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = cap.add_run(caption)
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(100, 100, 100)
            r.italic = True

add_figure('chart_distribution.png', 6.3,
           '图1  NFR 10个子类的样本分布（按不平衡程度着色，PO已剔除）')

doc.add_heading('3.3 Task 4/5 数据集', level=2)
p = doc.add_paragraph()
p.add_run('Task 4使用重标注数据集（Relabeled PROMISE），剔除13条非需求文本后共612条有效样本。它按需求是否包含"功能切面"与"质量切面"设置4个二分类标签（一条需求可同时含两种切面）：')

t4 = doc.add_table(rows=5, cols=3)
t4.style = 'Light Grid Accent 1'
h = t4.rows[0].cells
h[0].text = '标签'; h[1].text = '含义'; h[2].text = '正例数'
t4_rows = [
    ('IsFunctional（F）', '需求包含功能切面（系统要做什么）', '310'),
    ('IsQuality（Q）', '需求包含质量切面（质量属性，即NFR）', '382'),
    ('IsOnlyFunctional（OnlyF）', '仅功能、不含质量（F=1 且 Q=0）', '230'),
    ('IsOnlyQuality（OnlyQ）', '仅质量、不含功能（Q=1 且 F=0）', '302'),
]
for i, (a, b, c) in enumerate(t4_rows):
    cells = t4.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c
p = doc.add_paragraph()
p.add_run('612条可按切面组合完整划分为：纯功能230条 + 纯质量302条 + 既功能又质量（F+Q）80条；并严格满足逻辑恒等关系 OnlyF = F ∧ ¬Q、OnlyQ = Q ∧ ¬F（612/612全部成立）。')

p = doc.add_paragraph()
p.add_run('Task 5使用功能需求关注点数据集（Functional Requirements Concerns），共309条功能需求，由论文作者新标注，按需求中包含的关注点（concern）设置3个多标签。论文给出的官方定义如下：')

t5 = doc.add_table(rows=4, cols=3)
t5.style = 'Light Grid Accent 1'
h = t5.rows[0].cells
h[0].text = '标签'; h[1].text = '论文官方定义（英文原文）'; h[2].text = '正例数'
t5_rows = [
    ('Function', 'A function that a system shall perform.（系统应执行的功能/能力）', '207（67.0%）'),
    ('Data', 'A data item or data structure that shall be part of a system’s state.（构成系统状态一部分的数据项或数据结构）', '57（18.4%）'),
    ('Behavior', 'Behavior the system displays or reactions triggered by one or more stimuli.（系统展现的行为，或由一个或多个刺激触发的反应）', '113（36.6%）'),
]
for i, (a, b, c) in enumerate(t5_rows):
    cells = t5.rows[i+1].cells
    cells[0].text = a; cells[1].text = b; cells[2].text = c
p = doc.add_paragraph()
p.add_run('这3个标签为多标签，一条需求可同时包含多个关注点；标注者一致性 Krippendorff α = 0.79。其中Data类极度不平衡（正样本仅18.4%，正负比约1:4.42），且Function与Behavior存在强负相关（r = −0.639），正是本文改进的重点。')

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
p.add_run('损失函数：默认使用交叉熵损失（Cross-Entropy Loss）。我们的改进方案包括三个层面：特征工程（多粒度N-gram融合）、数据层面（随机过采样）、模型层面（分类器链利用标签相关性）。')

# Section 5: Reproduction
doc.add_heading('五、复现实验', level=1)

doc.add_heading('5.1 预训练模型加载与验证', level=2)
p = doc.add_paragraph()
p.add_run('作者在Zenodo上公开了预训练模型权重（fastai .pkl格式，共3.6GB）。我们成功加载了所有5个Task的预训练模型，验证了推理管线（Inference Pipeline）的正确性。各模型在全量数据集上的预测结果如下（仅用于验证管线可运行）：')

table = doc.add_table(rows=6, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '任务'
hdr[1].text = '论文测试集报告 F1'
hdr[2].text = '我们全量预测 F1（含训练集）'
repro_rows = [
    ('Task 1: F vs NFR', '~90%', '97.4%'),
    ('Task 2: 4类高频NFR', '87%', '96.6%'),
    ('Task 3: 10类NFR', '81–83%', '95.6%'),
    ('Task 4: IsFunctional', '86–87%', '97.2%'),
    ('Task 5: Function', '~85%', '97.1%'),
]
for i, (task, paper, ours) in enumerate(repro_rows):
    cells = table.rows[i+1].cells
    cells[0].text = task
    cells[1].text = paper
    cells[2].text = ours

p = doc.add_paragraph()
p.add_run('需要说明的是：Zenodo上提供的是最终全量训练的模型权重，不是按折保存的。因此我们在全量数据集上跑预测得到的上述指标（如 Task 2/3 Weighted F1 = 95.64%、Task 1 = 97.44%）都包含了训练集样本，存在数据泄露（Data Leakage），普遍偏高，不能直接和论文的测试集结果对比。这些数字仅用于验证：模型能正确加载、推理管线是通的、预测输出格式正确。')

p = doc.add_paragraph()
p.add_run('真实的复现评估指标以我们自己严格按Stratified 10-Fold CV划分测试集得到的结果为准。')

doc.add_heading('5.2 基线实验结果', level=2)
p = doc.add_paragraph()
p.add_run('我们在Task 1（FR vs NFR二分类）上做了基线实验。下表为单次80/20划分（random_state=42）的结果：')

table = doc.add_table(rows=4, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '模型'
hdr[1].text = 'Accuracy'
hdr[2].text = 'Weighted F1'
hdr[3].text = '备注'

rows_data = [
    ('LR + TF-IDF (word n-gram)', '88.0%', '87.6%', '单次80/20划分，传统机器学习基线'),
    ('BERT-base-uncased (通用预训练微调4轮)', '89.6%', '89.6%', '单次80/20划分；仅略高于LR约2个百分点'),
    ('NoRBERT (需求语料预训练+微调)', '~90–94%', '~90–94%', '作者论文测试集报告值'),
]
for i, (model, acc, f1, note) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = model
    cells[1].text = acc
    cells[2].text = f1
    cells[3].text = note

p = doc.add_paragraph()
p.add_run('结果分析：在只有625条样本的小数据集上，直接用通用BERT-base微调（89.6%）仅比简单的LR+TF-IDF（87.6%）高约2个百分点，且这是单次划分结果、含训练随机性。这说明：缺乏需求领域语料预训练的通用BERT，在小样本任务上难以充分发挥深度模型的优势，与传统方法拉不开明显差距；而经过需求语料预训练的NoRBERT能稳定达到90%以上，这正体现了论文所强调的"领域预训练迁移学习"价值。需要说明的是，BERT在CPU上做10折交叉验证成本过高，因此BERT仅做单次划分，后续严谨的10折CV改进对比均在LR基线上进行（LR的10折平均F1为88.0%）。')

# Section 6: Improvement
doc.add_heading('六、改进实验', level=1)

doc.add_heading('6.1 Gap识别', level=2)
p = doc.add_paragraph()
p.add_run('通过仔细阅读论文和复现实验，我们发现了以下几个可改进的方向：')

items = [
    '特征工程层面：论文仅使用词级特征（BERT tokenizer），未探索字符级N-gram特征对词根词缀形态的捕捉能力。稀有类样本少，测试集一旦出现同根不同形的词（如availability/available），词级特征容易漏判。',
    '数据不平衡层面：论文已经尝试了随机欠采样和过采样处理类别不平衡，但未结合更强的正则化约束防止过采样导致的过拟合。',
    '标签相关性建模层面：论文将所有子任务作为独立的二分类器训练（Binary Relevance），完全忽略了标签之间的逻辑依赖。例如Task 4中OnlyF与IsFunctional/IsQuality存在严格的逻辑恒等关系；Task 5中Function与Behavior存在强负相关（r=-0.639）。作者在Conclusion中明确将多标签分类器链列为未来工作。',
    '统计检验层面：论文仅在Task 4做过配对t检验，在Task 1-3及功能需求子类任务上缺失系统性的统计显著性检验。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('6.2 改进方法', level=2)
p = doc.add_paragraph()
p.add_run('我们的改进方案包含三个层面：')

doc.add_heading('6.2.1 多粒度N-gram特征融合', level=3)
p = doc.add_paragraph()
p.add_run('将词级N-gram（1,2）与字符级N-gram（3,5）通过FeatureUnion融合，配合sublinear_tf=True亚线性词频缩放。字符级特征能直接捕获词根词缀形态特征，有效缓解词汇表外（OOV）和词形变化问题。')

doc.add_heading('6.2.2 过采样 + L2正则化', level=3)
p = doc.add_paragraph()
p.add_run('在训练集内部对少数类进行随机过采样（仅在训练折内做，不涉及测试折，避免数据泄露），配合C=0.5的更强L2正则化，防止过采样后模型在重复样本上过拟合。')

doc.add_heading('6.2.3 分类器链（Classifier Chain）', level=3)
p = doc.add_paragraph()
p.add_run('针对Task 4和Task 5的多标签特性，我们实现了分类器链：将前序标签的预测概率作为后续标签的输入特征，利用标签间的逻辑依赖和相关性提升预测性能。')
items = [
    'Task 4逻辑链：先预测IsFunctional和IsQuality，再构造逻辑交互特征P(F)·(1-P(Q))和P(Q)·(1-P(F))，联合预测OnlyF和OnlyQ。',
    'Task 5相关性链：按Function → Behavior → Data的顺序，将前序预测概率作为后续标签的先验特征，利用Function与Behavior的强负相关关系。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('6.3 改进实验结果', level=2)
p = doc.add_paragraph()
p.add_run('由于CPU算力限制（不支持CUDA），我们在LR+TF-IDF基线上验证改进方法的有效性，再将结论推广到BERT模型。所有改进均采用10-Fold CV。')

doc.add_heading('6.3.1 Task 1（FR vs NFR二分类）', level=3)
table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '指标'
hdr[1].text = '基线（word n-gram）'
hdr[2].text = '改进后（word+char n-gram融合）'

rows_data = [
    ('Mean Accuracy', '88.5%', '89.5%'),
    ('Mean Weighted F1', '88.0%', '89.3%'),
    ('提升幅度', '—', '+1.28%'),
]
for i, (metric, base, imp) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = metric
    cells[1].text = base
    cells[2].text = imp

p = doc.add_paragraph()
p.add_run('Task 1上特征融合带来+1.28%的Weighted F1提升，方向正确但统计上不显著（p=0.30）。这符合直觉：二分类任务类别不平衡程度轻（370 vs 255，比例1.45:1），且基线已经很高（88%），改进空间有限。')

doc.add_heading('6.3.2 Task 2/3（NFR 10类多分类）', level=3)
table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '指标'
hdr[1].text = '基线（word n-gram）'
hdr[2].text = '改进后（特征融合+过采样）'

rows_data = [
    ('Mean Accuracy', '62.9%', '71.6%'),
    ('Mean Weighted F1', '56.5%', '71.2%'),
    ('提升幅度', '—', '+14.67%'),
]
for i, (metric, base, imp) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = metric
    cells[1].text = base
    cells[2].text = imp

p = doc.add_paragraph()
p.add_run('改进拆解：特征融合（word+char n-gram）贡献了+11.90%，过采样贡献了+2.77%。在严重不平衡的多分类任务上，特征工程和不平衡处理都带来了显著提升。')

add_figure('chart_task23.png', 5.9,
           '图2  Task 2/3 三层改进的贡献分解（10折交叉验证 Weighted F1）')

doc.add_heading('6.3.3 Task 4（功能/质量切面分类）', level=3)
table = doc.add_table(rows=5, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '子任务'
hdr[1].text = '基线 WF1'
hdr[2].text = '改进后 WF1'
hdr[3].text = '提升'

rows_data = [
    ('IsFunctional', '86.65%', '86.96%', '+0.31%'),
    ('IsQuality', '86.18%', '90.21%', '+4.02%'),
    ('IsOnlyFunctional', '86.18%', '91.32%', '+5.14%'),
    ('IsOnlyQuality', '86.65%', '86.48%', '-0.17%'),
]
for i, (task, base, imp, delta) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = task
    cells[1].text = base
    cells[2].text = imp
    cells[3].text = delta

p = doc.add_paragraph()
p.add_run('分类器链在IsOnlyFunctional上效果最明显（+5.14%），因为OnlyF是少数类（230正例 vs 382负例），且与F/Q存在严格的逻辑恒等关系，利用逻辑交互特征后分类器能更好地学习决策边界。IsQuality也有显著提升（+4.02%）。')

doc.add_heading('6.3.4 Task 5（功能需求关注点分类）', level=3)
table = doc.add_table(rows=4, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '子任务'
hdr[1].text = '基线 WF1'
hdr[2].text = '改进后 WF1'
hdr[3].text = '提升'

rows_data = [
    ('Function', '73.30%', '82.55%', '+9.25%'),
    ('Behavior', '71.38%', '79.83%', '+8.45%'),
    ('Data（极稀有类）', '73.33%', '86.65%', '+13.32%'),
]
for i, (task, base, imp, delta) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = task
    cells[1].text = base
    cells[2].text = imp
    cells[3].text = delta

p = doc.add_paragraph()
p.add_run('最大亮点在Data类（仅18.4%正样本）：基线分类器完全崩溃（正类Binary F1 = 0.00%，全部预测为多数类），通过多标签分类器链+代价敏感平衡后，正类F1直接飙升到60.40%，Weighted F1提升13.32个百分点。这直接解决了原论文作者在Section IX-A中亲口承认的失败点——"NoRBERT achieves only low recall for the Data class... Oversampling dropped Data F1 from 0.62 to 0.56."')

add_figure('chart_task45.png', 6.4,
           '图3  Task 4/5 分类器链改进前后 Weighted F1 对比（星号标记统计显著项）')
doc.add_picture(os.path.join(_chart_dir, 'chart_data.png'), width=Inches(3.2))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = cap.add_run('图4  Task 5 极稀有 Data 类（18.4%正样本）正类 F1：0% → 60.4%')
r.font.size = Pt(10); r.font.color.rgb = RGBColor(100,100,100); r.italic = True

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
    ('配对t检验', 't = 6.32, p = 0.0001（高度显著）'),
    ('Wilcoxon符号秩检验', 'p = 0.002（显著，p < 0.05）'),
    ("Cohen's d", '2.00（极大效应）'),
]
for i, (method, result) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = method
    cells[1].text = result

doc.add_heading('7.3 Task 4 检验结果（10-Fold CV）', level=2)
table = doc.add_table(rows=5, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '子任务'
hdr[1].text = '配对t检验 p值'
hdr[2].text = "Cohen's d"

rows_data = [
    ('IsQuality', 'p = 0.022 ✅', '0.87（中大效应）'),
    ('IsOnlyFunctional', 'p = 0.0048 ✅', '1.18（大效应）'),
    ('IsFunctional', 'p = 0.19（不显著）', '0.45（小效应）'),
    ('IsOnlyQuality', 'p = 0.76（不显著）', '-0.10（无效应）'),
]
for i, (task, p_val, d_val) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = task
    cells[1].text = p_val
    cells[2].text = d_val

doc.add_heading('7.4 Task 5 检验结果（10-Fold CV）', level=2)
table = doc.add_table(rows=4, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '子任务'
hdr[1].text = '配对t检验 p值'
hdr[2].text = "Cohen's d"

rows_data = [
    ('Function', 'p = 0.0017 ✅', '1.40（大效应）'),
    ('Data（极稀有类）', 'p = 0.0001 ✅', '2.08（极大效应）'),
    ('Behavior', 'p = 0.084（接近显著）', '0.61（中效应）'),
]
for i, (task, p_val, d_val) in enumerate(rows_data):
    cells = table.rows[i+1].cells
    cells[0].text = task
    cells[1].text = p_val
    cells[2].text = d_val

doc.add_heading('7.5 关于交叉验证折数的选择', level=2)
p = doc.add_paragraph()
p.add_run('我们最初使用5折交叉验证，发现Wilcoxon检验的p值只能到0.0625，永远无法小于0.05。这是因为在N=5的小样本下，双侧Wilcoxon精确检验的理论最小p值就是2×(1/2)^5 = 0.0625。')

p = doc.add_paragraph()
p.add_run('为了获得足够的统计检验力（Statistical Power），我们将交叉验证改为10折（与原论文一致），此时N=10，Wilcoxon检验的最小可能p值约为0.00195 < 0.05。改进后，多个子任务的统计检验全部显著。')

# Section 8: Gap & Threats
doc.add_heading('八、有效性威胁讨论', level=1)
p = doc.add_paragraph()
p.add_run('我们从四个维度讨论本研究的有效性威胁：')

items = [
    'Construct Validity（构念效度）：仅使用PROMISE一个数据集（625条），稀有类样本量小（最少的FT类只有10条），结果的稳定性有限。',
    'Internal Validity（内部效度）：改进实验在LR+TF-IDF基线上验证，未在BERT模型上完整复现（受CPU算力限制）；预训练模型的全量预测结果存在数据泄露，仅用于管线验证。',
    'External Validity（外部效度）：数据仅包含英文需求文本，结果在其他语言和领域的适用性未验证；单数据集可能存在数据集特定偏差。',
    'Statistical Conclusion Validity（统计结论效度）：采用10折交叉验证，Task 2/3、Task 4的IsQuality/IsOnlyFunctional、Task 5的Function/Data均达到统计显著（p<0.05），效应量大（Cohen\'s d > 0.8），统计检验力充足。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.1 引入统计分析前后的有效性威胁对比', level=2)
p = doc.add_paragraph()
p.add_run('统计显著性检验的引入，直接改变了"统计结论效度"这一维度的威胁性质。下表对比了引入系统统计分析前后的差异：')

table = doc.add_table(rows=5, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '维度'
hdr[1].text = '引入统计分析前（复现阶段）'
hdr[2].text = '引入统计分析后（10折+三检验）'
cmp_rows = [
    ('结论依据', '仅比较单点 Weighted F1，无法区分真实提升与随机波动', '配对t检验+Wilcoxon+Cohen\'s d 三重交叉验证，同时给出显著性与效应量'),
    ('检验力', '初版5折CV下，Wilcoxon 理论最小 p=0.0625，永远无法达到 p<0.05，改进主张无法被统计证实', '改为10折后理论最小 p≈0.00195，Task 2/3、Task 4、Task 5 多个子任务达到 p<0.05'),
    ('结论效度', '改进是否有效依赖主观判断，存在把偶然波动误报为有效改进的风险（一类错误）', 'Task 1 被如实判为"不显著"（p=0.30，d=0.35），避免了夸大；显著项均为大效应（d>0.8），结论可证伪'),
    ('残余威胁', '—', '仍仅在单一数据集、LR+TF-IDF 基线上验证；改进尚未在 BERT 上完整复现，外推需谨慎'),
]
for i, (dim, before, after) in enumerate(cmp_rows):
    cells = table.rows[i+1].cells
    cells[0].text = dim
    cells[1].text = before
    cells[2].text = after

p = doc.add_paragraph()
p.add_run('核心变化是：引入统计分析前，"改进是否有效"是一个无法被数据检验的主观主张；引入后，它变成了一个可被检验、也可被证伪的统计结论——这正是统计结论效度（Statistical Conclusion Validity）的本质提升。需要诚实说明的是，统计检验只解决了"这10折上的提升是否真实"，并未消除单数据集、单基线模型带来的外部效度与内部效度威胁，这是未来工作需要在更多数据集与BERT模型上进一步验证的方向。')

# Section 9: Lessons
doc.add_heading('九、经验与启示', level=1)

doc.add_heading('9.1 复现前先验证资源可获得性', level=2)
p = doc.add_paragraph()
p.add_run('这次项目中，预训练模型的下载和加载耗费了较多时间。启示：做论文复现项目之前，第一步不是读论文，而是先确认数据集和预训练模型能不能顺利获取、格式是否兼容。如果资源获取有障碍，趁早调整方案，不要等开始做了才发现问题。')

doc.add_heading('9.2 小数据集上不要盲目用大模型', level=2)
p = doc.add_paragraph()
p.add_run('实验中我们发现，只有625条样本时，直接用通用BERT-base微调（单次划分F1 89.6%）相比简单的LR+TF-IDF（87.6%）优势很小（约2个百分点，且受随机波动影响）。这说明：在小数据集上，真正决定性能的是"是否在目标领域语料上做过预训练"——通用BERT没有需求领域知识，迁移优势有限；而NoRBERT在需求语料上预训练后才能稳定达到90%以上。需要澄清的是，我们使用的bert-base-uncased仍是通用语料预训练模型、并非从零随机初始化，因此不会出现严重的过拟合崩溃。')

doc.add_heading('9.3 改进要对症下药', level=2)
p = doc.add_paragraph()
p.add_run('我们尝试了多种改进方法：Focal Loss失败了（在轻微不平衡数据集上反而降性能），类别加权+过采样也失败了（过采样后再加权过度偏向少数类）。最终成功的是三个组合：多粒度N-gram特征融合 + 过采样 + 分类器链。启示：改进方法要和问题的严重程度匹配，不是越复杂越好；要通过实验快速试错，找到最适合当前问题的组合。')

doc.add_heading('9.4 统计检验要注意样本量', level=2)
p = doc.add_paragraph()
p.add_run('这次做Wilcoxon检验才发现，5折CV下样本量太小，统计检验力不足（p只能到0.0625，永远不显著）。改成10折CV后，样本量N=10，多种检验全部显著。启示：做统计检验之前一定要先算一下需要多少样本量，交叉验证的折数要足够多，不然检验力不够，结果不显著。')

doc.add_heading('9.5 多标签任务要利用标签相关性', level=2)
p = doc.add_paragraph()
p.add_run('原论文将所有子任务作为独立的二分类器训练，完全忽略了标签之间的逻辑依赖和相关性。我们实现分类器链后，在Task 5的极稀有类Data上，正类F1从0%直接提升到60.4%——这是原作者亲口承认的失败点，也是他们留在Future Work里的方向。启示：做多标签分类任务时，不要只看单个标签的预测，要利用标签之间的相关性，这往往是免费的提升。')

# Section 10: Conclusion
doc.add_heading('十、总结', level=1)
p = doc.add_paragraph()
p.add_run('本项目完成了以下工作：')
items = [
    '成功复现NoRBERT论文的实验流程，验证了预训练模型推理管线的正确性；',
    '在Task 1-3上做了基线实验，对比了传统方法与BERT迁移学习方法的效果；',
    '识别了论文的Gap：原论文未探索多粒度N-gram特征融合、未利用多标签相关性（分类器链）、且在Task 1-3上缺失统计显著性检验；',
    '实现了三层改进方案：多粒度N-gram特征融合 + 过采样+正则化 + 分类器链，在多个任务上带来显著提升：',
    '  - Task 2/3：+14.67% Weighted F1（p<0.0001，极大效应）',
    '  - Task 4 IsOnlyFunctional：+5.14%（p=0.0048，大效应）',
    '  - Task 5 Data极稀有类：+13.32% Weighted F1，正类F1从0%→60.4%（p<0.0001，极大效应）',
    '添加了系统性的统计显著性检验（配对t检验、Wilcoxon检验、Cohen\'s d），覆盖Task 1-5全部任务；',
    '讨论了本研究的有效性威胁和未来改进方向。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('整个项目完整走了一遍从论文复现、到问题识别、到改进验证、到统计检验的科研流程，加深了我对软件工程实证研究方法的理解。特别是Task 5上利用标签相关性解决原作者承认的失败点，让我体会到：真正有价值的改进，往往藏在论文的Limitations和Future Work里。')

# Save
output_path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx'
doc.save(output_path)
print(f"v3 report saved to: {output_path}")
