# 八字精批分析系统

完整的八字命盘分析、五行运势预测、技术分析与实战分析工具。

---

## 一、项目简介

本项目是一个结构化的八字分析系统，目标是将八字排盘、技术分析、实战分析、典籍引用和案例参考整合为一个完整的命理分析流程。

系统支持：

- 八字排盘
- 真太阳时校准
- 阴历换算
- 大运排布
- 流年、流月、流日展开
- 技术分析
- 妻财子禄寿实战分析
- 结构化最终输出
- 典籍与案例引用

---

## 二、整体结构

```text
skill/suanming/
├── SKILL.md
├── README.md
├── .gitignore
├── bin/
│   └── bazi
├── src/
│   ├── cities_longitude.py
│   ├── yuanju.py
│   ├── dayun.py
│   └── analyzer_generator.py
├── lib/
│   ├── original_analyzer.py
│   ├── tech_analyzer.py
│   └── practical_analyzer.py
└── reference/
    ├── .gitignore
    ├── books/
    │   ├── 穷通宝鉴.md
    │   ├── 子平真诠.md
    │   └── 子平真诠评注.md
    ├── examples/
    │   ├── cai.md
    │   ├── zhengguan.md
    │   ├── pianguan.md
    │   ├── shangguan.md
    │   └── examples.md
    └── tools/
        ├── common.py
        ├── datas.py
        ├── ganzhi.py
        ├── luohou.py
        ├── shengxiao.py
        ├── sizi.py
        └── yue.py

---

## 三、目录与文件职责说明

### 1. 根目录

#### `SKILL.md`
Skill 规则入口，定义：
- 技能名称
- 触发条件
- 调用方式
- 参数规则
- 输出规范
- 追问层级

#### `README.md`
项目说明文档，定义：
- 项目目标
- 目录结构
- 文件职责
- 功能特性
- 使用方式

#### `.gitignore`
全局 Git 忽略规则。

---

### 2. `bin/`

#### `bin/bazi`
唯一对外入口。

职责：
- 接收用户输入
- 统一参数格式
- 调起后续主流程
- 返回最终结果

---

### 3. `src/`

这一层是流程编排与结果生成层。

#### `src/cities_longitude.py`
真太阳时工具模块。

职责：
- 城市经度查询
- 均时差计算
- 真太阳时修正
- 真太阳时与平太阳时校准

#### `src/yuanju.py`
原局排盘模块。

职责：
- 接收真太阳时后的出生信息
- 计算四柱原局
- 输出原局结构
- 提供原局分析所需的基础数据

#### `src/dayun.py`
时间展开模块。

职责：
- 顺逆排
- 起运计算
- 大运序列
- 流年序列
- 流月序列
- 流日序列

#### `src/analyzer_generator.py`
最终输出生成器。

职责：
- 将排盘、分析、参考资料整合为最终结构化输出
- 组织最终 JSON / 报告内容
- 作为最终输出出口

---

### 4. `lib/`

这一层是核心分析引擎层。

#### `lib/original_analyzer.py`
原始分析引擎。

职责：
- 原始排盘分析
- 原始结构判断
- 基础命盘解释

#### `lib/tech_analyzer.py`
统一技术分析引擎。

职责：
- 串联并分析不同层级命盘内容
- 生克路线
- 刑冲合会害破
- 格局分析
- 十神与六亲
- 神煞分析
- 学术性 comments

#### `lib/practical_analyzer.py`
实战分析引擎。

职责：
- 妻财子禄寿分析
- 原局实战判断
- 当前大运实战判断
- 后续可扩展到流年、流月、流日

---

### 5. `reference/`

这一层是传统命理资料库与参考库。

#### `reference/.gitignore`
参考资料层自己的忽略规则。

#### `reference/books/`
经典典籍资料。

- `穷通宝鉴.md`
- `子平真诠.md`
- `子平真诠评注.md`

用途：
- 格局判断参考
- 调候参考
- 经典引证

#### `reference/examples/`
格局案例资料。

- `cai.md`
- `zhengguan.md`
- `pianguan.md`
- `shangguan.md`
- `examples.md`

用途：
- 财格案例
- 正官格案例
- 七杀格案例
- 伤官格案例
- 案例总索引

#### `reference/tools/`
底层命理工具与数据支持。

- `common.py`
- `datas.py`
- `ganzhi.py`
- `luohou.py`
- `shengxiao.py`
- `sizi.py`
- `yue.py`

用途：
- 基础判断函数
- 命理数据字典
- 干支基础定义
- 罗喉辅助
- 生肖辅助
- 命理短评资料
- 月令参考资料

---

## 四、功能特性

### 1. 八字排盘
- 真太阳时调整（基于城市经度）
- 干支推导
- 纳音五行
- 十神判断

### 2. 命盘分析
- 日主强弱判断
- 用神忌神分析
- 格局分类
- 特殊格局识别（如魁罡格、从格等）

### 3. 大运分析
- 大运排序
- 大运干支推导
- 大��吉凶评估
- 流年预测

### 4. 五行分析
- 五行分布统计
- 五行强弱对比
- 调候用神建议
- 五运深度分析

### 5. 命理学参考
- 《穷通宝鉴》分析
- 《子平真诠》参考
- 《子平真诠评注》参考
- 十二时辰解读
- 星宿吉凶辅助评估

---

## 五、使用方式

直接调用：

```bash
python3 skill/suanming/bin/bazi --year 1990 --month 1 --day 15 --hour 8 --minute 0 --gender male --city 西安 --level full

---

## 六、输出层级

本系统的输出分为四层：

### 第一层：排盘
- 基本信息
- 真太阳时换算结果
- 阴历换算结果
- 八字原局
- 原局排盘细节
- 8 个大运及每运干支十神

### 第二层：分析
- 技术分析
- 实战分析（妻财子禄寿）

### 第三层：结构化整合
- 排盘信息
- 身强弱
- 格局
- 喜用忌
- 全局精批（妻财子禄寿）
- 当前大运精批（妻财子禄寿）
- 当前大运 + 流年精批（妻财子禄寿）

### 第四层：最终输出
- 默认输出结构化结果
- 支持继续追问并逐层深挖到流年、流月、流日

---

## 七、备注

- `bin/bazi` 是唯一入口
- `src/analyzer_generator.py` 负责最终输出生成
- `lib/` 是核心分析层
- `reference/` 是典籍、案例和工具参考库
