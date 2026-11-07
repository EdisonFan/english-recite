# 成果提交区

每个单元一个目录 `unit01/` … `unit08/`，**只由负责该单元的 AI 写入**。

## 目录里应该有什么

```
results/8b/unitNN/
├── 课文数据.json
├── 教材基准.json
└── 课文译文.json
```

恰好 3 个文件。字段见 `tasks/8b/数据契约.md`，整理规则见 `tasks/8b/任务包_课文整理.md`。

## 不要放

- 不要放 PDF、图片、音频、视频、脚本、临时文件
- 不要放 `DONE`、`CLAIM` 之类的标记文件（认领与完成状态由主流程写在 `status.json`）
- 不要放解释性 Markdown；需要说明的内容一律写进 JSON 的 `inferred` 字段
- 不要修改 `status.json`、`REJECT.md` 或别人的 `unitNN/`

## 提交节奏

一次提交只放自己那 3 个 JSON 即可。主流程每轮接手时会扫描新提交并跑校验，
结果写进 `status.json`；不合格会在你的目录放 `REJECT.md`，改完重新提交。
