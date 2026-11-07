# unit06 退回意见（仅译文切分口径）

验收时间：主流程本轮全量复核。**其他检查项全部通过**：

- 6 课齐全、key 命名正确、`canonical` 与 `lines[].text` 逐字一致
- role 全在音色表内、英文无中文混入、无超 170 字符句
- 官方正文页逐句命中 92.1%、词覆盖 0.999
- 初检报的「练习题残留」是主流程正则误报（正文原句 *They loved to listen to the singing of the birds.*），**已撤销，不用改**

## 唯一问题

`课文译文.json` 现有 **146** 条，但按当前渲染器的子句正则应为 **144** 条。
英文文字本身**完整无缺、无错位**（拼接后与正文逐字一致），纯粹是切分口径不同：
渲染器按 `(?<=[.!?])\s+(?=[A-Z“"]I?)` 切，
缩写点 `Jules G. Verne` / `O. Henry` 会被切开，而引号后接叙述（`?” The giant…`）、
括号舞台说明（`(He puts…)`）因后随字符不是大写字母/引号**不会**被切开。
条数不齐会导致落地时译文事件数与子句数对不上，成片字幕与译文错位，必须统一。

## 需要改的 6 处（其余 138 条不动）

### 期望第 18–21 条 / 现第 18–19 条
- **应为（4 条）**：
  - `Jules G.`
  - `Verne takes us on an exciting underwater adventure full of discoveries.`
  - `Yesterday, I just finished reading The Gift of the Magi by O.`
  - `Henry.`
- **现为（2 条）**：
  - `Jules G. Verne takes us on an exciting underwater adventure full of discoveries.`
  - `Yesterday, I just finished reading The Gift of the Magi by O. Henry.`

### 期望第 61–61 条 / 现第 59–60 条
- **应为（1 条）**：
  - `“What are you doing here?” The giant got mad and yelled in a deep voice.`
- **现为（2 条）**：
  - `“What are you doing here?”`
  - `The giant got mad and yelled in a deep voice.`

### 期望第 63–63 条 / 现第 62–63 条
- **应为（1 条）**：
  - `You must leave immediately!” The children were frightened and ran away.`
- **现为（2 条）**：
  - `You must leave immediately!”`
  - `The children were frightened and ran away.`

### 期望第 121–121 条 / 现第 121–122 条
- **应为（1 条）**：
  - `Here it is. (He puts the packet of money on the table.)`
- **现为（2 条）**：
  - `Here it is.`
  - `(He puts the packet of money on the table.)`

### 期望第 125–126 条 / 现第 126–127 条
- **应为（2 条）**：
  - `Of course. (She gives him a pen and some paper, and leaves.`
  - `Gillian writes a short note, and then reads it.)`
- **现为（2 条）**：
  - `Of course.`
  - `(She gives him a pen and some paper, and leaves. Gillian writes a short note, and then reads it.)`

### 期望第 136–136 条 / 现第 137–138 条
- **应为（1 条）**：
  - `Could I show it to you?” The king handed the jade back to Lin.`
- **现为（2 条）**：
  - `Could I show it to you?”`
  - `The king handed the jade back to Lin.`

## 改法

把 `课文译文.json` 的 `items` 按下方 144 条清单重排：英文照抄，中文相应合并或拆成对应条数，
`no` 从 1 连续编到 144。**只改这一份文件**，`课文数据.json` 与 `教材基准.json` 完全不用动，
不要改英文原句、不要凭记忆补课本内容。

改完重交 3 个 JSON 即可，主流程下一轮自动复核；不影响其他 7 个单元。

<details><summary>144 条期望英文清单（照抄用）</summary>

```
  1. Li Ming and Jenny are chatting online.
  2. Hey, Li Ming.
  3. We’re learning about different types of literature in our English class this week.
  4. So far, we have read fables and fairy tales.
  5. Oh, fables!
  6. I really enjoy them.
  7. They’re short but meaningful.
  8. Exactly.
  9. I think fables are rich in morals.
 10. One of my favourites is The Fox and the Grapes.
 11. Have you heard of it?
 12. Yes!
 13. It’s a good one.
 14. I also like science fiction.
 15. Have you ever read the novel Twenty Thousand Leagues Under the Sea?
 16. I’m just a quarter of the way into it.
 17. Yes, I love it.
 18. Jules G.
 19. Verne takes us on an exciting underwater adventure full of discoveries.
 20. Yesterday, I just finished reading The Gift of the Magi by O.
 21. Henry.
 22. Ah, I am familiar with that short story too.
 23. In my Chinese class, we’re reading ancient Chinese poems by great poets like Li Bai and Du Fu.
 24. They wrote hundreds of amazing poems.
 25. That sounds fascinating!
 26. I remember Brian is interested in writing poems.
 27. Perhaps you could discuss poetry with him one day.
 28. Really?
 29. I hope he enjoys Chinese poems and finds inspiration in them.
 30. I bet he does!
 31. Literature has so much to offer, and it can open new worlds for us.
 32. Let’s continue learning and exploring its wonders together!
 33. Long ago, there was a kind and honest woodcutter.
 34. One day, when he was cutting wood beside a lake, he lost his axe in the water.
 35. The water was deep, and he could not get his axe back.
 36. He had only one axe, and he needed it to make a living.
 37. He sat down and began to cry.
 38. As he cried, a fairy appeared.
 39. She asked the man what was wrong.
 40. She listened to the woodcutter and felt sorry for him.
 41. But what could she do to help?
 42. Suddenly, she came up with a great idea.
 43. The fairy jumped into the lake and brought back a golden axe.
 44. “Is this the axe you lost?” asked the good fairy.
 45. The man looked at the golden axe and shook his head.
 46. He told the fairy it wasn’t his.
 47. The fairy jumped into the water again and brought back a silver axe.
 48. Once again, the man said that none of the axes were his.
 49. The fairy went down a third time and returned with the woodcutter’s old axe.
 50. “That’s the right one!” said the woodcutter.
 51. The fairy was so happy with the woodcutter’s honesty that she gave him the other two axes as a present.
 52. Honesty truly is the best policy.
 53. Once upon a time, there was a big, beautiful garden in front of a large, empty house.
 54. Its grass was soft and green.
 55. Its trees were filled with singing birds.
 56. Every afternoon after school, children would play in the garden.
 57. They ran in the grass and climbed the trees.
 58. They loved to listen to the singing of the birds.
 59. They felt that they were in a wonderland.
 60. One day, the children were playing in the garden when a giant appeared.
 61. “What are you doing here?” The giant got mad and yelled in a deep voice.
 62. “This is my garden!
 63. You must leave immediately!” The children were frightened and ran away.
 64. The next day, the giant built a high wall around his garden and put up a notice: DO NOT ENTER!
 65. The poor children dared not come again.
 66. The giant was always in his house, watching.
 67. Summer turned to fall and fall turned to winter.
 68. When spring came, the giant noticed that flowers blossomed and birds began to sing across the land.
 69. But in his garden, it was still winter.
 70. The green grass was covered with snow and the cold winds kept the birds away.
 71. “I don’t understand why spring is so late coming to my garden this year,” said the giant.
 72. He felt sad when he looked through the window at his frozen, white garden.
 73. One morning when the giant was lying awake in his bed, he heard lovely music coming through the window.
 74. He thought it must be the king’s musicians passing by.
 75. “Perhaps spring has come at last,” he said when he jumped out of bed and looked outside.
 76. This week in class, we learned to write stories and poems.
 77. We read different kinds of poems, fables, and fairy tales.
 78. I think poems are more interesting than stories because they use creative forms and a small number of words to express strong feelings.
 79. During our class, we read a beautiful Chinese poem called Thoughts on a Tranquil Night by the poet Li Bai.
 80. This poem is about missing home and it painted clear pictures in my mind.
 81. Here’s the poem:
 82. Before my bed a pool of light —
 83. Or can it be hoar-frost on the ground?
 84. Looking up, I find the moon bright;
 85. Bowing, in homesickness I’m drowned.
 86. After learning about this special poem, my teacher encouraged us to try writing our own poems.
 87. At first, I tried to write about my favourite spot by the lake, but it was challenging.
 88. Instead, I wrote a poem about the months.
 89. Here it is:
 90. In April, come he will,
 91. In May, sing all day,
 92. In June, change his tune,
 93. In July, prepare to fly,
 94. In August, go he must!
 95. Writing poems can be challenging, and you should weigh your words, but it’s also lots of fun.
 96. I enjoy expressing my thoughts and feelings through words.
 97. I can’t wait to learn more about poetry in our next class!
 98. A young man’s uncle leaves him one thousand dollars in his will.
 99. What will the young man do with it?
100. In Tolman’s office, Mr Tolman, a lawyer, has just finished reading Gillian’s uncle’s will.
101. Well, there you are.
102. Your uncle wrote his will two months before he died, and now I’ve read it to you.
103. What do you think?
104. (Laughing) It’s not going to be easy to spend a thousand dollars.
105. After spending this cash, you must tell me in writing how you spent it.
106. Will you do that?
107. Yes, I’ll do it.
108. (Giving Gillian a packet) Here’s the money, one thousand dollars.
109. Gillian knows that the uncle’s caretaker, Miss Hayden, got just ten dollars.
110. Compared to that, a thousand is a lot.
111. How should Gillian spend his money?
112. He asks several friends, but doesn’t find the answer.
113. Finally, he decides to return to his uncle’s house.
114. In the living room, Miss Hayden is sitting at a table, writing letters.
115. She looks up when Gillian comes in.
116. I’ve just come from Tolman’s.
117. He found a mistake in the will.
118. He did?
119. My dear old uncle left you a thousand dollars, not ten.
120. Tolman asked me to bring it to you.
121. Here it is. (He puts the packet of money on the table.)
122. (Excited) Oh my!
123. Wow!
124. (Smiling) Can I write a note?
125. Of course. (She gives him a pen and some paper, and leaves.
126. Gillian writes a short note, and then reads it.)
127. “Paid to the best and dearest woman in the world, one thousand dollars.
128. I hope she will be happy forever.”
129. During the Warring States Period, the King of Zhao got an invaluable piece of jade, He Shi Bi.
130. When the King of Qin heard of this, he offered Zhao fifteen cities for the smooth, bright jade.
131. The King of Zhao feared he might get nothing in return.
132. Yet if he refused, Qin might attack Zhao.
133. Lin Xiangru, who was brave and intelligent, was sent to Qin with the jade.
134. The King of Qin was pleased when he saw the jade, but he did not mention the cities at all.
135. Lin said, “Your Majesty, there is a tiny flaw on the jade.
136. Could I show it to you?” The king handed the jade back to Lin.
137. As soon as Lin got the jade, he stepped back to the pillars in the palace, shouting, “You have no intention of giving us those cities, so I’ve taken back the jade.
138. If you use force against me, I’ll smash my head and the jade against this pillar.”
139. To save the jade, the King of Qin apologized, and then showed Lin the cities on the map.
140. But Lin did not believe he would turn them over.
141. He ordered one of his men to secretly take the jade back to Zhao.
142. He himself would stay to face the King of Qin.
143. Although the King of Qin was furious, he had no better choice but to set Lin free.
144. Lin Xiangru and the jade returned to Zhao safely.
```

</details>

---

## 补充（契约 v2）

本轮已把这条口径固化进 `tasks/8b/数据契约.md` **第 4 节**：
子句切分正则 `(?<=[.!?])\s+(?=[A-Z“"]I?)` 现在是硬约定，
`tasks/8b/自检_课文整理.py` 是主流程闸门的同源副本。

改完后在仓库根目录跑一次：

```
python tasks/8b/自检_课文整理.py unit06
```

全绿再提交。脚本会直接告诉你 144 条有没有对齐，不用再等主流程复核。

