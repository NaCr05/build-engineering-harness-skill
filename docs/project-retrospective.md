# 项目复盘：Build Engineering Harness

> 收尾基线：`v0.3.4-beta`（提交 `89fb54a3671fb239bee5f7d0f9de600d62f3bea1`）。本文记录截至该基线已经完成的工作与已知限制；最新公开版本以 [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) 为准，维护状态与支持承诺分别以 [`CONTRIBUTING.md`](../CONTRIBUTING.md) 和 [`SECURITY.md`](../SECURITY.md) 为准。

## 项目目标与最终结果（Project Goal and Final Outcome）

项目目标是把个人 AI 工程方法沉淀成一个可安装的 Codex Skill，帮助人类与 Agent 围绕明确目标、可信仓库知识、权限边界和可执行证据协作。它不替代项目本身的工程判断，而是提供一套从只读审计、方案审批、受控实施到验证收尾的工作方式。

截至收尾基线，仓库交付了以下结果：

| 目标 | 已交付结果 | 证据 | 状态 |
|---|---|---|---|
| 将方法论变成可执行 Skill | 英文运行规则、同步中文说明、方法论参考、知识治理参考、审计模板和项目收尾模板组成可安装包 | [`skill/build-engineering-harness/`](../skill/build-engineering-harness/) | 已实现并受结构验证 |
| 约束 Agent 的修改边界 | 工程 Harness 模式采用“先只读评估、用户批准后实施”的两阶段契约；项目收尾模式只允许写两份固定文档 | [`SKILL.md`](../skill/build-engineering-harness/SKILL.md) | 已实现并有静态测试 |
| 让仓库知识可治理 | 建立“功能角色 × 更新语义”模型，明确主要角色、权威范围、所有者、触发条件和验证关系 | [`repository-knowledge-governance.md`](../skill/build-engineering-harness/references/repository-knowledge-governance.md) | 已实现并通过 L2 场景验证 |
| 让行为验证可追溯 | 建立 L1、L2、L3 隔离前向测试、Schema v2 运行证据、哈希绑定和追加式历史 | [`tests/scenarios/`](../tests/scenarios/)、[`tests/README.md`](../tests/README.md) | 三个基线场景均通过硬门禁并获得 10/10 |
| 提供可验证的安装包 | 确定性归档、manifest、校验和、来源提交、文件树哈希、安全安装器、备份和失败回滚 | [`scripts/`](../scripts/)、[`tests/installation/result.json`](../tests/installation/result.json) | 已实现并有隔离安装证据 |
| 建立可信发布链 | Windows/Linux 独立构建并逐字节比较，固定 Actions SHA，生成 Artifact Attestation，只刷新 Draft Release，拒绝覆盖已公开资产 | [验证工作流](../.github/workflows/validate.yml) | 已由 `v0.3.4-beta` 标签工作流验证 |
| 形成可暂停维护的公开仓库 | MIT 许可、双语 README、贡献规则、安全报告入口、Issue 模板、Ruleset、Changelog 约束和明确维护声明 | [`README.md`](../README.md)、[`CONTRIBUTING.md`](../CONTRIBUTING.md)、[`SECURITY.md`](../SECURITY.md) | 已完成；当前为维护暂停的 Beta |

这是一项 Beta 交付，不是稳定版承诺。合成场景验证了代表性工作流和安全边界，但不能等价为对所有真实仓库的完整覆盖。

## 关键技术决策（Key Technical Decisions）

1. **把批准边界写进运行契约。** 普通评估请求只授权读取和提出方案；只有明确批准才允许实施。这样把“建议”和“写入权限”分开，减少 Agent 因语义模糊扩大修改范围的风险。
2. **按风险选择 L1、L2、L3 强度。** 小型项目、多人持续协作项目和 Agent 密集型项目需要不同密度的规则与证据；Skill 不为套模板而制造文件。
3. **用“功能角色 × 更新语义”治理知识。** 每个工件必须有且只有一个主要角色，可有零到两个仅用于导航和理解的次要角色；更新语义只能有一个，目录、责任和验证规则由主要角色决定。
4. **区分规范验证与前向评测。** 静态测试检查结构、链接、打包器和安装器的不变量；L1/L2/L3 场景检查 Skill 面对代表性仓库时是否做出合适判断。两者不能互相替代。
5. **证据必须绑定输入、输出和执行来源。** Schema v2 使用域分隔哈希记录 Skill、Prompt、期望、响应、Fixture、执行器和评审信息；历史运行只追加，不原地改写。
6. **发布产物由仓库源码确定性生成。** `VERSION` 与 Skill 树决定安装包内容，manifest 和哈希描述实际产物；跨平台独立构建必须逐字节一致。
7. **先认证来源，再执行安装器。** 发布资产通过 GitHub Artifact Attestation 绑定仓库、标签和固定签名工作流；安装器随后再次检查 manifest、归档和文件哈希，并在升级失败时恢复备份。
8. **自动化止于 Draft，公开发布保留人工确认。** 标签触发验证、认证和 Draft Prerelease；工作流遇到已经公开的同名 Release 必须停止，禁止覆盖不可变资产。
9. **维护暂停是显式的运行状态。** 通过公开维护声明、暂停计划型 Dependabot 版本 PR、保留安全报告入口和既有 CI，把“不保证响应”与“现有版本仍可验证下载”同时说清楚。

## 做得好的方面（What Went Well）

- **范围控制逐步变成机器可检查的不变量。** 两阶段契约、收尾模式写入范围、发布资产不可覆盖、运行历史只追加，都不只停留在说明文字中。
- **测试证据从“有结果”升级为“能追溯结果”。** 三个场景均记录硬门禁、分项理由、输入输出哈希和隔离方式；安装证据覆盖全新安装、升级备份、故障回滚和篡改拒绝。
- **发布链同时关注一致性与来源。** Windows 和 Linux 分别构建后逐字节比较，解决“同一个标签在不同平台产生不同包”的风险；Attestation 再补充来源认证。
- **公开文档与运行规则职责清楚。** README 面向使用者，`SKILL.md` 管实际行为，参考文件承载详细方法，测试文档解释证据规则，CHANGELOG 记录版本变化，避免一个入口承担全部知识。
- **兼容性承诺有证据边界。** CPython 3.10–3.13 以及托管 Windows、Ubuntu、macOS 的 CI 覆盖被明确列出；WSL、Windows PowerShell 5.1 和其他 Unix 被标记为尽力支持。
- **停更状态没有破坏供应链安全边界。** CI、Ruleset、Secret Scanning、Push Protection、私密漏洞报告和发布资产认证仍保留，只有会持续制造维护工作的计划型版本更新被暂停。

## 问题、原因与解决方案（Problems, Causes, and Solutions）

| 问题 | 根因 | 采取的解决方案 | 当前结论 |
|---|---|---|---|
| README、docs、AGENTS.md、决策记录和当前状态可能互相冲突 | 只按文件类型分类，无法表达职责、时效和权威范围 | 建立六类功能角色、四种更新语义、主要角色唯一性和验证关系；提供正式审计模板 | 方法已进入 Skill，并由 L2 场景验证 |
| 早期场景结果能评分，但来源和运行过程信息不足 | Schema v1 没有完整记录执行器、模型、耗时、用量和输入包哈希 | 升级为 Schema v2、加入域分隔哈希和追加式历史；无法恢复的历史字段明确写入未知原因 | 旧运行已安全迁移，但部分遥测仍不可追溯 |
| 安装脚本可能面对路径穿越、符号链接、篡改或半安装状态 | 仅依赖下载成功或单一校验和不足以覆盖安装过程 | 校验 manifest、文件和文件树哈希，拒绝不安全路径与符号链接，使用临时目录、备份和自动回滚 | 静态测试和隔离安装证据均覆盖关键失败路径 |
| Windows 与 Linux 构建结果可能不同 | 文件遍历、换行或归档元数据受平台影响 | 固定排序、权限和时间戳；两个平台独立构建后逐字节比较 | CI 已将一致性作为合并和发布前置条件 |
| 自动发布可能覆盖已公开版本的资产 | Draft 刷新与 Published Release 更新没有明确状态边界 | 工作流只允许创建或刷新 Draft；发现同名公开 Release 立即失败 | 已有静态回归测试，公开资产保持不可变 |
| Dependabot 自动 PR 与严格 Changelog 门禁发生冲突 | 依赖更新属于受控范围，但机器人 PR 不会同步人工维护的版本说明 | 吸收当期更新、保留门禁，并在维护暂停期将计划型版本 PR 上限设为 0 | 减少停更期噪声；恢复维护时需重新启用并集中更新 |
| Windows 工作流与安装器经历过执行兼容问题 | Shell 版本、命令调用方式和托管环境变化未在初期完整建模 | 明确 PowerShell 7 支持范围，补充 Windows dry-run 与跨平台兼容矩阵 | 当前受支持矩阵通过；PowerShell 5.1 仍为尽力支持 |
| 文档中的 Release 状态容易随 Draft → Published 变化而过期 | 把瞬时状态复制到多个长期文档 | 改为描述不随状态变化的规则，并把具体发布状态路由到 GitHub Releases | 公开文档不再依赖某个 Draft 状态 |

## 技术债与剩余风险（Technical Debt and Remaining Risks）

| 风险或限制 | 影响 | 当前控制 | 恢复维护时的建议 |
|---|---|---|---|
| 项目仍为 Beta，没有稳定版兼容承诺 | 使用者需自行评估对其仓库的适用性 | README 和 Release 明确 Beta；安装包可认证、可校验 | 先定义稳定版成功标准，再补真实仓库回归集后决定是否进入 `1.0.0` |
| L1/L2/L3 是代表性合成场景，不是广泛生产语料 | 可能遗漏复杂单体仓库、多仓协作或特殊组织规则 | 明确证据边界；保留可追加的场景格式 | 从真实使用反馈中挑选匿名、最小 Fixture，新增场景而不是修改历史运行 |
| 旧场景迁移到 Schema v2 后，模型版本、时间和用量等字段仍未知 | 无法完整比较历史成本、延迟和模型差异 | 对每个未知字段记录原因，不伪造数据 | 新运行必须由支持遥测的执行器原生记录这些字段 |
| WSL 只记录 POSIX 包装器 dry-run；PowerShell 5.1 和其他 Unix 未纳入保证矩阵 | 边缘环境中的完整替换或回滚行为未直接保证 | 核心替换路径复用已在 Windows 验证的 Python 安装器 | 有明确用户需求后再增加对应 CI 或端到端安装证据 |
| Codex Desktop 安装后自动刷新 Skill 目录未做自动化验证 | 用户可能需要新建任务后才能看到 Skill | 安装说明明确要求新建 Codex 任务 | 若平台提供稳定的目录刷新测试接口，再加入安装回归 |
| Actions 使用固定 SHA，而计划型 Dependabot 更新已暂停 | 长期停更会使 Actions 和工具链版本逐渐陈旧 | 固定 SHA 防止漂移；Ruleset 和安全扫描继续工作 | 恢复维护的第一批工作应审计 Actions、Python 与 GitHub CLI 兼容性并更新固定 SHA |
| 当前没有 Issue、PR 或安全报告的响应时限 | 外部反馈和漏洞报告可能长期等待 | 维护与安全文档明确“不承诺响应或修复时间” | 恢复维护时先处理私密安全报告，再重新声明支持版本与响应目标 |

## 可复用资产（Reusable Assets）

| 资产 | 可复用价值 | 入口 |
|---|---|---|
| 个人 AI 工程 Playbook | 用统一维度检查目标、上下文、工具、记忆、输出、失败处理、成本、延迟和可靠性 | [`personal-ai-engineering-playbook.md`](../skill/build-engineering-harness/references/personal-ai-engineering-playbook.md) |
| 仓库知识治理模型 | 用“功能角色 × 更新语义”定位权威冲突、责任空缺和知识漂移 | [`repository-knowledge-governance.md`](../skill/build-engineering-harness/references/repository-knowledge-governance.md) |
| 知识审计模板 | 为正式仓库审计提供工件清单、问题分级、事实来源和实施建议结构 | [`repository-knowledge-audit-template.md`](../skill/build-engineering-harness/assets/repository-knowledge-audit-template.md) |
| 项目收尾模板 | 约束复盘与新人上手文档的固定产出和必要章节 | [`project-closeout-templates.md`](../skill/build-engineering-harness/references/project-closeout-templates.md) |
| 仓库验证器 | 校验 Skill 结构、元数据、文档同步、链接、证据和发布约束 | [`validate_repository.py`](../scripts/validate_repository.py) |
| 确定性打包器与比较器 | 生成版本化资产并验证不同操作系统产物逐字节一致 | [`build_release_package.py`](../scripts/build_release_package.py)、[`compare_release_artifacts.py`](../scripts/compare_release_artifacts.py) |
| 安全安装器 | 提供 manifest/哈希校验、路径防护、备份、回滚和多平台包装器 | [`install_skill.py`](../scripts/install_skill.py)、[`install.ps1`](../scripts/install.ps1)、[`install.sh`](../scripts/install.sh) |
| Schema v2 前向测试 | 为 Skill 行为保留隔离、可评分、可哈希和只追加的运行证据 | [`tests/scenarios/`](../tests/scenarios/)、[`tests/README.md`](../tests/README.md) |
| 发布供应链工作流 | 演示固定 Action SHA、兼容矩阵、跨平台比较、Attestation 和 Draft-only 发布 | [`validate.yml`](../.github/workflows/validate.yml) |

## 下次可以做得不同（What to Do Differently Next Time）

1. **第一版就定义证据 Schema。** 在首次运行前确定执行器、模型、时间、用量、哈希域和未知值规则，避免后续只能以“未知原因”迁移历史记录。
2. **第一版就区分规范测试、行为评测与生产覆盖。** 三类证据的目标、门禁和可声明结论不同，应在测试目录建立时同时写清。
3. **在引入 Dependabot 前先设计机器人 PR 与 Changelog 的协作规则。** 严格门禁本身正确，但自动更新策略需要与维护成本共同设计。
4. **更早建立跨平台确定性构建。** 打包格式、时间戳、权限和换行一旦稳定后再修正，迁移成本会更高。
5. **从首次公开 Beta 起就使用 Draft-only 发布状态机。** 自动化负责可重复的证据生成，人类负责最终公开；公开资产从第一天起保持不可变。
6. **为“恢复维护”预留一份操作清单，而不是模糊承诺。** 恢复时应依次检查私密安全报告、Action 固定版本、运行时兼容性、依赖更新、前向场景和安装证据，再决定新版本范围。
7. **真实场景应在方法稳定后尽早加入。** 当前合成 Fixture 适合守住契约，但下一阶段最有价值的工作不是增加更多说明，而是积累去敏后的真实失败案例和回归场景。
