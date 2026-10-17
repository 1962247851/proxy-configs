# proxy-configs

个人规则 + ACL4SSR NoAuto 上游同步。GitHub 用户：`1962247851`，默认分支：`main`。

## 结构

- `rules/DIRECT/custom.yaml`：12 条直连规则（已包含全部指定域名）
- `rules/REJECT/`：自定义拦截规则，按需新增 `.yaml`
- `rules/PROXY/`：走 `🚀 节点选择` 的自定义代理规则，按需新增 `.yaml`
- `scripts/sync_acl4ssr.py`：扫描目录、下载最新 ACL4SSR NoAuto INI、插入规则引用
- `.github/workflows/sync-acl4ssr.yml`：每 6 小时 / 规则目录变动 / 手动触发
- `subconverter/ACL4SSR_Online_Full_NoAuto.ini`：Actions 首次运行**才会生成**，不要手工编辑

## 初次部署

1. 在 GitHub 创建 **公开**仓库 `1962247851/proxy-configs`，主分支 `main`，上传压缩包**内部的全部文件**（包括 `.github/` 隐藏目录）。
2. 进入 GitHub **Actions → Sync ACL4SSR NoAuto → Run workflow**，运行成功后确认新建 `subconverter/ACL4SSR_Online_Full_NoAuto.ini`。若提交失败，检查 Settings → Actions → General → Workflow permissions 是否允许 `Read and write permissions`；组织策略可能限制。
3. 在现有 SubConverter-Extended 订阅链接中，**只替换 `config=`** 为以下 URL 的 URL 编码值；其余 `url`、`target`、`classic` 等参数不变：

   `https://raw.githubusercontent.com/1962247851/proxy-configs/main/subconverter/ACL4SSR_Online_Full_NoAuto.ini`

4. 让 OpenClash **更新一次完整配置订阅**并使用 Mihomo/Meta 内核。检查生成 YAML 的 `rule-providers:` 和 `rules:` 中自定义 `RULE-SET` 位于公共规则之前。
5. 此后修改现有 `rules/DIRECT/custom.yaml` 内容：Mihomo 按 `3600` 秒定期检查远程规则文件，**不需要重新生成主配置**；增加或删除规则文件则需 OpenClash 再更新一次主订阅以注册/移除 Provider。

## 新增规则集

例如创建 `rules/REJECT/tracker.yaml`：

```yaml
payload:
  - DOMAIN-SUFFIX,tracker.example.com
```

或创建 `rules/PROXY/ai.yaml`：

```yaml
payload:
  - DOMAIN-SUFFIX,chatgpt.com
```

提交后 GitHub Actions 自动把远程 Provider 插入上游模板，随后 OpenClash 主订阅更新即可使用。新文件保持 Mihomo classical 的 `payload` 格式。规则从上到下匹配，优先级高于 ACL4SSR 公共规则。

## 更新流程

- 修改已存在 YAML 的规则内容：Mihomo 原生 `rule-providers` 自动更新；更新间隔 3600 秒，不是立即推送。
- 新增/删除 YAML：Actions 自动提交更新的 INI；OpenClash 必须更新完整订阅。
- ACL4SSR 上游修改：Actions 每 6 小时检查；OpenClash 必须更新完整订阅才能应用新模板。
- 不要修改 Actions 自动生成的 INI，否则下次同步会覆盖。GitHub Actions 定时任务可能延迟或被平台停用；可手动运行。

## 安全

**不要把机场订阅 Token、代理服务器凭据或私钥上传公开 GitHub 仓库。** Actions 不需要机场订阅链接，也不会访问订阅信息。

## 故障排查

- Actions 下载失败：检查 GitHub 到上游 raw.githubusercontent.com 的可用性。
- Actions 推送失败：检查 Workflow 权限、分支保护规则。
- SubConverter 没生成远程 `rule-providers`：确认使用兼容的 **SubConverter-Extended** 版本，检查服务日志和生成的完整 YAML。
- OpenClash 未加载：检查 Mihomo 内核、GitHub Raw 连通性和客户端日志，并确保其他覆写没有清理 `rule-providers`。
