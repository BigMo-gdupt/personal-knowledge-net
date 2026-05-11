---
tags: [深度学习, Transformer, 时间序列预测, PatchTST]
date: 2026-05-07
source_refs: [PatchTST]
---

PatchTST（Patch Time Series Transformer）是一种针对多变量时间序列预测的 Transformer 架构，通过引入 Patching（分块）和 Channel-independence（通道独立）两个关键设计，使标准 Transformer 能够有效处理时间序列数据，在长期预测任务上超越线性模型和其他 Transformer 变体。

## 数学/逻辑推导

给定长度为 $L$ 的单变量时间序列，Patching 使用滑动窗口将其分割为约 $N \approx L/S$ 个 Patch，其中 $P$ 为 Patch 长度，$S$ 为步长。

输入 Token 数量从 $L$ 减少到 $N$，注意力计算复杂度从 $O(L^2)$ 降低到 $O(N^2) = O((L/S)^2)$。

对于 $M$ 个通道的多变量时间序列，Channel-independence 将其视为 $M$ 个独立的单变量序列，共享 Transformer 权重但独立前向传播：

$$\hat{x}_{i,t+1:t+H} = f_\theta(\text{Patch}(x_{i,1:t}))$$

其中 $f_\theta$ 为共享的 Transformer 主干，$i$ 为通道索引。

## 前提条件与适用边界

### 前提条件

1. 时间序列具有局部模式（趋势、周期性等），单个时间点缺乏独立语义
2. 多变量通道间相关性较弱或存在异质性
3. 需要利用较长历史窗口进行预测

### 适用边界

1. 在长期预测任务上表现优异，优于 DLinear 等线性模型
2. 支持自监督预训练（Masked Patch 重建）
3. 对通道间强相关的时间序列，可能不如通道混合方法

## [关联拓扑]

- [[Patching（分块机制）]]：PatchTST 的核心技术
- [[Channel-independence（通道独立）]]：PatchTST 的架构设计
- [[点级注意力问题]]：PatchTST 解决的核心动机
