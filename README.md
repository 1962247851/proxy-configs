# proxy-configs

个人代理配置、Mihomo 远程规则和订阅转换配置。公开仓库不得保存机场订阅 token、私钥或账号。

## 目录

- `rules/direct.yaml` 自定义直连规则
- `rules/reject.yaml` 自定义拦截规则（示例）
- `rules/proxy.yaml` 自定义代理规则（示例）
- `mihomo/rule-providers.yaml` Mihomo/OpenClash 可合并的**片段**（不是完整配置）
- `subconverter/custom-rulesets.ini` SubConverter-Extended 外部配置中 `[rulesets]` 段的**片段**
- `sub-store/` 预留 JS 覆写

## 使用

1. 把这些文件上传至自己的 GitHub `proxy-configs` 公开仓库，默认分支 `main`。
2. 将文本中的 `USER` 替换成 GitHub 用户名。
3. **两种接入方式择一**，不要重复添加：
   - 方式 A：使用 SubConverter-Extended，将 `subconverter/custom-rulesets.ini` 的三个 `ruleset=` 行合并到现有外部配置 `[rulesets]` 段最前面，保留其他公共规则和最终 `MATCH`；转换后检查生成 YAML 的 `rule-providers`。
   - 方式 B：直接修改 Mihomo 主配置，把 `mihomo/rule-providers.yaml` 中的 provider 条目合并到原 `rule-providers`，把 3 条 `RULE-SET` 插入原 `rules` 的前面（在最终 MATCH 前）。
4. OpenClash 选择 Mihomo/Meta 内核，加载生成/合并后的完整配置。
5. `rule-providers` 使用 `interval: 3600`，运行中的 Mihomo 会定期尝试从 GitHub 刷新，不需要重新转换整个订阅。
6. 在 OpenClash 检查运行配置中实际存在 provider 和 RULE-SET；如启用 OpenClash 覆写功能，请确认没有把顺序改掉。

**注意**：`rules/*.yaml` 是经典 `payload` 格式，不要通过 `ruleprepend` 导入；这里使用 `clash-classic:` 和 Mihomo 原生 RULE-SET。

### 远程地址

`https://raw.githubusercontent.com/USER/proxy-configs/main/rules/direct.yaml`

`https://raw.githubusercontent.com/USER/proxy-configs/main/rules/reject.yaml`

`https://raw.githubusercontent.com/USER/proxy-configs/main/rules/proxy.yaml`

### 校验

可以在本地运行：

```bash
python3 -m pip install pyyaml
python3 - <<'PY'
from pathlib import Path
import yaml
for f in Path('rules').glob('*.yaml'):
    data = yaml.safe_load(f.read_text(encoding='utf-8'))
    assert isinstance(data, dict) and isinstance(data.get('payload'), list) and data['payload'], f
    print(f, len(data['payload']), 'rules OK')
PY
```

完整 Mihomo 配置可以用 `mihomo -t -f config.yaml` 验证（需安装兼容内核）。
