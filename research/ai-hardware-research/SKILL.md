---
name: ai-hardware-research
description: "AI hardware research: chip architectures, automotive computing units, intelligent driving domain controllers — web search strategies, analysis templates, and key information sources."
version: 1.0.0
author: AI Hardware Researcher Profile
license: MIT
platforms: [linux, macos]
---

# AI Hardware Research

Comprehensive research methodology for AI chips, automotive computing, and intelligent driving domain controllers. Use this skill whenever the user asks about chip architectures, SoCs, domain controllers, ADAS/AD computing platforms, or autonomous driving hardware.

## When to Use

- "深度调研 NVIDIA Thor"
- "对比 Mobileye EyeQ6 vs 地平线 J6"
- "本周 AI 芯片动态"
- "车载域控技术趋势"
- "HBM4 进展"
- Any chip architecture or automotive computing question

## Key Information Sources

### Industry News & Analysis (搜中文用中文关键词)

| Source | URL | Type |
|--------|-----|------|
| AnandTech | https://www.anandtech.com | 芯片深度评测 |
| SemiAnalysis | https://www.semianalysis.com | 半导体分析 |
| ServeTheHome | https://www.servethehome.com | 服务器/数据中心硬件 |
| SemiEngineering | https://semiengineering.com | 半导体工程 |
| WikiChip | https://en.wikichip.org | 芯片架构数据库 |
| Hot Chips | https://www.hotchips.org | 顶会演讲 |
| IEEE Spectrum | https://spectrum.ieee.org | 技术新闻 |
| 车东西 | https://chedongxi.com | 中文自动驾驶/汽车电子 |
| 半导体行业观察 | https://www.semiinsights.com | 中文半导体深度 |
| 芯智讯 | https://www.icsmart.cn | 中文芯片产业 |

### Academic Papers

| Source | URL | Search Pattern |
|--------|-----|----------------|
| arXiv CS.AR | https://arxiv.org/list/cs.AR/recent | Architecture papers |
| arXiv CS.AI | https://arxiv.org/list/cs.AI/recent | AI systems |
| IEEE Xplore | https://ieeexplore.ieee.org | chip + accelerator |
| Google Scholar | https://scholar.google.com | chip architecture OR domain controller |
| ACM DL | https://dl.acm.org | accelerator OR ASIC |

### Official Sources

| Company | Primary URL | For |
|---------|-------------|-----|
| NVIDIA Automotive | https://developer.nvidia.com/drive | DRIVE platform, Thor/Orin docs |
| Qualcomm Automotive | https://www.qualcomm.com/products/automotive | Snapdragon Ride |
| Mobileye | https://www.mobileye.com | EyeQ, SuperVision, Chauffeur |
| 地平线 Horizon Robotics | https://www.horizon.ai | Journey/J6 series |
| 黑芝麻 Black Sesame | https://www.blacksesame.com.cn | A1000/A2000 |
| 爱芯元智 Axera | https://www.axera-tech.com | M55H/M76H ADAS SoCs |
| 芯擎科技 SiEngine | https://www.siengine.com.cn | SE1000/AD1000 |
| 辉羲智能 Huixi | https://www.huixi-tech.com | 光至 R1 |
| 后摩智能 Houmo AI | https://www.houmo.ai | H30/H60 PIM chips |
| 奕行智能 YiXing | https://www.evatechip.com | EVA-1 |
| 为旌科技 ViGEM | https://www.vigemtek.com | VS series ADAS SoCs |
| Ambarella | https://www.ambarella.com | CV3-AD, CV5, CV7 |
| NXP | https://www.nxp.com/applications/automotive | S32G/S32V/S32R, i.MX 95 |
| Infineon | https://www.infineon.com/cms/en/applications/automotive | AURIX TC4x, TRAVEO, PSoC |
| STMicro | https://www.st.com/content/st_com/en/applications/automotive.html | Stellar, Accordo |
| Hailo | https://hailo.ai | Hailo-8/Hailo-10 AI accelerator |
| Kneron | https://www.kneron.com | KL730/KL830 edge NPU |
| Renesas | https://www.renesas.com/us/en/application/automotive | R-Car V4H, R-Car X5 |
| Texas Instruments | https://www.ti.com/applications/automotive | TDA4VM, AM62A |
| Tesla | https://www.tesla.com/AI | FSD Computer, Dojo |
| Google TPU | https://cloud.google.com/tpu | TPU specs |

## Research Workflows

### Workflow 1: Deep-Dive Chip Analysis (深度调研)

When user says "深度调研 [CHIP_NAME]":

1. **Web search for official specs**: `"[CHIP_NAME] datasheet OR specifications OR whitepaper"`
2. **Web search for third-party analysis**: `"[CHIP_NAME] review OR analysis OR benchmark" site:anandtech.com OR site:semianalysis.com`
3. **arXiv search**: Search arxiv for papers referencing the chip architecture
4. **Competitor identification**: Find 3-5 comparable chips
5. **Output the full report** using this template:

```markdown
## [芯片名称] 深度调研报告

### 1. 规格摘要表
| 参数 | 规格 |
|------|------|
| 制程 (Process Node) | N4 / N5 / ... |
| 晶体管数 (Transistors) | XXB |
| Die Size | XX mm² |
| 算力 (INT8/FP16/BF16) | XX / XX / XX TOPS |
| TDP | XX W |
| 能效比 (TOPS/W) | XX |
| 存储带宽 (Mem BW) | XX GB/s |
| 存储类型 | HBM3 / LPDDR5X ... |
| 互联 (Interconnect) | NVLink / PCIe Gen5 / CXL ... |
| 封装 (Packaging) | CoWoS / EMIB / ... |
| 制程来源 | 🥇/🥈/🥉/⚠️ |

### 2. 架构分析
- 计算核心微架构
- 存储层次与带宽
- 互联拓扑
- 专用加速单元 (Tensor Core / NPU / ISP / ...)

### 3. 竞品对比
| 参数 | 本品 | 竞品A | 竞品B | 竞品C |
|------|------|-------|-------|-------|
| ... | ... | ... | ... | ... |

### 4. 车载适配性评估 (如适用)
| 维度 | 评估 |
|------|------|
| ASIL 等级 | ASIL-B(C) / ASIL-D |
| AEC-Q100 | ✓ / ✗ |
| 工作温度 | -40~105°C / ... |
| 实时性 | 硬实时/软实时 |
| 软件栈 | CUDA/TensorRT/DNNL/... |

### 5. 定位与市场判断
- 目标市场
- 量产时间线
- 竞争优势/劣势
- 信息来源汇总
```

### Workflow 2: Quick Scan (速览)

When user says "速览 [TOPIC]":

1. Single web search for the topic
2. Output a compact specs table + one-paragraph positioning summary
3. Offer: "需要深度分析吗？"

### Workflow 3: Weekly Digest (本周动态)

When user says "本周动态" or "本周 AI 芯片":

1. Search for news from last 7 days:
   - `site:anandtech.com chip OR processor OR GPU 2026`
   - `site:semianalysis.com`
   - `site:servethehome.com`
   - 中文: `site:chedongxi.com OR site:semiinsights.com`
2. Check arXiv CS.AR for new papers
3. Check official NVIDIA/AMD/Intel blogs
4. Output as categorized digest with bullet points

### Workflow 4: Competitive Comparison (竞品对比)

When user says "对比 X vs Y vs Z":

1. Search specs for each chip individually
2. Build comparison table with at least: process, TOPS, TDP, TOPS/W, memory BW, package, target market
3. Add a "verdict" row for each dimension
4. Flag any missing/unconfirmed data with ⚠️

### Workflow 5: Automotive Suitability Assessment (车载适配分析)

When user says "车载适配 [CHIP]":

1. Check for ASIL certification
2. Check AEC-Q100 qualification
3. Check operating temperature range
4. Check real-time capabilities
5. Check software ecosystem (AUTOSAR, ROS2, Hypervisor support)
6. Output suitability matrix with go/no-go recommendation

### Workflow 6: Discover New SoC Vendors (发现新厂商)

When user says "发现新车载 SoC 厂商" or asks about emerging players:

1. **VC/Funding search**: Search Crunchbase, 36Kr, IT桔子 for recent semiconductor/automotive chip funding rounds — `"automotive chip" OR "ADAS SoC" funding round 2025 2026`
2. **Supply chain signals**: Search for new tape-out announcements — `"tape out" OR "流片" automotive SoC 2025 2026`
3. **Academic pipeline**: Check ISSCC/Hot Chips/ISCA proceedings for university automotive chip papers — flag teams that may be spinning out
4. **Talent tracking**: Search for key departures from NVIDIA/Mobileye/Qualcomm automotive teams forming startups — `"former NVIDIA" OR "former Mobileye" founder automotive chip`
5. **Certification trail**: Search AEC-Q100/ISO 26262 certification announcements — `"AEC-Q100" OR "ISO 26262" certification chip`
6. **Baidu/Zhihu Chinese ecosystem**: 百度/知乎搜索 `"车载芯片 创业" OR "智驾SoC 新公司" OR "自动驾驶芯片 融资"` for Chinese market startups

**Output format:**

```markdown
## 新兴车载 SoC 厂商侦察报告 (YYYY-MM-DD)

### 已确认的新玩家 (有流片/定点/认证)
| 厂商 | 国家 | 产品 | 制程 | 算力 | 状态 | 信息来源 |
|------|------|------|------|------|------|----------|
| ... | ... | ... | ... | ... | tape-out/样片/定点 | ... |

### 待观察的信号
| 线索 | 类型 | 详情 | 置信度 |
|------|------|------|--------|
| ... | 融资/论文/人才/流片传闻 | ... | 高/中/低 |

### 推荐关注
- 列出 3-5 家最值得持续追踪的公司及理由
```

## Search Query Patterns

Use these with web_search or browser tools:

### English Queries
- Chip specs: `"[CHIP] package" site:wikichip.org`
- Benchmarks: `"[CHIP] MLPerf inference benchmark results"`
- News: `"[COMPANY] automotive chip announcement 2026"`
- Papers: `"accelerator architecture" site:arxiv.org/abs`
- Die analysis: `"[CHIP] die shot TechInsights"`

### Chinese Queries
- 芯片规格: `"[芯片名] 规格 算力 TOPS`
- 车载: `"智驾域控 [车型] 芯片方案 拆解"`
- 行业: `"自动驾驶芯片 2026 对比 地平线 英伟达 高通"`
- 趋势: `"中央计算平台 跨域融合 SoC"`

## Key Terminology Quick Reference

| Abbreviation | Full Name | Chinese |
|-------------|-----------|---------|
| ADAS | Advanced Driver Assistance Systems | 高级驾驶辅助系统 |
| ASIL | Automotive Safety Integrity Level | 汽车安全完整性等级 |
| AUTOSAR | AUTomotive Open System ARchitecture | 汽车开放系统架构 |
| Chiplet | - | 芯粒/小芯片 |
| CoWoS | Chip on Wafer on Substrate | 台积电先进封装 |
| DDS | Data Distribution Service | 数据分发服务 |
| EEA | Electrical/Electronic Architecture | 电子电气架构 |
| GMSL | Gigabit Multimedia Serial Link | 千兆多媒体串行链路 |
| HBM | High Bandwidth Memory | 高带宽存储器 |
| ISP | Image Signal Processor | 图像信号处理器 |
| MCU | Microcontroller Unit | 微控制器 |
| NoC | Network on Chip | 片上网络 |
| NPU | Neural Processing Unit | 神经网络处理器 |
| SerDes | Serializer/Deserializer | 串行器/解串器 |
| SoC | System on Chip | 片上系统 |
| TSN | Time-Sensitive Networking | 时间敏感网络 |
| UCIe | Universal Chiplet Interconnect Express | 通用芯粒互联标准 |

## Chip Hardware Image Sources

When reports need chip die shots, processor photos, or hardware imagery:

| Source | URL | Type |
|--------|-----|------|
| Unsplash | `https://unsplash.com/s/photos/processor` | Free chip/processor photos |
| WikiChip | `https://en.wikichip.org/wiki/File:` | Annotated die shots |
| TechInsights | `https://www.techinsights.com` | Professional teardown images (paywall) |
| Chipwise | `https://www.chipwise.com` | Chinese-language chip teardowns |
| Fritzchens Fritz | `https://www.flickr.com/photos/130561288@N04` | High-quality open-source die shots |
| CPU Shack | `https://www.cpushack.com` | Historic processor imagery |

For Bing image search (user preference): search with `"chip die shot" OR "processor wafer" OR "SoC package"` and filter by size=Large.

## Pitfalls

1. **Never** present die size or transistor counts from AI-generated summaries — always verify against official documentation or reliable third-party teardown sources (TechInsights, Chipwise, etc.)
2. **TOPS numbers are not comparable across vendors** — NVIDIA INT8 TOPS ≠ Qualcomm INT8 TOPS due to different sparsity assumptions. Always note the precision format and sparsity setting.
3. **Automotive qualification (ASIL, AEC-Q100) is not implied by the silicon alone** — it requires the full SoC + software stack + toolchain certification. Flag this distinction.
4. **Chinese chip companies often don't publish detailed English datasheets** — search in Chinese (中文) for domestic products
5. **Conference papers (ISCA, MICRO, HPCA, Hot Chips) are often more current than arXiv preprints** for established companies — check conference proceedings for latest architectural details
