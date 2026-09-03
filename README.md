# OneKey 小手册

面向普通用户的 OneKey 产品与使用整理站。

## 项目定位

- 独立整理站，不代表 OneKey 官方
- 面向新手，内容简洁、清晰、易上手
- 公开访问，不设置登录、付费墙或访问限制
- 内容基于 OneKey 官方公开资料重新整理

## 本地预览

本项目是零依赖静态网站，可直接运行：

```bash
python3 -m http.server 8080
```

然后打开 http://localhost:8080

## 目录规划

```text
onekey-xiaoshouce/
├── index.html              # 首页
├── styles.css              # 全站样式
├── content-plan.md         # 内容规划
├── articles/               # 后续整理后的文章
├── assets/                 # 图片与插图
└── README.md
```

## 部署方向

代码和文章放在 GitHub，网站可部署到静态托管平台。域名 `onekey.beauty` 在实际部署后再绑定，DNS 与托管平台配置不写入仓库。

上线前需要使用中国大陆多个地区实际测试访问速度和可用性。域名本身不能保证中国大陆访问稳定，后续根据测试结果决定是否增加香港/新加坡源站、CDN 或镜像方案。
