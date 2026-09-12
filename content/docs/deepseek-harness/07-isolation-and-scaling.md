---
title: 第七章 租户隔离与规模化加固
linkTitle: 租户隔离与规模化加固
description: 回环租户隔离的陷阱与 O(n) 实现、容器化两种形态的坑、千用户规模的选型与容量规划、按需启停策略与上线核对清单
weight: 137
---

# 租户隔离与规模化加固

上一章的路线 B 到 D 都有一个共同的隐蔽漏洞：**所有 dsh 实例都监听 `127.0.0.1`，而同一个内核里任何 uid 都能连回环的任意端口。** 本章先补上这块，再讨论用户数上千之后哪些结论会翻。

## 最容易漏掉的一步：回环租户隔离 {#loopback}

网关做得再严密，用户也根本不必经过它——alice 的 Agent 可以自己执行：

```bash
curl 127.0.0.1:3102        # 直连 bob 的实例，绕过网关的登录认证
```

所以必须在**内核层按 UID 切断跨租户的回环访问**。这一步不做，前面的认证网关就是纸糊的。

### 反面做法：枚举「别人的端口」

最直觉的写法是「对每个用户，拒绝访问其他每一个用户的端口」：

```bash
# 反面教材
iptables -A DSH-GUARD -m owner --uid-owner dsh-alice -p tcp -d 127.0.0.1 --dport 3102 -j REJECT
iptables -A DSH-GUARD -m owner --uid-owner dsh-alice -p tcp -d 127.0.0.1 --dport 3103 -j REJECT
# ... 对 bob / carol / ... 重复
```

规则数是 **O(n²)**，用户一多就失控：

| 用户数 | 规则条数 | 后果 |
| --- | --- | --- |
| 100 | 10,000 | 可用 |
| 200 | 40,000 | 开始变慢 |
| 1000 | **约 1,000,000** | 装载数分钟、占约 200MB 内核内存、**每个出站包平均扫 50 万条规则** |

按每条约 20ns 估算，包均开销约 10ms。一个页面 60 请求 × 8 包 = 480 个包 → **单次加载凭空多出数秒延迟**。这是内核态开销，加机器无效。

### 正确做法一：每用户一条子链（O(n)）

不枚举邻居端口，而是用**一条子链表达该用户的全部回环权限**：先放行自己的端口，再拒绝其余全部回环。

```bash
# 派发：命中该 uid 的包跳进它的子链
iptables -A DSH-GUARD -m owner --uid-owner dsh-alice -j DSH-U-alice

# 子链：几条规则表达完整语义
iptables -A DSH-U-alice -p tcp -d 127.0.0.0/8 --dport 3101 -j RETURN   # 自己的实例，放行
iptables -A DSH-U-alice -p udp -d 127.0.0.0/8 --dport 53   -j RETURN   # DNS，放行
iptables -A DSH-U-alice -p tcp -d 127.0.0.0/8 --dport 53   -j RETURN
iptables -A DSH-U-alice -p tcp -d 127.0.0.0/8 --dport 3100 -j REJECT   # 网关，禁止直连
iptables -A DSH-U-alice -d 127.0.0.0/8                     -j REJECT   # 其余回环，禁止
iptables -A DSH-U-alice -j RETURN                                      # 非回环（模型 API）放行
```

规则数降到约 7n：**1000 用户约 7000 条**，扫描开销回到微秒级。三个容易踩的细节：

1. **用 `127.0.0.0/8` 而不是 `127.0.0.1`**——只写单地址时，用户改用 `127.0.0.2` 之类的别名就能绕过。
2. **必须放行 DNS**——不加这两条会把 `systemd-resolved`（监听 127.0.0.53）一起掐掉，症状是「实例能启动、但调不通模型 API」，非常难排查。
3. **IPv6 要单独做一遍**（`ip6tables` + `::1/128`）。如果 dsh 同时监听了 `[::1]`，只做 IPv4 等于没做隔离。

规则默认不持久化，需要 `netfilter-persistent` 保存或挂到网关服务的 `ExecStartPost`，**并在每次增删用户后重跑**。

### 正确做法二：每用户一个网络命名空间（O(1)）

更彻底的办法是让每个实例活在自己的 network namespace 里：alice 的 netns 内只有她自己的 loopback，`curl 127.0.0.1:<任意端口>` 只可能命中自己的进程，**零 iptables 规则**，隔离由内核网络栈保证。

代价是网关无法直接访问实例的回环地址，需要在每个 netns 内放一个极小的回环中继：

顺序有讲究，四步缺一不可：

```bash
NAME=alice
TARGET_UID=$(id -u "dsh-$NAME")     # 注意：不要用 $UID！它是 bash 只读内置变量，
                                    # 取的是「执行脚本的人」的 uid，会把实例跑成 root
RELAY_IP=10.200.0.2                 # netns 内侧地址
HOST_IP=10.200.0.1                  # 宿主侧地址

# ① 建 netns，并把回环网卡拉起来
#    新建的 netns 里 lo 默认 DOWN，不 up 的话后面绑定 127.0.0.1 会直接失败
ip netns add "dsh-$NAME"
ip netns exec "dsh-$NAME" ip link set lo up

# ② 建 veth pair 打通宿主与 netns（这一步才是 10.200.0.x 的来源）
ip link add "veth-$NAME" type veth peer name "veth-$NAME-br"
ip link set "veth-$NAME" netns "dsh-$NAME"
ip netns exec "dsh-$NAME" ip addr add "$RELAY_IP/30" dev "veth-$NAME"
ip netns exec "dsh-$NAME" ip link set "veth-$NAME" up
ip addr add "$HOST_IP/30" dev "veth-$NAME-br"
ip link set "veth-$NAME-br" up

# ③ netns 内启动实例（仍只监听 127.0.0.1，符合硬约束）
ip netns exec "dsh-$NAME" setpriv --reuid="$TARGET_UID" --regid="$TARGET_UID" --clear-groups \
  env HOME=/data/users/$NAME DSH_HOME=/data/users/$NAME dsh --profile web --port 3101

# ④ netns 内挂中继：veth 地址 → 回环端口
ip netns exec "dsh-$NAME" socat \
  TCP-LISTEN:13101,fork,reuseaddr,bind="$RELAY_IP" TCP:127.0.0.1:3101
```

网关改为连接 `10.200.0.2:13101`（宿主侧经 veth 可达），上游 `Host` 仍改写成回环地址。这样做顺带消除了「规则忘记重建」这类人为故障——而这件事容器和 K8s 是免费提供的，这也是它们在规模化场景下的真正价值。

> [!WARNING]
> 中继本身是一个**新的攻击面**：它监听在 veth 地址上，netns 内的任何进程（包括用户自己跑的 Agent）都能直连 `10.200.0.2:13101` 而不经过网关的认证。这不要紧——因为它只通向**该用户自己的** 3101 端口，跨租户访问在 netns 边界就已被切断。但不要把 socat 绑到 `0.0.0.0`，否则等于把实例暴露给宿主上的其他 netns。

## 容器化的两种形态与陷阱 {#docker}

### 形态 C：单容器内建多个 Linux 用户

可行，而且文件与会话隔离是**真实**的（uid 隔离由内核强制，与「容器内」还是「裸机」无关）。换来一份 compose、一条命令、一个数据卷、环境完全可复现。但它默认丢掉三样东西：

| 缺失项 | 后果 | 补法 |
| --- | --- | --- |
| 单 cgroup，无 per-user 配额 | 一个人跑满，全员饿死 | cgroup v2 手工分组 `memory.max` / `cpu.max` |
| 容器内共享 `127.0.0.1` | 用户可绕过网关直连他人端口 | 容器内 iptables + `NET_ADMIN` |
| 单容器故障域 | 容器重启 / OOM，全员断线 | 接受并安排低峰升级，或改用形态 D |

```yaml
cap_add: [NET_ADMIN]        # 只作用于本容器 netns，不影响宿主机
environment:
  DSH_LOOPBACK_GUARD: "1"
```

> [!WARNING]
> **宿主机的 iptables 看不到容器内部回环流量**，回环隔离只能在容器自己的 network namespace 里下规则。另外容器内的 root（网关进程、监管进程、`docker exec`）能读所有用户数据——形态 C 的安全边界是「用户之间互不可见」，不是「防运维」。这个前提必须写进团队的安全说明。

### 形态 D：一用户一容器

配额用 compose 原生 `mem_limit` / `cpus`，故障域天然分开。但有一个必须记住的陷阱：

```yaml
dsh-alice:
  network_mode: "service:dsh-gateway"    # 让容器共享网关的网络命名空间
```

用这个写法是因为 dsh 拒绝绑定 `0.0.0.0`，网关没法跨 bridge 访问实例的回环。代价是**用户容器依附于网关容器创建时的网络命名空间**：

> [!WARNING]
> 重建网关容器后，用户容器不会自动跟随，只会继续引用已消失的命名空间。必须**删除并重建**用户容器，`restart` 无效：
>
> ```bash
> docker compose up -d --force-recreate dsh-gateway
> docker compose up -d --force-recreate dsh-alice dsh-bob
> ```

还要注意：`network_mode: service:网关` 让所有用户容器**共享同一个 netns**，于是「共享回环」的问题原样回来了——这正是下一节结论的由来。

## 扩容到 1000 人 {#scale}

规模一上来，「能跑」的方案会直接失效。这不是调优问题，是架构问题。

### 三条缩放定律 {#laws}

**定律一：共享运行时 + 可区分 uid 时，隔离规则必须做成 O(n)；uid 不可区分时，隔离根本无从下手。**

先澄清一处容易误读的地方：**「共享 netns」本身不是死罪**。上一节的 O(n) 子链方案正是为共享 netns 设计的——1000 人只要约 7000 条规则，完全可以接受。真正把形态 D 判死刑的是另一件事：

**形态 D 里所有用户容器共享 netns，而容器内进程的用户身份彼此不可区分。** O(n) 子链完全依赖 `-m owner --uid-owner <uid>` 把包归属到具体用户；一旦大家是同一个 uid（容器默认都以 root 或同一个固定 uid 运行），这条匹配就失效了——规则分不清这个包是 alice 的还是 bob 的。此时只剩两条路：

- 退回 O(n²) 的「枚举别人的端口」写法（1000 人 = 100 万条，上一节已算过，不可用）；
- 或者干脆不做回环隔离。

**所以准确的表述是：共享 netns 且 uid 可区分（形态 B、C）时，用 O(n) 子链可以撑到千人；共享 netns 且 uid 不可区分（形态 D 的 `network_mode: service:网关` 写法）时，在千人规模必须否决。** 形态 D 想活下来，得放弃共享 netns，改用让每个容器拥有独立 netns 的编排方式（也就是方案 F 的每用户一 Pod）。

**定律二：常驻实例的内存是 O(n)。** dsh 实例是 Node.js Agent 运行时，空载 RSS 约 150~250MB，干活时 400MB~1.5GB：

```text
1000 个常驻实例 × 0.25GB（最乐观的空载）≈ 250GB
```

**定律三：手工账号管理的成本是 O(n)。** 1000 人意味着每天都有入职/离职/忘密码事件，人肉 `userctl add` 必然导致：离职账号长期存活、密码重置变成工单瓶颈、零审计记录。

### 各方案在每个量级的承载能力 {#matrix}

上一章定义了 A~D 四条基础路线和 E（SSO 叠加层）。到了千人规模还要再引入一条：

> **方案 F：Kubernetes，每用户一 Pod。** 它不在上一章的候选里，是因为 K8s 本身就是一套平台成本——几十人规模用它不划算。但在千人规模它是唯一「每用户独立 netns + 独立 PVC 子路径 + NetworkPolicy 禁互访」三项都天然具备的方案，所以在这里正式登场。

| 方案 | 100 人 | 300 人 | 1000 人 |
| --- | --- | --- | --- |
| A 单密码反代 | 不可用 | 不可用 | 不可用 |
| B 裸机多用户 | 可用 | 需改造 | 需改造 |
| C 单容器多用户 | 勉强 | 不可用 | 不可用 |
| D 一用户一容器（共享 netns） | 可用 | 勉强 | 不可用 |
| F Kubernetes（每用户一 Pod） | 可用 | 可用 | **首选** |

**千人规模下的结论：有 K8s 平台就用方案 F（每用户一 Pod，各自独立 netns + 独占 PVC 子路径 + NetworkPolicy 禁互访），没有就用路线 B 的规模修正版，并在两者前面强制叠加 SSO。**

路线 C 被否决是四处硬伤叠加：单 cgroup 无法归因、回环 O(n²)、单故障域（重启即全员断线）、单机无法水平扩展且容器 root 可读全部用户数据。它的合理定位是 **20~30 人的小团队**。

### 容量估算 {#capacity}

| 指标 | 空载 | 日常 | 重负载 | 建议配额 |
| --- | --- | --- | --- | --- |
| 内存 RSS | 150~250MB | 400~800MB | 1~1.5GB | `MemoryMax=1.5G` |
| CPU | ~0% | 突发 0.3~0.8 核 | 1~1.5 核 | `CPUQuota=50%` |

```text
峰值并发 ≈ 注册数 × 10%~15%      → 1000 人约 100~150
真在生成中 ≈ 峰值并发 × 20%~30%  → 20~45
规划内存 ≈ 并发数 × 0.5G × 1.3（碎片与峰值余量）
vCPU    ≈ 并发数 ÷ 3（Agent 以 API 等待与 IO 为主，可安全超卖）
```

| 峰值并发 | 规划内存 | 建议机型 |
| --- | --- | --- |
| 50 | ~33G | 64GB |
| 100 | ~65G | 96GB |
| 150 | ~100G | **2 × 64C/128G** |
| 300 | ~200G | 3~4 节点 / K8s |

> [!WARNING]
> **磁盘才是隐藏炸弹。** 人均 20G 配额 × 1000 人 = 20TB 配额；而工作区里会堆积 `node_modules`、模型缓存、构建产物和会话日志。做法：按 uid 设配额（`xfs_quota -x -c 'limit bhard=20g dsh-alice' /data`），备份分层（活跃用户每日增量、长尾用户每周），并把缓存目录排除在外。全量每日备份 10TB 不现实。

### 最省钱的一招：按需启停 + 分层池 {#on-demand}

不要让 1000 个实例常驻。按活跃度分两池：常驻池约 100~200 人（重度用户，登录即用），按需池约 800 人（登录时拉起、空闲 15 分钟回收）。同样 1000 人，规划内存从全员常驻的约 250GB 降到分层池的约 63GB。

网关进程无 root 权限，所以触发要走一条受控通道：

```text
网关 ──D-Bus/polkit──▶ systemd ──▶ systemctl start dsh-user@<name>
       （只授权 dsh-user@* 的 start/stop，其余一律不给）
```

> [!WARNING]
> 空闲回收必须**双条件**判断：无 HTTP 请求 **且** 无活跃 WebSocket。只按 HTTP 判断会掐掉用户正在跑的 Agent 长任务——那段时间浏览器是静默的，但 WebSocket 是活的。

冷启动延迟要如实告知：空工作区 3~6 秒，中等工作区 6~15 秒，大仓库 20~60 秒。所以按需池要有等待页，且**重度用户一律划入常驻池**——让最活跃的 10% 每天等 15 秒，体验损失远大于省下的内存。

### 网关在规模下要补的六件事 {#gateway-scale}

| # | 改动 | 原因 |
| --- | --- | --- |
| 1 | 接入 SSO，密码退化为兜底 | 离职回收、密码重置、MFA、审计；1000 个手工账号必然失控 |
| 2 | 用户表 JSON → PostgreSQL / LDAP | 多副本下的并发与一致性不可接受，且需要审计查询 |
| 3 | 登录限流内存 → Redis | 多副本后进程内计数形同虚设，轮换副本即可绕过 |
| 4 | 网关无状态化 + 多副本 | HMAC 会话设计天然支持，路由表与限流状态外置即可 |
| 5 | 加审计日志 | 记录登录成功/失败与管理操作，合规与事故复盘的刚需 |
| 6 | 端口段规划 + 路由表内存缓存 | 1000 用户占用 3101~4100；路由映射用内存 + 变更通知，而非每请求读文件 |

> [!IMPORTANT]
> 叠加 SSO 时，**网关只能接受来自身份代理的连接**。否则攻击者自己伪造一个 `X-Auth-Request-User` 头就能冒充任意用户。做法：网关只监听回环，并用 iptables/nginx 白名单把来源限制为身份代理。

## 分阶段落地顺序 {#phases}

| 阶段 | 目标 | 动作 |
| --- | --- | --- |
| P0 | 先把人放进来 | 接入 SSO；网关多副本 + 用户表迁 DB + 限流迁 Redis；加审计日志 |
| P1 | 拆掉定时炸弹 | 回环隔离改 O(n) 或改用 netns；实例改按需启停 + 分层池；slice 分层下发配额 |
| P2 | 把边界收紧 | 每 uid 磁盘配额；备份分层；监控实例内存、网关 QPS、登录失败率 |
| P3 | 要平台化就到这里 | 多节点诉求成立时迁移到 K8s；迁移期两套可并存（共用同一份用户表契约） |

> [!CAUTION]
> **P0 和 P1 的顺序不能颠倒。** 先把认证与账号生命周期接上（人少时改造成本最低），再动隔离与容量。反过来做，会在没有审计记录的情况下先暴露一个无隔离的系统。

## 上线核对清单 {#checklist}

- [ ] 公网只暴露 443；网关与实例只监听回环，端口永不对外
- [ ] 反向代理**覆盖**而非追加 `X-Forwarded-For`
- [ ] 回环租户隔离已生效，且 `iptables -S | grep -c '^-A DSH'` 与用户数同量级（不是平方级）
- [ ] IPv6（`::1`）也做了隔离
- [ ] 每实例有资源上限（systemd 指令 / cgroup v2 / compose limits）
- [ ] `NODE_OPTIONS=--max-old-space-size=1024` 已下发，否则 Node 默认堆让配额形同虚设
- [ ] `HOME` 与 `DSH_HOME` 同时指向用户私有目录
- [ ] 用户表权限 `0640`、会话签名密钥 `0600`
- [ ] 已关闭 `proxy_buffering`，否则流式输出异常
- [ ] `trustedHosts` 里写的是浏览器实际访问的**完整** Host
- [ ] 备份覆盖用户表、签名密钥与用户目录，并演练过恢复
- [ ] 没有人把实例端口暴露到公网，也没有人解禁 `--host 0.0.0.0`
- [ ] 团队已知晓「容器内 root = 可读全部用户数据」这一前提

## 排错表 {#troubleshooting}

| 现象 | 根因 | 解决 |
| --- | --- | --- |
| 页面壳能开，所有 `/api/*` 返回 403 | 特权接口的 Host/Origin 校验没过 | 配 `DSH_TRUSTED_HOSTS`（含回环与完整域名）；网关把上游 `Host` 改写成 `127.0.0.1:<port>` |
| 白屏 / `crypto.randomUUID is not a function` | 明文 HTTP，非安全上下文 | 上 HTTPS，别用 `http://IP:端口` |
| 回答「攒一堆」才整段出现 | 反代开了响应缓冲 | `proxy_buffering off`，并确认没被 CDN/WAF 二次缓冲 |
| 实例能启动，但调不通模型 API | 回环隔离把 DNS（127.0.0.53）也拒了 | 放行回环的 53 端口 |
| 用户能连上别人的实例端口 | 回环隔离没做，或规则没重建 | 跑隔离脚本；每次增删用户后重跑 |
| 「Agent 生成了文件但我看不到」 | `HOME` 与 `DSH_HOME` 不一致 | 两者都指向用户私有目录 |
| 容器重建后用户容器失联 | 共享 netns 的依附关系失效 | 删掉并重建用户容器，不要只 restart |
| 卷里的文件属主变成 root | 命名卷首次由 root 创建 | 容器启动脚本里加一句 `chown "$TARGET_UID" "$DSH_HOME"` 自愈（实例启动前跑），或手工 `chown -R "$TARGET_UID" /data/users/<name>` |
| cgroup 配额没生效 | 容器内 `/sys/fs/cgroup` 不可写 | 使用 `cgroup: private` 并挂载可写，否则退化为整容器 `mem_limit` |
| `iptables` 报权限不足 | 容器缺 `NET_ADMIN` | 加 `cap_add: [NET_ADMIN]`，或明确接受该风险 |
| 登录一直提示表单过期 | CSRF Cookie 未回传 | 确认 WAF/CDN 不吞 `Set-Cookie`，且访问域名前后一致 |

## 小结 {#summary}

把 dsh 变成团队服务，要补的是两层：**认证**回答「谁能进来」，**隔离**回答「他只能看见什么」。三个最值得记住的结论：

1. **认证做在网关，隔离做在操作系统。** 网关会被绕过，内核不会。
2. **所有实例共享回环是一种假隔离。** 必须按 UID 切断跨租户访问，而且规则要做成 O(n) 而不是 O(n²)——1000 人时这是 100 万条和 7000 条的差别。
3. **规模会改变结论。** ≤3 人用单密码，十几人到几十人用独立实例，上千人就必须上 SSO、按需启停和独立的网络命名空间。

至此本套教程七个章节完成：从安装、上手、核心概念、插件开发，到进阶实践，再到多用户部署与规模化加固——你已经可以把 dsh 从一个单机工具，安全地变成一个团队服务。
