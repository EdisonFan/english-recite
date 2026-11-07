# 八下 · 课文整理任务卡（8 个任务）

> 分发方式：把 `tasks/README.md` + `tasks/任务包_课文整理.md` + `tasks/数据契约.md`
> 连同**本文件里指定的那一行**一起发给一个 AI，并明确告诉它 `unitNN`。
> 一个 AI 领一个单元（6 个板块），8 个任务可完全并行。
> 输入文件在 `pages/8b/unitNN.txt`，成果写到 `results/8b/unitNN/`。

---

## 通用约定

- 册次：**冀教版英语 · 八年级下册（2026春版）**，2022 年版课标修订教材
- 每单元固定 **6 个板块**：Lesson 1~5 + 单元拓展（Understanding cultures）
- 正文页 = 单元扉页 +1 / +3 / +5 / +7 / +9 / +11，共 6 页，已导出到 `unitNN.txt`
- 版本红线：若正文里出现 *Back to school*、*It's Show Time!*、
  Lessons 1~48 连续编号、或封面写「衔接三年级起点」，**立刻停下并报告旧版**
- 成果：3 个 JSON，见 `数据契约.md`

---

## Unit 01 · `unit01.txt`

**单元标题**：Spring is coming!（P1–14） · 输入 `pages/8b/unit01.txt` · 输出 `results/8b/unit01/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Planting trees |
| Lesson 2 | It's getting warmer! |
| Lesson 3 | The Spring City |
| Lesson 4 | Stories about spring |
| Lesson 5 | Jeremy's observation diary |
| 单元拓展 | The 24 solar terms |

## Unit 02 · `unit02.txt`

**单元标题**：Safety（P15–28） · 输入 `pages/8b/unit02.txt` · 输出 `results/8b/unit02/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Be careful! |
| Lesson 2 | Safety education |
| Lesson 3 | My helmet saved my life! |
| Lesson 4 | An accident on the street |
| Lesson 5 | Home safety |
| 单元拓展 | Being cybersafe |

## Unit 03 · `unit03.txt`

**单元标题**：Amazing sports（P29–42） · 输入 `pages/8b/unit03.txt` · 输出 `results/8b/unit03/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | What's your favourite sport? |
| Lesson 2 | National sport |
| Lesson 3 | Dream team |
| Lesson 4 | Never giving up |
| Lesson 5 | Classroom Olympics |
| 单元拓展 | The Olympic Games |

## Unit 04 · `unit04.txt`

**单元标题**：Rules make for a better life!（P43–56） · 输入 `pages/8b/unit04.txt` · 输出 `results/8b/unit04/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Signs in public places |
| Lesson 2 | Traffic laws help! |
| Lesson 3 | Spoken and unspoken rules |
| Lesson 4 | Personal boundaries |
| Lesson 5 | Public rules |
| 单元拓展 | Funny international laws |

## Unit 05 · `unit05.txt`

**单元标题**：Great inventions（P57–70） · 输入 `pages/8b/unit05.txt` · 输出 `results/8b/unit05/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Inventions are great! |
| Lesson 2 | Ways of travelling |
| Lesson 3 | Computers and the internet |
| Lesson 4 | Thank you, Mr Pasteur! |
| Lesson 5 | Refrigerator timeline |
| 单元拓展 | Great inventions of ancient China |

## Unit 06 · `unit06.txt`

**单元标题**：I love literature!（P71–84） · 输入 `pages/8b/unit06.txt` · 输出 `results/8b/unit06/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Exploring literature |
| Lesson 2 | The woodcutter fable |
| Lesson 3 | The Giant |
| Lesson 4 | Writing a poem |
| Lesson 5 | One thousand dollars |
| 单元拓展 | Return the jade intact to Zhao |

## Unit 07 · `unit07.txt`

**单元标题**：The value of money（P85–98） · 输入 `pages/8b/unit07.txt` · 输出 `results/8b/unit07/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Money in history |
| Lesson 2 | What do you with money?（目录如此，疑似缺词，**按正文页实际写法填，并写进 inferred**） |
| Lesson 3 | Money talks |
| Lesson 4 | Needs or wants? |
| Lesson 5 | Managing your money |
| 单元拓展 | Money: A fair medium of exchange |

## Unit 08 · `unit08.txt`

**单元标题**：Natural disasters（P99–112） · 输入 `pages/8b/unit08.txt` · 输出 `results/8b/unit08/`

| 板块 | 标题 |
|---|---|
| Lesson 1 | Disaster safety tips |
| Lesson 2 | Staying safe in an earthquake |
| Lesson 3 | Secondary disasters |
| Lesson 4 | Natural disasters are dangerous! |
| Lesson 5 | Let's do an escape drill! |
| 单元拓展 | Measures to prevent floods |

---

## 标题口径说明

上表标题来自课本 Contents 页。板块标题可能与正文页上的写法略有出入
（例如语法栏小标题、写作任务提示会跟在后面），**以正文页实际语篇标题为准**，
目录里跟着课标题的语法名称（如 *Adverbial clauses of time*）和写作任务
（如 *Write about the spring*）**不是课标题，不要写进 `title`**。
