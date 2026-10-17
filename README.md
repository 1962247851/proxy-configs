# proxy-configs

个人分流规则与 ACL4SSR NoAuto 自动合并仓库，仓库账号：`1962247851`。

## 目录

- `rulesets/DIRECT/*.list`：普通 SubConverter 规则集，注入 `🎯 全球直连`。
- `rulesets/REJECT/*.list`：普通 SubConverter 规则集，注入 `🛑 全球拦截`。
- `rulesets/PROXY/*.list`：普通 SubConverter 规则集，注入 `🚀 节点选择`。
- `rules/DIRECT/*.yaml` / `rules/REJECT/*.yaml` / `rules/PROXY/*.yaml`：可选 Mihomo 远程 classical Rule Provider；保留支持，但默认没有启用，避免重复规则。
- `scripts/sync_acl4ssr.py`：下载最新 ACL4SSR_Online_Full_NoAuto.ini 并自动插入自定义规则。
- `.github/workflows/sync-acl4ssr.yml`：每 6 小时、手动或规则文件变动时运行。

## 使用步骤

1. 将压缩包内文件上传到公开仓库 `1962247851/proxy-configs` 的 `main` 分支（合并/覆盖相同路径）。
2. 在 **Actions → Sync ACL4SSR NoAuto → Run workflow** 手动触发一次。工作流会自动产生 `subconverter/ACL4SSR_Online_Full_NoAuto.ini`。
3. 把现有 SubConverter 请求中 `config=` 的值改为：

   `https://raw.githubusercontent.com/1962247851/proxy-configs/main/subconverter/ACL4SSR_Online_Full_NoAuto.ini`

   其他参数不变。OpenClash 重新更新配置订阅一次。
4. 后续编辑 `rulesets/DIRECT/OrCustom.list`；普通 `.list` 在 **SubConverter 重新转换时** 拉取，OpenClash 需重新更新主订阅才会生效。不要把它当作 Mihomo 原生 Rule Provider 自动独立更新。

## Or 前缀自动重命名

可以上传 `rulesets/DIRECT/Custom.list`，脚本会将文件重命名为 `OrCustom.list`，并在一次 GitHub Actions 运行中提交重命名结果和生成的 INI。文件已是 `OrCustom.list` 则不会重复添加前缀。`steam.list` 会变成 `OrSteam.list`。若目标文件已存在会报错以防覆盖。

**注意**：脚本只为未以 `Or` 开头的文件添加前缀、将原首字母大写，并不会将 `my_custom.list` 等任意命名转换为标准大驼峰。推荐新建文件时直接使用 `OrMyCustom.list`。

## 自定义和更新说明

- 修改现有 `.list` 内容：工作流可运行并检查 NoAuto 模板，但生成的 INI 引用 URL 不变；OpenClash 下次更新完整订阅时通过转换服务加载最新 `.list`（转换服务可能存在缓存）。
- 新增/删除 `.list`：工作流自动更新生成的 INI；OpenClash 下次更新完整订阅获得新规则集。
- 修改 `.yaml`：Mihomo 使用 `clash-classic:` Provider 时可按 3600 秒独立更新；若新增/删除 Provider 仍需要主订阅更新。
- ACL4SSR 上游更新：Actions 每六小时检查；OpenClash 仍需更新主订阅。
- 工作流需要 `contents: write` 权限；若 GitHub 禁止 Actions 写入，需在仓库 Actions 设置中授权。

**优先级**：个人规则插入原版 ACL4SSR 第一条规则之前。不要在 `.list` 和 `.yaml` 中同时维护相同域名，避免重复。
