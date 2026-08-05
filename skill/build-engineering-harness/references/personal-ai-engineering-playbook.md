# Personal AI Engineering Playbook

> 面向 AI Agent / 软件工程项目的个人开发方法论  
> Version: 1.0

---

# 0. 核心理念

## 从 Coding 到 Engineering

传统开发：

    需求
     ↓
    写代码
     ↓
    运行
     ↓
    修 Bug

AI Agent 时代：

    目标定义
     ↓
    系统设计
     ↓
    Harness 构建
     ↓
    Agent 执行
     ↓
    自动验证
     ↓
    反馈优化
     ↓
    持续迭代

核心变化：

> 工程师的价值不只是写代码，而是设计一个能够稳定产生正确结果的工程系统。

---

# 1. Harness Engineering 核心思想

## 1.1 什么是 Harness？

Harness = Agent 工作的完整工程环境。

包括：

- Context（上下文）
- Documentation（文档）
- Tools（工具）
- Workflow（流程）
- Rules（规范）
- Testing（测试）
- Feedback Loop（反馈闭环）
- Memory（经验沉淀）

模型决定能力上限，Harness 决定能力是否稳定发挥。

---

## 1.2 人负责方向，Agent 负责执行

Human：

- 定义目标
- 拆解任务
- 制定标准
- Review结果

Agent：

- 编码
- 调试
- 测试
- 文档生成
- 重复执行

不要问：

> AI 能不能帮我写代码？

应该问：

> 我有没有设计一个环境，让 AI 可以可靠完成任务？

---

# 2. 开始任何项目之前：7步流程

## Step 1：明确 Goal

必须明确：

- 为什么做？
- 解决什么问题？
- 用户是谁？
- 成功标准是什么？

形成：

    Project Goal

    Input:

    Output:

    Success Criteria:

---

## Step 2：设计 Architecture

不要直接写代码。

先设计：

- 模块边界
- 数据流
- API关系
- 核心组件

---

## Step 3：建立 Repository Knowledge

原则：

> 没写进项目里的知识，对 Agent 来说不存在。

每个项目至少应覆盖：

- 稳定的项目入口与任务路由；
- 必要的架构、边界或契约；
- 可执行的开发与验证方式；
- 会影响当前决策的状态与证据；
- 值得长期保留的决策和经验。

这些知识可以合并在已有文档、代码、Schema、测试或脚本中，不要求采用固定文件名或固定数量。优先维护少量清晰的事实来源，避免为了形式完整而创建容易过期的平行文档。

记录：

- 项目背景
- 技术方案
- 开发流程
- 常见问题
- 踩坑经验

---

## Step 4：设计 Agent Workflow

明确：

哪些任务交给 Agent？

哪些任务自己负责？

Agent：

- 生成代码
- 测试
- Debug
- 整理文档

Human：

- 架构设计
- 方向判断
- 质量审核

---

## Step 5：建立 Verification

任何功能必须可验证。

不要：

> 看起来能运行。

应该：

> 有明确测试证明它正确。

包括：

- API测试
- 单元测试
- 边界测试
- Benchmark
- Evaluation

---

## Step 6：建立 Feedback Loop

优秀系统：

    执行
     ↓
    验证
     ↓
    发现问题
     ↓
    修正
     ↓
    再次验证

不要追求一次成功。

追求快速发现错误。

---

## Step 7：项目结束后沉淀

每个项目留下：

    Project Summary

    ├── What I built
    ├── Architecture
    ├── Technology Stack
    ├── Problems
    ├── Solutions
    ├── Lessons Learned
    └── Reusable Templates

一次经验变成长期资产。

---

# 3. Agent-Friendly Engineering

未来代码不仅需要 Human-readable，也需要 Agent-readable。

原则：

## 模块职责清晰

避免：

    utils.py
    3000 lines

推荐：

    auth/
    database/
    payment/
    notification/

---

## 命名明确

避免：

    process()
    handle()
    data()

推荐：

    extract_news_article()
    calculate_sentiment_score()
    validate_user_input()

---

## 文档靠近代码

让 Agent 能快速找到上下文。

---

# 4. AI 协作开发原则

不要把 AI 当代码生成器。

错误：

    帮我写这个函数

正确：

    理解项目结构
    分析方案
    设计接口
    实现代码
    测试
    Review

---

# 5. 项目开发检查表

## 开始阶段

- [ ] 项目目标明确
- [ ] 用户需求明确
- [ ] 架构设计完成
- [ ] 技术栈确定
- [ ] 文档初始化

## 开发阶段

- [ ] 模块职责明确
- [ ] 有测试方式
- [ ] 有错误处理
- [ ] 有日志
- [ ] 有版本管理

## Agent项目额外检查

- [ ] Prompt是否明确
- [ ] Context是否充分
- [ ] Tool是否合理
- [ ] Output Schema是否固定
- [ ] Failure Handling是否存在

---

# 6. 经验沉淀原则

每次解决问题，都问：

## 1. 以后还会不会遇到？

如果会：

记录。

## 2. 能不能模板化？

例如：

Docker配置 → Docker模板

README → README模板

Prompt → Prompt模板

## 3. 能不能自动化？

重复工作：

优先脚本化。

---

# 7. AI Agent 项目重点

## Context Engineering

提供：

- 正确知识
- 正确工具
- 正确限制

## Tool Design

工具应该：

- 输入明确
- 输出稳定
- 错误可解释

## Memory

保存：

- 历史经验
- 用户偏好
- 项目状态

## Evaluation

定义：

- Accuracy
- Latency
- Cost
- Reliability

---

# 8. 最重要的十句话

1. 不要只开发功能，要开发产生功能的系统。
2. 不可见的知识等于不存在。
3. 文档不是附属品，而是 Agent 的工作环境。
4. 测试不是最后一步，而是 Agent 能力的一部分。
5. 人负责判断，Agent负责执行。
6. 好的架构首先应该让 Agent 理解。
7. 重复的问题应该变成模板。
8. 每次项目都应该留下可复用资产。
9. 速度来自自动化，而不是单纯增加工作量。
10. 优秀工程师的核心能力，是设计可靠系统。

---

# Final Principle

未来的软件开发：

    Human designs system

    ↓

    Agent executes work

    ↓

    Verification ensures quality

    ↓

    Knowledge accumulates

    ↓

    System improves continuously

这就是 AI Agent 时代的工程方法。
