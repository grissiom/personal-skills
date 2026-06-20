# Chinese Automotive SoC Companies — Quick Reference

Last updated: 2026-06

## 地平线 (Horizon Robotics)
- Founded: 2015 | HQ: Beijing
- Key Products: Journey 5 (128 TOPS), Journey 6 series (J6E/J6M/J6P)
- J6E: 80 TOPS, entry ADAS, mass production
- J6M: 128 TOPS, mid-tier L2+, mass production
- J6P: 560 TOPS, L3 highway + urban NOA, 2025 MP
- Architecture: BPU (Bernoulli/Nash/Turing generations), proprietary AI accelerator
- Software: TogetherOS, OpenExplorer toolchain
- Customers: Li Auto, BYD, Volkswagen (JV with CARIAD)
- ASIL: BPU IP rated ASIL-B(D), full SoC path to ASIL-D
- Funding: IPO Hong Kong 2024, market cap ~60B HKD

## 黑芝麻智能 (Black Sesame Technologies)
- Founded: 2016 | HQ: Shanghai
- Key Products: A1000 (58 TOPS), A1000L (16 TOPS), A2000 (250+ TOPS)
- A1000: 8-core A55, 58 TOPS INT8, LPDDR4x, mass production since 2022
- A2000: next-gen, 250+ TOPS, 7nm, targeting L2+/L3
- Architecture: In-house ISP + NPU (DynamAI NN engine), Arm Cortex CPU
- Software: Shanhai AI toolchain, supports PyTorch/ONNX/TensorFlow
- Customers: FAW, Dongfeng, JMC, Geely (A1000 in production vehicles)
- ASIL: A1000 ASIL-B system, A2000 targeting ASIL-D
- Funding: IPO Hong Kong 2024

## 爱芯元智 (Axera Semiconductor)
- Founded: 2019 | HQ: Shanghai
- Key Products: M55H, M76H (ADAS SoCs)
- M55H: mixed-precision NPU, entry-level ADAS, front-view/monocular
- M76H: higher performance, multi-sensor fusion, L2/L2+
- Architecture: Mixed-precision NPU (AxNeuron) + ISP (AxVision), Arm CPU
- Differentiation: ISP+NPU deep binding, ultra-low light performance, <1W in sleep
- Mass production: Since 2022, multiple vehicle models
- Customers: Multiple Chinese OEMs
- ASIL: Targeting ASIL-B

## 芯擎科技 (SiEngine)
- Founded: 2018 | HQ: Wuhan (backed by Geely/ECARX)
- Key Products: SE1000 "龍鷹一號" (7nm cockpit SoC), AD1000 (ADAS SoC)
- SE1000: 7nm, 8-core, 8 TOPS NPU, 4K display, mass production since 2023
- AD1000: ADAS SoC targeting 2026, 7nm, L2+ highway NOA
- Architecture: Arm Cortex + in-house NPU, multi-OS hypervisor
- Customers: Geely, Lynk & Co, Zeekr (SE1000 in mass production)
- Significance: China's first mass-produced 7nm automotive-grade SoC

## 辉羲智能 (Huixi Intelligence)
- Founded: 2022 | HQ: Shanghai (founded by ex-Waymo/Horizon engineers)
- Key Product: 光至 R1 (Guangzhi R1), L2++ autonomous driving SoC
- R1: 200+ TOPS, 2025 tape-out, targeting L2++ (highway + urban NOA)
- Architecture: Proprietary NPU, ARM Cortex-A78AE, safety island with lockstep R5F
- Software: Full-stack toolchain, supports BEV+Transformer deployment
- Status: Early stage, still in sampling/validation

## 后摩智能 (Houmo AI)
- Founded: 2020 | HQ: Nanjing
- Key Products: H30, H60 (PIM/CIM-based automotive chips)
- H30: 256 TOPS, 35W, 28nm, PIM (Processing-in-Memory) architecture, targeting L2+
- H60: Next-gen, higher performance, targeting L2+/L3
- Architecture: Computing-in-Memory (CIM), much higher energy efficiency than Von Neumann
- Differentiation: PIM architecture claims 10x+ energy efficiency for AI workloads
- Status: H30 in sampling, targeting automotive qualification

## 奕行智能 (YiXing Intelligence)
- Founded: 2022 | HQ: Shanghai
- Key Product: EVA-1, 7nm automotive SoC
- EVA-1: Vision-centric architecture for ADAS/AD, high ISP performance
- Target: L2+ ADAS, front-view + multi-camera
- Architecture: Proprietary vision processor + NPU, 7nm process
- Status: Early stage, tape-out expected

## 为旌科技 (ViGEM Technology)
- Founded: 2020 | HQ: Shanghai
- Key Products: VS series automotive SoCs for L2/L2+ ADAS
- Target: Entry-to-mid tier ADAS, front-view + corner radar fusion
- Architecture: In-house ISP + AI accelerator, Arm CPU cores
- Status: In development/sampling phase

## 芯驰科技 (SemiDrive)
- Founded: 2018 | HQ: Nanjing
- Key Products: X9 series cockpit, G9 gateway, V9 ADAS
- X9HP: High-performance cockpit, 4K multi-display
- Focus: Cockpit + gateway, expanding into domain controllers
- Customers: Multiple Chinese OEMs (cockpit in mass production)
- ASIL: X9 targeting ASIL-B, V9 targeting ASIL-D
