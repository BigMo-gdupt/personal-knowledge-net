---
tags: [深度学习, Transformer, 时间序列, Token化]
date: 2026-05-07
source_refs: [PatchTST]
---

Patching（分块机制）是将时间序列分割为子序列（Patches）的技术，每个 Patch 包含连续的多个时间点。该方法解决了单个时间点缺乏语义意义的问题，同时大幅降低 Transformer 的计算复杂度。

## 数学/逻辑推导

给定长度为 $L$ 的时间序列 $x = [x_1, x_2, \ldots, x_L]$，设定 Patch 长度为 $P$，步长为 $S$，生成 $N$ 个 Patch：

$$\text{Patch}_i = [x_{i \cdot S + 1}, x_{i \cdot S + 2}, \ldots, x_{i \cdot S + P}]$$

其中 $N \approx \lfloor (L - P) / S \rfloor + 1$。

计算复杂度降低：
- 原始：$O(L^2)$（$L$ 个 Token）
- Patching 后：$O(N^2) = O((L/S)^2)$

当 $S = P/2$（50% 重叠）时，Token 数量减少约 $S$ 倍，计算量减少约 $S^2$ 倍。

## 前提条件与适用边界

### 前提条件

1. 时间序列具有局部模式（趋势、周期、形状）
2. Patch 长度 $P$ 应与局部模式尺度匹配
3. 步长 $S$ 决定 Patch 间重叠程度

### 适用边界

1. 适用于具有局部语义的时间序列（如传感器数据、金融数据）
2. 不适用于每个时间点独立同分布的序列（如白噪声）
3. Patch 长度需调参：太短无法捕捉语义，太长丢失细节

## [关联拓扑]

- [[PatchTST模型]]：Patching 的代表性应用
- [[Channel-independence（通道独立）]]：与 Patching 配合使用
- [[点级注意力问题]]：Patching 解决的核心问题
