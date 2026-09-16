# 抖音视频转写与分析库

> 自动处理流水线：抖音抓流下载 → ffmpeg 抽音频 → MLX Whisper 本地转写 → 术语清洗 → 结构化分析报告


## 项目说明
本仓库沉淀一批抖音视频的**转写稿与结构化分析报告**，主题覆盖电商带货、自媒体运营、AI/技术实操、知识管理、搞钱思维、人文认知等。所有报告由本地 MLX Whisper 转写 + 人工校准生成，关键数字/案例均做可信度标注。


## 目录结构
```
douyinzongjie/
├── analysis/      # 86 份结构化分析报告（.md）
├── downloads/     # 各视频字幕转写：transcript.txt / .srt / transcript_clean.txt / captured_urls.json
│   └── NN_主题/
├── .gitignore     # 已排除 mp4/wav 大媒体文件与本地 .workbuddy 工作记忆
└── README.md
```

## 处理流水线
1. **抖音抓流下载**：Playwright 驱动真实 Chrome 打开视频页，拦截 `douyinvod` 视频流/音频流直链，ffmpeg 合成（绕过 yt-dlp 403 与验证码墙）。
2. **抽音频**：ffmpeg 提取 16kHz 单声道 wav。
3. **本地转写**：MLX Whisper `large-v3-turbo`（Apple Silicon GPU）。
4. **清洗**：`clean_transcript.py` 术语 / 音译校正。
5. **分析报告**：结构化拆解（核心论点 / 步骤 / 可信度 / 与搞钱主线的落点 / 关联视频）。

## 报告索引（86 份，按主题粗略归类）

### 电商 / 带货 / 短视频运营（33）

- [15个自媒体赛道](analysis/分析报告_15个自媒体赛道.md)
- [24小时涨粉1000冷启动](analysis/分析报告_24小时涨粉1000冷启动.md)
- [29_模仿罗永浩提升表达](analysis/分析报告_29_模仿罗永浩提升表达.md)
- [30_自媒体3时代与变现](analysis/分析报告_30_自媒体3时代与变现.md)
- [90分钟讲透自媒体Vol02上](analysis/分析报告_90分钟讲透自媒体Vol02上.md)
- [AI变现底层逻辑](analysis/分析报告_AI变现底层逻辑.md)
- [从零开始做新媒体](analysis/分析报告_从零开始做新媒体.md)
- [伪交付情绪价值内容变现](analysis/分析报告_伪交付情绪价值内容变现.md)
- [做自媒体五个动作要做对](analysis/分析报告_做自媒体五个动作要做对.md)
- [做自媒体你没听过的事](analysis/分析报告_做自媒体你没听过的事.md)
- [关于抖音的100个知识点](analysis/分析报告_关于抖音的100个知识点.md)
- [口碑营销四大误区拖垮生意](analysis/分析报告_口碑营销四大误区拖垮生意.md)
- [好内容逻辑拆解](analysis/分析报告_好内容逻辑拆解.md)
- [工厂行业短视频运营](analysis/分析报告_工厂行业短视频运营.md)
- [带货爆单选题](analysis/分析报告_带货爆单选题.md)
- [带货结构](analysis/分析报告_带货结构.md)
- [带货视频钩子](analysis/分析报告_带货视频钩子.md)
- [带货选题逻辑](analysis/分析报告_带货选题逻辑.md)
- [平台本月更新不知情事](analysis/分析报告_平台本月更新不知情事.md)
- [我的短视频系统](analysis/分析报告_我的短视频系统.md)
- [抖音改版系列18自媒体变现](analysis/分析报告_抖音改版系列18自媒体变现.md)
- [换个发布入口发视频换买菜钱](analysis/分析报告_换个发布入口发视频换买菜钱.md)
- [播放量掉到200三步诊断](analysis/分析报告_播放量掉到200三步诊断.md)
- [普通人拍视频三件事](analysis/分析报告_普通人拍视频三件事.md)
- [每日一镜578别说自己没内容拍](analysis/分析报告_每日一镜578别说自己没内容拍.md)
- [爆款三要素](analysis/分析报告_爆款三要素.md)
- [爆款是否是一种能力](analysis/分析报告_爆款是否是一种能力.md)
- [知识付费成交文案](analysis/分析报告_知识付费成交文案.md)
- [知识付费成交文案四大真相](analysis/分析报告_知识付费成交文案四大真相.md)
- [短视频变现成长计划](analysis/分析报告_短视频变现成长计划.md)
- [自媒体的建议](analysis/分析报告_自媒体的建议.md)
- [视频没人看因为知道太多](analysis/分析报告_视频没人看因为知道太多.md)
- [转化视频死在掏兜感](analysis/分析报告_转化视频死在掏兜感.md)

### 知识管理 / 学习法（9）

- [Obsidian新手教程](analysis/分析报告_Obsidian新手教程.md)
- [WorkBuddy搭个人知识库](analysis/分析报告_WorkBuddy搭个人知识库.md)
- [大脑喜欢这样学](analysis/分析报告_大脑喜欢这样学.md)
- [框架学习法](analysis/分析报告_框架学习法.md)
- [知识库无用论](analysis/分析报告_知识库无用论.md)
- [笔记该从AIagent淘汰](analysis/分析报告_笔记该从AIagent淘汰.md)
- [英语学习的第一性原理](analysis/分析报告_英语学习的第一性原理.md)
- [训练自学能力WorkBuddySkill](analysis/分析报告_训练自学能力WorkBuddySkill.md)
- [费曼学习法](analysis/分析报告_费曼学习法.md)

### AI / 技术实操（19）

- [3加6公式看懂所有Agent](analysis/分析报告_3加6公式看懂所有Agent.md)
- [AI做PPT工作流](analysis/分析报告_AI做PPT工作流.md)
- [AI博主赚钱](analysis/分析报告_AI博主赚钱.md)
- [AI改造蓝海赛道](analysis/分析报告_AI改造蓝海赛道.md)
- [AI改造高客单交付](analysis/分析报告_AI改造高客单交付.md)
- [AI漫剧教程零基础](analysis/分析报告_AI漫剧教程零基础.md)
- [AI自动剪辑_剪映Agent](analysis/分析报告_AI自动剪辑_剪映Agent.md)
- [Codex进阶教程](analysis/分析报告_Codex进阶教程.md)
- [MCP协议爆火](analysis/分析报告_MCP协议爆火.md)
- [Mac43个设置](analysis/分析报告_Mac43个设置.md)
- [VibeCoding小程序技术栈](analysis/分析报告_VibeCoding小程序技术栈.md)
- [VibeCoding运维](analysis/分析报告_VibeCoding运维.md)
- [个人小程序收款](analysis/分析报告_个人小程序收款.md)
- [大学生数码好物](analysis/分析报告_大学生数码好物.md)
- [如何让AI在同一会话内对话超过5000轮](analysis/分析报告_如何让AI在同一会话内对话超过5000轮.md)
- [新手做AI服务最好市场](analysis/分析报告_新手做AI服务最好市场.md)
- [新时代二道贩子怎么干](analysis/分析报告_新时代二道贩子怎么干.md)
- [普通人用AI赚钱](analysis/分析报告_普通人用AI赚钱.md)
- [量化免费数据源](analysis/分析报告_量化免费数据源.md)

### 搞钱 / 副业 / 思维破局（13）

- [31_搞钱书三本救命](analysis/分析报告_31_搞钱书三本救命.md)
- [不上班之后人生能重启吗](analysis/分析报告_不上班之后人生能重启吗.md)
- [不上班在家赚小钱](analysis/分析报告_不上班在家赚小钱.md)
- [不上班的思维盲区](analysis/分析报告_不上班的思维盲区.md)
- [争点理论选题](analysis/分析报告_争点理论选题.md)
- [信息差发现大势机会](analysis/分析报告_信息差发现大势机会.md)
- [变穷_赚钱_认知](analysis/分析报告_变穷_赚钱_认知.md)
- [吸引有钱人回归人本身](analysis/分析报告_吸引有钱人回归人本身.md)
- [姜胡说先做小事](analysis/分析报告_姜胡说先做小事.md)
- [姜胡说赚钱法](analysis/分析报告_姜胡说赚钱法.md)
- [改变命运设计不可能失败结构](analysis/分析报告_改变命运设计不可能失败结构.md)
- [最简单的才是最难的](analysis/分析报告_最简单的才是最难的.md)
- [走窄门技能是工具箱](analysis/分析报告_走窄门技能是工具箱.md)

### 人文 / 认知 / 社会（11）

- [人元大道九层炼心文终经](analysis/分析报告_人元大道九层炼心文终经.md)
- [债务纠纷](analysis/分析报告_债务纠纷.md)
- [劳动仲裁败诉原因](analysis/分析报告_劳动仲裁败诉原因.md)
- [对工作说不](analysis/分析报告_对工作说不.md)
- [意识搬运师宇宙飞船](analysis/分析报告_意识搬运师宇宙飞船.md)
- [换个角度拆解执行力](analysis/分析报告_换个角度拆解执行力.md)
- [王小波教会我们什么](analysis/分析报告_王小波教会我们什么.md)
- [砚山县民族中学校长讲话](analysis/分析报告_砚山县民族中学校长讲话.md)
- [穷忙陷阱](analysis/分析报告_穷忙陷阱.md)
- [自律与概率](analysis/分析报告_自律与概率.md)
- [谁在操控你的人生](analysis/分析报告_谁在操控你的人生.md)

### 其他（1）

- [鹤老师自媒体实操教程](analysis/分析报告_鹤老师自媒体实操教程.md)

## 说明与免责
- 原始视频 / 音频（约 5.1GB）因 GitHub 单文件 100MB 限制未入库，仅保留字幕文本与报告。
- 报告内容基于视频口播转写，部分数字 / 案例已做可信度分层；抖音内容版权归原作者所有，本仓库仅作个人学习整理。
- 本地工作记忆（`.workbuddy/`）未公开。
