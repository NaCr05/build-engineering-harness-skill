# Build Engineering Harness

[English](README.en.md)

[![Validate repository](https://github.com/NaCr05/build-engineering-harness-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/NaCr05/build-engineering-harness-skill/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/NaCr05/build-engineering-harness-skill?include_prereleases&label=release)](https://github.com/NaCr05/build-engineering-harness-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个面向 Codex 的软件工程 Skill：让人类与 AI Agent 围绕清晰目标、可信仓库知识、明确边界和可执行证据协作，而不是只靠一次性的 Prompt。

`只读检查 → 改进方案 → 用户批准 → 实施 → 自动验证`

> 仓库版本：`v0.3.3-beta`。版本是否已经公开以及是否可下载，以 [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) 为准；`main` 可能领先于公开版本。

## 30 秒开始

安装完成后，在 Codex 中打开你的项目，直接发送：

```text
使用 $build-engineering-harness 对这个仓库做一次只读体检。
请从项目目标、架构、仓库知识、开发流程、验证方式和反馈闭环六个方面检查，
区分事实、推断、风险和建议。先不要修改文件。
```

Skill 会先用仓库证据给出成熟度判断、优先级问题和分批改进方案；只有你明确批准后，它才会修改获批范围。尚未安装？跳到[安装](#安装)。

## 你会得到什么

| 你的场景 | 主要产出 |
|---|---|
| 初步完成的项目需要整理或开源 | 目标、架构、仓库知识、流程、验证与发布准备度体检 |
| README、docs、AGENTS.md 或当前状态容易漂移 | 工件角色、权威范围、事实来源、维护责任与漂移风险审计 |
| AI 或 Agent 功能需要工程化 | Prompt、Context、Tool、Memory、输出 Schema、失败处理、成本、延迟与可靠性检查 |
| 已批准实施改进 | 严格限于批准范围的修改、自动验证证据和剩余风险 |
| 项目准备交接或结束 | 基于证据的项目复盘和新人上手文档 |

它适用于新项目、遗留项目、团队仓库和 Agent 密集型系统；不会为了套用模板而强迫每个项目创建同一组文件。

## 工作方式与安全边界

工程 Harness 模式分为两个严格阶段：

1. **只读评估**：检查仓库、区分事实与推断、提出可审查方案，不修改项目。
2. **批准后实施**：只实施用户明确批准的项目，保留无关改动，并报告验证结果。

普通的“评估、审计、解释”请求不构成写入许可。项目收尾是一个显式例外：用户直接要求 `project-closeout` 时，只允许创建或更新 `docs/project-retrospective.md` 和 `docs/project-onboarding.md`。

Codex 实际执行的完整规则见 [`SKILL.md`](skill/build-engineering-harness/SKILL.md)，中文同步说明见 [`SKILL.zh-CN.md`](skill/build-engineering-harness/SKILL.zh-CN.md)。

## 适用场景与成熟度

Skill 会根据风险、协作人数、变化频率、Agent 参与度和错误成本选择合适强度：

| 等级 | 适用情况 | 建设重点 |
|---|---|---|
| L1 基础型 | 小型或低风险项目 | 入口、核心规则、必要契约和运行验证 |
| L2 管理型 | 多人持续协作 | 中央注册表、所有权、决策记录和同步检查 |
| L3 Agent 密集型 | Agent 高频参与或高风险系统 | 分层指令、项目 Skill、评测、生成证据和自动检查 |

仓库知识使用“**功能角色 × 更新语义**”模型治理：每个工件有且只有一个主要角色、一种更新语义和一种权威属性，并明确所有者、更新触发条件与验证方式。六类角色和四种更新语义的完整定义见[仓库知识治理参考](skill/build-engineering-harness/references/repository-knowledge-governance.md)。

## 安装

### 支持范围

| 运行面 | 支持契约 | CI 证据 |
|---|---|---|
| Python 工具与安装器 | CPython 3.10–3.13 | Ubuntu 覆盖全部版本；Windows 和 macOS 覆盖 3.12 |
| PowerShell 安装包装器 | Windows 上的 PowerShell 7 | `windows-latest` dry-run |
| POSIX 安装包装器 | Ubuntu 和 macOS 上的 `sh` | `ubuntu-latest` 与 `macos-latest` dry-run |
| 操作系统 | 当前 GitHub 托管的 Windows、Ubuntu 和 macOS 运行器 | 每次 PR 和 `main` 推送验证 |

Windows PowerShell 5.1、其他 Unix 发行版和 WSL 属于尽力支持范围，不是当前 CI 保证。发现兼容性问题时请提供具体版本和最小复现。

准备条件：上述受支持范围内的 Python、支持 `gh attestation` 的 [GitHub CLI](https://cli.github.com/)，以及已完成的 `gh auth login`。请选择 [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) 中已经公开的固定版本；下面以当前仓库版本为例。

安装顺序固定为：下载资产 → 验证 GitHub Artifact Attestation → 安装器只读校验 → 安装。来源验证会绑定本仓库、对应版本标签和固定签名工作流。

<details>
<summary>PowerShell（Windows）</summary>

```powershell
$version = "v0.3.3-beta"
$repository = "NaCr05/build-engineering-harness-skill"
$signerWorkflow = "$repository/.github/workflows/validate.yml"
$assetBase = "build-engineering-harness-$version"
$assets = Join-Path $env:TEMP "$assetBase-assets"
New-Item -ItemType Directory -Force -Path $assets | Out-Null
gh release download $version --repo $repository --dir $assets --pattern "$assetBase*" --pattern "install*"

Get-ChildItem -LiteralPath $assets -File | ForEach-Object {
    gh attestation verify $_.FullName --repo $repository --source-ref "refs/tags/$version" --signer-workflow $signerWorkflow
    if ($LASTEXITCODE -ne 0) { throw "Attestation verification failed for $($_.Name)" }
}

& "$assets\install.ps1" -Version $version -AssetDir $assets -DryRun
& "$assets\install.ps1" -Version $version -AssetDir $assets
```

</details>

<details>
<summary>macOS 或 Linux</summary>

```bash
set -eu
version="v0.3.3-beta"
repository="NaCr05/build-engineering-harness-skill"
signer_workflow="$repository/.github/workflows/validate.yml"
asset_base="build-engineering-harness-$version"
assets="$(mktemp -d)"
gh release download "$version" --repo "$repository" --dir "$assets" --pattern "$asset_base*" --pattern "install*"

for asset in "$assets"/*; do
  gh attestation verify "$asset" --repo "$repository" --source-ref "refs/tags/$version" --signer-workflow "$signer_workflow"
done

sh "$assets/install.sh" --version "$version" --asset-dir "$assets" --dry-run
sh "$assets/install.sh" --version "$version" --asset-dir "$assets"
```

</details>

安装器遵循 `CODEX_HOME`；未设置时使用用户目录下的 `.codex`。升级会先备份旧版本，失败时自动恢复。安装或升级后请新建一个 Codex 任务，让 Skill 列表重新加载。

## 常用 Prompt

### 审计仓库知识治理

```text
使用 $build-engineering-harness 的仓库知识治理模型审计这个项目，目标成熟度为 L2。
检查工件角色、更新语义、权威范围、事实来源、验证关系和文档漂移。
使用正式审计模板输出，等待我批准后再实施。
```

### 审计 AI 或 Agent 项目

```text
使用 $build-engineering-harness 审计这个 Agent 项目。
除常规工程检查外，重点检查 Prompt、Context、Tool、Memory、输出 Schema、
失败处理，以及 Accuracy、Latency、Cost、Reliability 的评测覆盖。
```

### 实施已批准的改进

```text
我批准上一次方案中的第 1、3、4 项。
请只实施这些获批内容，保留无关修改，并在完成后报告验证证据和剩余风险。
```

### 项目收尾

```text
使用 $build-engineering-harness 进入 project-closeout 模式，
基于仓库证据生成项目复盘和新人上手文档，不修改产品代码或其他项目文件。
```

## 信任与验证

| 保证 | 实现方式 | 可核对证据 |
|---|---|---|
| Skill 行为可评估 | 隔离的 L1、L2、L3 前向测试和统一安全门禁 | [`tests/scenarios/`](tests/scenarios/) 与 [`tests/README.md`](tests/README.md) |
| 评测记录可追溯 | Schema v2 哈希、运行与评审来源、逐项理由、追加式历史 | [`tests/scenarios/`](tests/scenarios/) |
| 安装过程可校验 | manifest、归档与文件哈希、备份和失败回滚 | [`tests/installation/result.json`](tests/installation/result.json) |
| 跨平台产物一致 | Windows 与 Linux 独立构建并逐字节比较 | [验证工作流](.github/workflows/validate.yml) |
| 发布来源可证明 | 六项发布资产生成 GitHub Artifact Attestation | [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) |

本地验证入口不依赖第三方 Python 包：

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
python scripts/build_release_package.py --output-dir .test-runs/release-package
python scripts/validate_repository.py --release
```

这些证据来自可复现的代表性合成场景，不等同于所有生产仓库的覆盖，也不是稳定版承诺。

## 项目导航

| 想了解什么 | 权威入口 |
|---|---|
| Skill 的实际行为和安全边界 | [`skill/build-engineering-harness/SKILL.md`](skill/build-engineering-harness/SKILL.md) |
| 个人 AI 工程方法 | [`personal-ai-engineering-playbook.md`](skill/build-engineering-harness/references/personal-ai-engineering-playbook.md) |
| 仓库知识治理模型 | [`repository-knowledge-governance.md`](skill/build-engineering-harness/references/repository-knowledge-governance.md) |
| 前向测试、隔离方法和评分规则 | [`tests/README.md`](tests/README.md) |
| 版本变化 | [`CHANGELOG.md`](CHANGELOG.md) |
| 贡献方式 | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| 安全问题报告 | [`SECURITY.md`](SECURITY.md) |

## 方法论与许可

本项目将个人 AI 工程方法、Agent 友好的仓库实践和证据驱动验证整合为可执行 Skill。整体方向受到 OpenAI 文章 [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) 的启发；仓库知识治理模型是面向通用软件项目重新抽象的原创综合方法。

本项目采用 [MIT License](LICENSE)。
