# 抖音直播弹幕爬取 python 实现

## 环境

```
python 3.11.4
```

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 运行效果

```
2024-01-26 19:10:59 [入场] 用户2214465713176 进入直播间  [头像 ]['https://p6.douyinpic.com/aweme/100x100/aweme-avatar/mosaic-legacy_3797_2889309425.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 你猜我猜猜不猜 进入直播间  [头像 ]['https://p26.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-avt-0015_ab880787efa2aba0d5fa737bf2ca16d6.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 妮妮 进入直播间  [头像 ]['https://p26.douyinpic.com/aweme/100x100/aweme-avatar/mosaic-legacy_3793_3131589739.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 光明 进入直播间  [头像 ]['https://p3.douyinpic.com/aweme/100x100/aweme-avatar/mosaic-legacy_3791_5035712059.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 孙大爷 进入直播间  [头像 ]['https://p6.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_oUwgIaCfcnABeaAzAf8WB7LAFBGAPEdSQabELD.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 往事随风丶 进入直播间  [头像 ]['https://p3.douyinpic.com/aweme/100x100/aweme-avatar/mosaic-legacy_2d0950006e1b03d30e3a4.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 慌伴👍 进入直播间  [头像 ]['https://p11.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_e0f7bef54cee4b7997018222b8749c65.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 感恩 进入直播间  [头像 ]['https://p3.douyinpic.com/aweme/100x100/aweme-avatar/mosaic-legacy_3791_5035712059.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 四子 进入直播间  [头像 ]['https://p11.douyinpic.com/aweme/100x100/aweme-avatar/mosaic-legacy_3795_3047680722.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 小康之家建筑节能科技有限公司 进入直播间  [头像 ]['https://p11.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813c001_bc456b3379784e85831c68aa1b39e08b.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 阿迪达标 进入直播间  [头像 ]['https://p26.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813c001_ocKAAJyIaxKztCy5g1COXthGfAAeCATGtBrXAE.jpeg?from=3067671334']
2024-01-26 19:11:02 [弹幕] 时光煮酒: 剃须刀介绍一下
2024-01-26 19:10:59 [入场] 用户6763634423749 进入直播间  [头像 ]['https://p11.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_8a619a5e36c049a0978a37d3bf3f5cc2.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 感恩有涵 进入直播间  [头像 ]['https://p3.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_1b693ee347634c72a5573d8f406182e8.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 勇往直前 进入直播间  [头像 ]['https://p26.douyinpic.com/aweme/100x100/90eb002843357368477e.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 小石头 进入直播间  [头像 ]['https://p3.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_66c048003b054b22963d3fd62a091a2e.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 好好工作，好好生活。 进入直播间  [头像 ]['https://p6.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_5a5603a4e3e944978e6e736d86c03386.jpeg?from=3067671334']
2024-01-26 19:10:59 [入场] 知足常乐_2bys9 进入直播间  [头像 ]['https://q.qlogo.cn/qqapp/101302986/03EFFD3160ADA441742B3F6E6B21F32A/100']
2024-01-26 19:11:04 [弹幕] ^_^: 为什么这里的人戴头巾
2024-01-26 19:11:00 [点赞] 时尚水瓶姐，爱生活，爱时尚，: 点赞 * 7
2024-01-26 19:11:00 [入场] 用户7496945788720 进入直播间  [头像 ]['https://p11.douyinpic.com/aweme/100x100/aweme-avatar/douyin-user-file_9eea8e5430a89745660d1f5bc639bbe3.jpeg?from=3067671334']
2024-01-26 19:11:00 [入场] 没 进入直播间  [头像 ]['https://p11.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813_472808e0abca429380e1ea9a47c0b446.jpeg?from=3067671334']
2024-01-26 19:11:00 [入场] 流年似水- 进入直播间  [头像 ]['https://p3.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813c001_ooCezhgjERyAOjAqICmA6CfAu0nyZANzEMARNS.jpeg?from=3067671334']
```

## 打包

```bash
## MacOS
pyinstaller main.py --add-data "static/*:static/" # 打包成文件夹

## Windows
pyinstaller main.py --add-data "static/*;static/" # 打包成文件夹
```

## 配置位置（包括URL）

```
static/config_dev.yml 
```

## ENV设置

```bash
export DY_LIVE_ENV="prod" ## 生效配置 config-<DY_LIVE_ENV>.yml
```

# 鸣谢

感谢 [ConcaXu](https://github.com/ConcaXu) 为本项目的贡献和支持。

<div style="display: flex; align-items: center;">
  <a href="https://github.com/ConcaXu" target="_blank"><img src="https://avatars.githubusercontent.com/u/71932317?s=400&u=83d5623cc2765fe5ff750187329448f1efc2b506&v=4" width="100" height="100" style="border-radius: 50%; margin-right: 20px;"></a>
  <a align="right">个人主页 <a href='https://github.com/ConcaXu'] .</p>
</div>
