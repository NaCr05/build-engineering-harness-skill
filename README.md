# Build Engineering Harness

[English](README.en.md)

一个面向人类与 AI Agent 协作的软件工程 Skill：审计、建立和改进项目的目标、仓库知识、规则、验证与反馈闭环，并在项目完成后沉淀复盘和新人上手资料。

> 当前候选版本：`v0.3.0-beta`。本轮为版本化安装包增加跨平台逐字节比较、构建来源证明和自动 Draft Prerelease；最新已公开版本仍是 `v0.2.0-beta`。

## 它解决什么问题

Agent 能否稳定完成工程任务，不只取决于模型能力，还取决于仓库是否提供了清晰的目标、可靠的事实来源、明确的边界、可执行的工作流和及时的验证反馈。

这个 Skill 用于帮助你回答：

- 项目目标、用户、输入、输出和成功标准是否清楚？
- 架构、模块边界、数据流和接口是否可理解？
- README、docs、AGENTS.md、决策记录和当前状态是否各司其职？
- 是否存在重复事实源、冲突规则或容易漂移的说明？
- 人、Agent 和自动化分别应该负责什么？
- 测试、评估、日志和错误处理能否证明结果正确？
- 项目结束后，哪些经验应该沉淀为长期资产？

## 核心能力

- **工程 Harness 体检**：基于仓库证据识别已有资产、缺口与风险。
- **仓库知识治理**：使用“功能角色 × 更新语义”模型管理知识工件。
- **权威与关系检查**：识别 canonical、explanatory、evidence，以及事实来源和验证关系。
- **Agent 项目专项审计**：检查 Prompt、Context、Tool、Memory、输出 Schema、失败处理、成本、延迟和可靠性。
- **验证闭环建设**：把主观的“看起来可用”转化为可执行证据。
- **项目收尾**：生成基于证据的项目复盘和新人上手文档。

## 安全工作方式

工程 Harness 模式严格分为两个阶段：

1. 只读检查并提出方案，不修改项目。
2. 只有用户明确批准后，才实施获批部分。

项目收尾模式是一个明确例外：用户显式要求收尾时，只允许创建或更新：

- `docs/project-retrospective.md`
- `docs/project-onboarding.md`

Skill 不会把普通的评估请求理解成写入许可，也不会因为偏好某套文件名而机械重组仓库。

## 仓库知识治理模型

每个知识工件具有：

- 一个主要角色，零到两个次要角色；
- 一种更新语义；
- 一种权威属性；
- 明确的维护责任、更新触发条件和验证方式。

六类功能角色：

1. 导览与路由
2. 规则与边界
3. 规格与契约
4. 状态与证据
5. 原因与历史
6. 执行与验证

四种更新语义：

1. 稳定入口
2. 同步更新
3. 追加演进
4. 派生生成

这是一套分类和诊断空间，不是要求每个项目创建固定数量文档的检查清单。

## 成熟度等级

| 等级 | 适用情况 | 建设重点 |
|---|---|---|
| L1 基础型 | 小型或低风险项目 | 入口、核心规则、必要契约和运行验证 |
| L2 管理型 | 多人持续协作 | 中央注册表、所有权、决策记录和同步检查 |
| L3 Agent 密集型 | Agent 高频参与或高风险系统 | 分层指令、项目 Skill、评测、生成证据和自动检查 |

等级取决于风险、协作人数、变化频率、Agent 参与度和错误成本，而不只取决于仓库大小。

## 安装

推荐从已公开的 GitHub Release 安装固定版本。`v0.3.0-beta` 会先由 CI 创建为 Draft Prerelease，完成人工核对并公开前，以下命令继续安装 [`v0.2.0-beta`](https://github.com/NaCr05/build-engineering-harness-skill/releases/tag/v0.2.0-beta)。

PowerShell：

```powershell
$version = "v0.2.0-beta"
$assetBase = "build-engineering-harness-$version"
gh release download $version --repo NaCr05/build-engineering-harness-skill --pattern "$assetBase*"

$expected = ((Get-Content "$assetBase.zip.sha256").Trim() -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash "$assetBase.zip" -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "Release archive checksum mismatch." }

$skillsDir = Join-Path $env:USERPROFILE ".codex\skills"
$target = Join-Path $skillsDir "build-engineering-harness"
if (Test-Path $target) { throw "Target already exists: $target. Back it up or remove it before upgrading." }
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
Expand-Archive -LiteralPath "$assetBase.zip" -DestinationPath $skillsDir
```

macOS 或 Linux：

```bash
version="v0.2.0-beta"
asset_base="build-engineering-harness-$version"
gh release download "$version" --repo NaCr05/build-engineering-harness-skill --pattern "$asset_base*"

expected="$(awk '{print $1}' "$asset_base.zip.sha256")"
actual="$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$asset_base.zip")"
[ "$actual" = "$expected" ] || { echo "Release archive checksum mismatch." >&2; exit 1; }

skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
target="$skills_dir/build-engineering-harness"
[ ! -e "$target" ] || { echo "Target already exists: $target. Back it up or remove it before upgrading." >&2; exit 1; }
mkdir -p "$skills_dir"
unzip -q "$asset_base.zip" -d "$skills_dir"
```

如需从源码安装，请克隆对应标签而不是移动中的 `main`：

```bash
git clone --branch v0.2.0-beta --depth 1 https://github.com/NaCr05/build-engineering-harness-skill.git
```

安装或升级后新建一个 Codex 任务，让 Skill 列表重新加载。

## 验证

仓库提供不依赖第三方包的跨平台验证入口：

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
python scripts/build_release_package.py --output-dir .test-runs/release-package
```

GitHub Actions 会在 Windows 和 Linux 上运行相同检查。发布前还必须运行：

```text
python scripts/validate_repository.py --release
```

`--release` 额外要求 L1、L2、L3 前向测试证据和从 GitHub 全新安装的验证记录。场景设计、隔离方法和评分规则见 `tests/README.md`。

CI 会分别上传 Windows 与 Linux 构建结果，再使用 `scripts/compare_release_artifacts.py` 逐字节比较 ZIP、校验文件和 manifest。版本标签只有在跨平台比较和发布证据都通过后，才会为资产生成 GitHub Artifact Attestation 并创建 Draft Prerelease。正式打包还要求 `VERSION` 与 Skill 包内容已经提交，并与给定来源提交一致。

## 快速使用

### 现有项目体检

```text
使用 $build-engineering-harness 对这个仓库做一次只读体检。
请从项目目标、架构、仓库知识、开发流程、验证方式和反馈闭环六个方面检查，
区分事实、推断、风险和建议。先不要修改文件。
```

### 仓库知识治理审计

```text
使用 $build-engineering-harness 的仓库知识治理模型审计这个项目，目标成熟度为 L2。
请检查工件角色、更新语义、权威范围、事实来源、验证关系和文档漂移。
使用正式审计模板输出，等待我批准后再实施。
```

### AI 或 Agent 项目审计

```text
使用 $build-engineering-harness 审计这个 Agent 项目。
除常规工程检查外，重点检查 Prompt、Context、Tool、Memory、输出 Schema、
失败处理，以及 Accuracy、Latency、Cost、Reliability 的评测覆盖。
```

### 批准实施

```text
我批准上一次方案中的第 1、3、4 项。
请只实施这些获批内容，保留无关修改，并在完成后报告验证证据和剩余风险。
```

### 项目收尾

```text
使用 $build-engineering-harness 进入 project-closeout 模式，
基于仓库证据生成项目复盘和新人上手文档，不修改产品代码或其他项目文件。
```

## 项目结构

```text
skill/build-engineering-harness/
├── SKILL.md
├── SKILL.zh-CN.md
├── agents/openai.yaml
├── references/
│   ├── personal-ai-engineering-playbook.md
│   ├── project-closeout-templates.md
│   └── repository-knowledge-governance.md
└── assets/
    └── repository-knowledge-audit-template.md
```

`SKILL.md` 是 Codex 实际加载的入口。`SKILL.zh-CN.md` 是供中文读者理解和核对的同步版本。详细方法按需放在 `references/`，可复制的输出模板放在 `assets/`。

## `v0.3.0-beta` 候选版验证证据

- L1、L2、L3 三组隔离前向测试均通过全部安全门禁，质量评分均为 10/10；原始回答与评分记录位于 [`tests/scenarios/`](tests/scenarios/)。
- 前向测试证据记录运行 ID、源提交、隔离方式及 Skill、Prompt、Fixture、预期、响应的可复算 SHA-256；证据见 [`tests/scenarios/`](tests/scenarios/)。
- 已从公开 GitHub 仓库构建并安装确定性版本化 ZIP，核对归档、校验和、manifest、源目录、安装目录和全新 Agent 响应；证据见 [`tests/installation/result.json`](tests/installation/result.json)。
- `v0.3.0-beta` 不改变可安装 Skill 的行为，继续使用同一 Skill 目录树和已有 L1、L2、L3 前向测试证据。
- GitHub Actions 已配置为上传 Windows 与 Linux 构建、比较全部发布资产、验证发布证据、生成 Artifact Attestation，并自动创建 Draft Prerelease。
- 所有第三方 Actions 均固定到完整提交 SHA；正式打包拒绝来源提交不匹配、未提交的包输入、符号链接、目录联接和特殊文件。

这些是可复现的代表性合成场景，不等同于对所有生产仓库的覆盖。`v0.3.0-beta` 在 Draft Prerelease 经过人工核对并公开前，不是可安装的公开版本或稳定版承诺。

## 参与贡献

提交改动前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。安全问题请参阅 [SECURITY.md](SECURITY.md)。版本变化记录在 [CHANGELOG.md](CHANGELOG.md)。

## 方法论来源

本项目将个人 AI 工程方法论、Agent 友好的仓库实践和工程验证原则整合为可执行 Skill。Harness Engineering 的整体方向受到 OpenAI 文章 [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) 的启发；仓库知识治理模型是面向通用软件项目重新抽象的原创综合方法。

## 许可证

本项目采用 [MIT License](LICENSE)。
