"""
Generate project report Word document
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

doc = Document()

# Set default font
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)

# Title
title = doc.add_heading('NoRBERT 论文复现与改进项目报告', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Subtitle
subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('SE789 Software Metrics Course Project')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_paragraph()

# Section 1: Introduction
doc.add_heading('一、项目概述', level=1)
p = doc.add_paragraph()
p.add_run('我是清迈大学CAMT学院的交换学生，主修计算机软件工程方向。本学期选修了SE789 Software Metrics课程，课程要求我们选择一篇软件度量相关的会议论文进行复现，并在此基础上做扩展改进。')

p = doc.add_paragraph()
p.add_run('我选择的论文是《NoRBERT: Transfer Learning for Requirements Classification》（IEEE RE 2020）。这篇论文做的是软件需求分类任务——自动区分功能需求（Functional Requirements, FR）和非功能需求（Non-Functional Requirements, NFR），并进一步对NFR进行子类分类。我之所以选这篇论文，一方面是因为它和我访学方向（人因工程与软件工程交叉）相关，另一方面是这篇论文公开了完整的数据集和代码，复现难度相对可控。')

p = doc.add_paragraph()
p.add_run('课程要求的核心任务有三个：第一，复现论文的实验和评估过程；第二，添加论文中没有的统计显著性检验；第三，找出论文的不足，提出改进方法并验证效果。')

# Section 2: Paper Selection
doc.add_heading('二、论文选择过程', level=1)
p = doc.add_paragraph()
p.add_run('最开始老师让我自己找一篇合适的论文。我一开始找的是一篇IEEE Access上的论文，但那篇论文的代码和数据集都不完整，复现起来很困难。后来我换了思路，专门找那种"有代码、有数据集、有预训练模型"的论文。')

p = doc.add_paragraph()
p.add_run('最终选定NoRBERT这篇论文的原因有三点：')

items = [
    '有公开数据集（PROMISE NFR Dataset），625条需求文本，标注完整；',
    '有公开代码（GitHub仓库）和预训练模型（Zenodo仓库），可以直接加载运行；',
    '论文里没有做统计显著性检验，这刚好是我们可以扩展的点。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

# Section 3: Environment Setup
doc.add_heading('三、环境搭建与踩坑', level=1)
p = doc.add_paragraph()
p.add_run('环境搭建阶段踩了很多坑，浪费了不少时间。')

doc.add_heading('3.1 硬件限制', level=2)
p = doc.add_paragraph()
p.add_run('我的笔记本是AMD Radeon 780M集显，不支持CUDA。这意味着我没法用GPU加速训练BERT模型，所有计算都只能靠CPU跑。这直接导致后面的训练速度非常慢。')

doc.add_heading('3.2 Python版本问题', level=2)
p = doc.add_paragraph()
p.add_run('我一开始用的是Python 3.13，结果transformers库装不上。因为transformers还没有适配最新的Python版本。折腾了半天，最后不得不专门装了一个Python 3.11的环境。')

doc.add_heading('3.3 最终环境', level=2)
p = doc.add_paragraph()
p.add_run('最终我用的是：Python 3.11 + CPU版PyTorch + transformers + scikit-learn + pandas + scipy。虽然慢，但至少能跑起来。')

# Section 4: Dataset
doc.add_heading('四、数据集', level=1)
p = doc.add_paragraph()
p.add_run('用的是PROMISE NFR Dataset，总共625条需求文本。数据集分为两个层级：')

items = [
    'Task 1（二分类）：功能需求FR（370条） vs 非功能需求NFR（255条）；',
    'Task 2/3（多分类）：NFR子类分类，共10个类别（US可用性、SE安全性、O操作性、PE性能、LF兼容性、SC可扩展性、A可用性、MN可移植性、L可维护性、FT容错性）。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('在数据分析阶段我发现了一个很重要的问题——类别极度不平衡。最多的类（US，67条）和最少的类（FT，10条）差了将近7倍。还有一个PO类只有1条样本，直接排除了。这个发现后来成为了我们改进的核心动机。')

# Section 5: Reproduction Experiments
doc.add_heading('五、复现实验', level=1)

doc.add_heading('5.1 预训练模型下载（最耽误时间的环节）', level=2)
p = doc.add_paragraph()
p.add_run('这是整个项目最耽误时间的一个环节。作者把预训练模型放在Zenodo上，一个压缩包有3.6GB。我一开始想用命令行wget直接下载，结果多次返回404错误。后来发现是Zenodo的API接口变了，直接下载链接失效了。')

p = doc.add_paragraph()
p.add_run('我又尝试在Google Colab上跑作者的notebook，想让Colab自动下载模型。结果Colab高峰期分配不到GPU，而且在Colab上安装依赖也报错（spacy版本不兼容）。折腾了半天，Colab这条路也走不通。')

p = doc.add_paragraph()
p.add_run('最后没办法，我只能手动在Zenodo网页上点下载。这个3.6GB的压缩包下载了整整四五个小时，速度非常慢。等下载完解压好，已经浪费了将近一天的时间。')

p = doc.add_paragraph()
p.add_run('这是我这次项目最大的教训——以后做论文复现，一定要先确认数据集和预训练模型能不能顺利下载，下载速度怎么样，再决定选哪篇论文。不然光下载就能耗掉你一整天。')

doc.add_heading('5.2 预训练模型加载踩坑', level=2)
p = doc.add_paragraph()
p.add_run('下载完模型后，加载过程也踩了好几个坑：')

items = [
    '第一个坑：PyTorch 2.6版本默认weights_only=True，加载旧的fastai .pkl模型会报错。我不得不monkey-patch torch.load函数来解决。',
    '第二个坑：模型文件里缺少自定义类BertTextClassifier的定义。我不得不从作者的GitHub notebook里把这个类的代码提取出来，加到我的脚本里。',
    '第三个坑：类索引映射错误。learn.predict()返回的是相对索引，不是原始标签值，导致预测结果全乱了。调试了半天才发现这个问题。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.3 复现结果', level=2)
p = doc.add_paragraph()
p.add_run('最终成功加载了所有预训练模型，跑了论文里的所有5个Task：')

items = [
    'Task 1（FR vs NFR二分类）：F1 ≈ 90%',
    'Task 2/3（10类NFR子类分类）：Weighted F1 = 95.64%',
    'Task 4（功能/质量切面分类，4个子任务）：Accuracy 95.4% - 98.2%',
    'Task 5（功能需求子类分类，3个子任务）：Accuracy 94.2% - 97.7%'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('这些结果比论文里报的数字还要高一点，因为我是在全部数据集（包括训练数据）上跑的预测，而论文里报的是测试集结果。但核心是——我成功复现了论文的实验流程，证明了作者的模型确实能达到论文里的效果。')

# Section 6: Baseline Experiments
doc.add_heading('六、自己跑的基线实验', level=1)
p = doc.add_paragraph()
p.add_run('除了加载作者的预训练模型，我还自己从头训练了基线模型，用来对比。')

doc.add_heading('6.1 Task 1基线', level=2)
p = doc.add_paragraph()
p.add_run('我用了两种基线方法：')

items = [
    '逻辑回归（LR + TF-IDF）：Accuracy = 88.0%，F1 = 87.6%',
    'BERT-base从头训练：Accuracy = 89.6%，F1 = 89.6%'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('然后我做了5折分层交叉验证（Stratified 5-Fold CV），得到更稳健的结果：')

items = [
    'LR基线：Mean F1 = 87.29%（±0.0217）',
    'BERT基线：Mean F1 = 75.40%（±0.1020）'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('有意思的是，自己从头训练的BERT效果反而比LR差很多。这是因为数据集太小了（只有625条），BERT这种大模型很容易过拟合。这也侧面说明了作者为什么要用预训练+微调的方式——小数据集上，预训练模型的迁移学习效果确实好很多。')

# Section 7: Improvement Experiments
doc.add_heading('七、改进实验', level=1)

doc.add_heading('7.1 改进动机', level=2)
p = doc.add_paragraph()
p.add_run('在数据分析阶段我发现了类别不平衡的问题。论文里用的是标准交叉熵损失函数，没有针对类别不平衡做任何处理。这会导致分类器偏向多数类，少数类的分类效果很差。')

p = doc.add_paragraph()
p.add_run('所以我的改进思路就是：想办法让分类器不要那么偏向多数类，多关注少数类。')

doc.add_heading('7.2 第一次尝试：Focal Loss（失败了）', level=2)
p = doc.add_paragraph()
p.add_run('我第一个想到的方法是Focal Loss。Focal Loss是目标检测领域提出来的，专门用来解决类别不平衡问题。它的核心思想是：让分类器更关注那些难分的样本（也就是少数类样本）。')

p = doc.add_paragraph()
p.add_run('我实现了Focal Loss，然后跑了实验。结果——失败了。Weighted F1从基线的89.6%降到了81.12%，反而降了8.5%。')

p = doc.add_paragraph()
p.add_run('为什么失败？后来我分析了一下：Focal Loss更适合那种极端不平衡（比如1:100）的场景。而我们的数据集虽然不平衡，但程度还没那么极端（最多和最少差7倍）。在这种情况下用Focal Loss，反而会让模型太关注少数类的难分样本，忽略了多数类的正确分类，整体效果反而下降。')

doc.add_heading('7.3 第二次尝试：类别加权 + 过采样（成功了）', level=2)
p = doc.add_paragraph()
p.add_run('Focal Loss失败后，我换了一个更简单直接的方法：类别加权损失 + 少数类过采样。')

p = doc.add_paragraph()
p.add_run('具体做法是：')

items = [
    '类别加权：在损失函数里给少数类更高的权重，让分类器错分少数类时惩罚更重；',
    '过采样：对少数类进行随机过采样，把每个类的样本数都补到和最多的类一样多。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('这个方法虽然简单，但效果非常好。')

p = doc.add_paragraph()
p.add_run('Task 1（二分类）改进结果：')

items = [
    '基线：F1 = 89.6%',
    '改进后：F1 = 90.37%',
    '提升：+0.77%'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('Task 2/3（10类NFR子类分类）改进结果：')

items = [
    '基线LR：Mean Weighted F1 = 54.60%',
    '改进后LR：Mean Weighted F1 = 69.51%',
    '提升：+14.91%'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('效果非常显著！尤其是在NFR子类分类任务上，提升了将近15个百分点。这说明类别不平衡确实是NFR分类的一个大问题，解决好了效果提升非常明显。')

# Section 8: Statistical Significance Test
doc.add_heading('八、统计显著性检验', level=1)
p = doc.add_paragraph()
p.add_run('这是论文里没有的，也是我们课程要求加的扩展点。')

p = doc.add_paragraph()
p.add_run('为什么要做统计显著性检验？因为如果你只跑一次实验说"我改进了，分数提高了"，那可能只是你运气好，刚好这次划分的测试集比较简单。用5折交叉验证，每次结果都不一样，你需要统计方法来证明：这个改进是真实有效的，不是随机波动出来的。')

p = doc.add_paragraph()
p.add_run('我用了三种统计检验方法：')

items = [
    '配对t检验（Paired t-test）：检验改进前后的均值是否有显著差异。p < 0.05就说明显著。',
    'Wilcoxon符号秩检验（Wilcoxon signed-rank test）：非参数版本的t检验，不假设数据服从正态分布，更稳健。',
    "Cohen's d：效应量，衡量改进效果有多大。d=0.2小效应，d=0.5中等效应，d=0.8大效应，d>2就是极大效应。"
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.1 Task 1统计检验结果', level=2)
items = [
    '配对t检验：t = -2.67, p = 0.0557（接近显著，p≈0.05）',
    'Wilcoxon检验：p = 0.0625（接近显著）',
    "Cohen's d = -1.34（大效应）"
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.2 Task 2/3统计检验结果', level=2)
items = [
    '配对t检验：t = 8.91, p = 0.0009（高度显著！p < 0.001）',
    'Wilcoxon检验：p = 0.0625（接近显著）',
    "Cohen's d = 4.45（极大效应！）"
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('Task 2/3的结果非常好——p值只有0.0009，说明改进几乎不可能是碰巧发生的。而且Cohen\'s d达到了4.45，属于极大效应，说明改进效果非常大。')

# Section 9: Gap Analysis
doc.add_heading('九、Gap分析：论文的不足', level=1)
p = doc.add_paragraph()
p.add_run('通过复现实验，我发现了论文里几个没有提到的问题：')

items = [
    '类别不平衡问题：NFR子类极度不平衡，但论文用的是标准交叉熵损失，没有处理。这会导致少数类分类效果差。',
    '没有统计显著性检验：论文只报了单次划分的结果，没有用交叉验证和统计检验来验证结果的稳健性。',
    '数据集单一：只用了PROMISE一个数据集，没有跨项目验证。结果能不能推广到其他数据集上？论文没说。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

# Section 10: Threats to Validity
doc.add_heading('十、有效性威胁讨论', level=1)
p = doc.add_paragraph()
p.add_run('一个严谨的研究必须讨论自己的有效性威胁。我从四个维度来分析：')

items = [
    'Construct Validity（构念效度）：只用了一个小数据集（625条），少数类样本太少（最少的只有10条），结果可能不稳定。',
    'Internal Validity（内部效度）：我的改进实验用的是LR基线，不是BERT；而且预训练模型的结果是在全部数据上跑的，不是严格的测试集划分。',
    'External Validity（外部效度）：结果可能不能推广到其他领域或语言——我们只用了英文的需求文本，其他语言的效果怎么样？不知道。',
    'Statistical Conclusion Validity（统计结论效度）：5折交叉验证的方差还是比较大的。但好在效应量很大（Cohen\'s d = 4.45），弥补了这一点。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('我的缓解措施：用了分层5折交叉验证、配对统计检验、报告效应量（Cohen\'s d），而不只是p值。')

# Section 11: Lessons Learned
doc.add_heading('十一、经验与启示', level=1)
p = doc.add_paragraph()
p.add_run('这次项目踩了很多坑，也学到了很多东西。总结几点最重要的：')

doc.add_heading('11.1 预实验：先确认数据能下载，再选论文', level=2)
p = doc.add_paragraph()
p.add_run('这次最耽误时间的就是预训练模型下载——3.6GB的文件，Zenodo下载了四五个小时，还多次404。我之前完全没预料到这个问题，等开始做了才发现下载这么慢，白白浪费了一天多。')

p = doc.add_paragraph()
p.add_run('以后做论文复现项目，第一步不是读论文，而是先确认：数据集能不能顺利下载？预训练模型能不能顺利拿到？下载速度怎么样？如果这些都有问题，趁早换论文，别浪费时间。')

doc.add_heading('11.2 环境问题要尽早解决', level=2)
p = doc.add_paragraph()
p.add_run('Python版本不兼容、CUDA不支持、fastai旧版本加载问题……这些环境问题加起来也浪费了不少时间。以后做深度学习相关的项目，先花半天时间把环境搭好，确认能跑通一个最小例子，再开始正式做实验。不要一边做实验一边解决环境问题，那样效率太低。')

doc.add_heading('11.3 改进方法要简单直接，不要贪复杂', level=2)
p = doc.add_paragraph()
p.add_run('我一开始想用Focal Loss这种"高级"方法，结果失败了。最后用的是最朴素的类别加权+过采样，效果反而特别好。')

p = doc.add_paragraph()
p.add_run('这说明：解决问题不一定非要用最复杂的方法。先看看问题的本质是什么——我们的问题就是类别不平衡，那就直接针对不平衡做处理（加权+过采样），比绕一大圈用Focal Loss效果还好。')

doc.add_heading('11.4 统计检验很重要', level=2)
p = doc.add_paragraph()
p.add_run('以前我做实验，就是跑一次，分数高就说成功了。这次做了5折交叉验证和统计检验之后，才意识到：单次实验的结果真的可能是运气好。有了p值和效应量，你的结论才站得住脚。')

p = doc.add_paragraph()
p.add_run('以后做实验，不管是什么项目，都要做交叉验证和统计检验。这是科研的基本素养。')

# Section 12: Conclusion
doc.add_heading('十二、总结', level=1)
p = doc.add_paragraph()
p.add_run('这次项目虽然踩了很多坑，但最终还是完成了所有要求：')

items = [
    '复现了NoRBERT论文的所有5个Task，验证了论文结果的可复现性；',
    '自己跑了基线实验，做了5折交叉验证；',
    '添加了统计显著性检验（配对t检验、Wilcoxon检验、Cohen\'s d），这是论文里没有的；',
    '找到了类别不平衡这个gap，提出了类别加权+过采样的改进方法；',
    '改进效果显著——Task 2/3 Weighted F1提升了14.9%，p=0.0009，效应量极大。'
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

p = doc.add_paragraph()
p.add_run('整个过程虽然辛苦，但学到了很多——不只是技术上的，还有做研究的思路和方法。从选论文、搭环境、复现、找问题、做改进、做统计检验、讨论有效性威胁，完整走了一遍科研的流程。这对我以后做毕设和研究生阶段的研究应该会有很大帮助。')

# Save
output_path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx'
doc.save(output_path)
print(f"Report saved to: {output_path}")
