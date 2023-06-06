# LiteClashProMan

生成并更新 clash 配置文件，并提供 http 下载和规则文件镜像下载。

## 说明

本项目使用 `配置模板` 以及节点的 `订阅链接` 生成多种不同的配置文件，也可以将多个订阅中的节点整合至一个配置文件中~~但会导致部分功能丧失~~。

## 快速上手

安装依赖（推荐使用pipx）

```bash
pip install liteclashproman
```

运行程序

```bash
# 可以通过 -c 指定特定的配置文件
# lcpm -c specific_config.yaml
# 未添加 -c 时，默认读取当前目录下的 config.yaml 文件
lcpm # 等效于 lcpm -c config.yaml
```

## 项目配置文件

参考源代码中的 [模板](./LiteClashProMan/static/config.exp.yaml)

### 配置模板(template)

位于 `/data/template` 文件夹的半成品配置文件，在每日的更新中会被填入订阅节点并生成配置文件，存放于 `/data` 文件夹下。

您可以仿照 `/static/template` 中预设的默认模板文件和 [clash文档](https://github.com/Dreamacro/clash/wiki/Configuration) 创建自己的模板。

### 订阅链接(subscribe)

通常由服务商所提供，以获取节点信息的订阅链接。如果您愿意临时提供订阅链接以供开发，可以联系开发者进行更多服务商适配。

目前支持的服务商/订阅方式:

- [Just My Socks](https://justmysocks3.net/members/index.php)
  - 类型： `jms`
  - 特殊配置项：
    - counter：节点的剩余流量API
- 通用的Clash订阅地址，通过联网下载获取 (ClashSub)
- 通用的Clash配置文件，通过本地文件获取 (ClashFile)

计划支持的提供商/订阅方式:

- 单独的ss节点
- 单独的ssr节点

### 规则集(ruleset)

或称规则提供者(rule-provider)，是一系列域名或应用程序的列表，可以用于规则的编写。

本项目默认模板使用的规则集来源于 [@Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)，于每日 22:30(UTC) / 06:30(UTC+8) 使用 GitHub Action 自动生成，因此本项目的定时更新也设定为其后5分钟更新。

### 特色功能

#### 规则集的本地缓存

在部分地区，直接访问 GitHub 获取规则集是较为困难和耗时的行为，因此由配置模板生成配置文件时会将其中的规则集下载至本地并替换配置文件中的下载链接，使规则文件的下载更加高效稳定。

当然，您可以自由的在配置文件中添加不属于默认规则集以外的链接，只需要注意：在启用的规则文件中的规则集若出现**重复的文件名**，将会只保留**靠后**的规则集的文件，因此请务必注意不要出现**不同的文件但文件名相同**的情况。

### 剩余流量及租期

部分服务商会提供接口供用户查询剩余流量及到期时间，在 [Clash for Windows](https://github.com/Fndroid/clash_for_windows_pkg/releases) 或 [Clash Meta for Android
](https://github.com/MetaCubeX/ClashMetaForAndroid)中可以通过 `Header` 中的信息将上述信息展示在配置文件界面，若您的服务商提供了接口且在配置文件中**仅启用了一个订阅**，那么您可以在获取配置文件时自动额外取得这些信息。
