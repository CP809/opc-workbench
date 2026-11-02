# 一人公司工作台 - 项目笔记

## 每日知识模块（原资讯已替换）
- 内容源：knowledge.json 知识库（AI 基础 30 条 + 计算机基础 40 条），由 sync_data.py 每日按日期轮换生成。
- 用户要求：不要 IT之家、不要泛娱乐热榜；用「基础知识」替换掉资讯热榜。
- 分类：AI 基础 / 计算机基础；前端 index.html 渲染 x.source，无链接卡片。
- 每日展示：AI 15 条 + 计算机 20 条。

## 每日更新（自动化）
- automation f81c31dc-5691-46ad-b8ae-12a3ad4bb9cd「备份·电脑开机才跑」：抓数 → 推 GitHub → 重新发布。
- 部署地址：https://93e14aa60a70466f9fe608234a38925e.app.workbuddy.host
- 入口 index.html。

## 已知阻塞：本机 GitHub 推送链路不可用
- 环境变量 `GH_TOKEN` 在本机 User / Machine / Process 三级均未配置，`.workbuddy/gh_upload.py` 第 30 行 `os.environ["GH_TOKEN"]` 直接 KeyError。
- 与 token 过期（401/403）是两回事：这是变量根本不存在。修复方式 `setx GH_TOKEN <classic PAT>`（scopes=repo,workflow）后重开终端。
- 未修复前，每日自动化只能完成「抓数 + 静态发布」，GitHub 仓库与 Actions 不会更新；GitHub Actions 自身的定时链路（UTC 23:30）不受影响，仍会自行抓数并提交。
- 本机 curl 连 github.com 报 schannel 证书吊销错误，所有 GitHub 网络操作必须用 Python urllib。

## Service Worker 版本号约定
- data.js 在 SW 的 ASSETS 预缓存列表内 → **每次数据更新都要同步升 CACHE 版本号**（opc-vN）。
- 当前版本：opc-v14（2026-10-20）。
