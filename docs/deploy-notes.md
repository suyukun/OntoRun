# OntoRun 云端 DSH 部署笔记（2026-08-14）

> 用途：把 DSH（DeepSeek Harness Web）部署到阿里云服务器并迁移数据，本机通过 SSH 隧道访问。
> 状态：✅ 已完成并验证（隧道 3081 通、迁移完成、服务器 DSH 运行中）

## 1. 服务器现状

- IP：39.97.234.216（阿里云，Alibaba Cloud Linux 3.2104，x86_64）
- SSH：root + 密钥 `~/.ssh/citic-demo`（PasswordAuthentication no）
- 规格：2C / 1.8G 内存（已加 2G swap，共约 3.8G）/ 40G 磁盘（剩 25G）
- 已有服务：宝塔面板（8888，对外）、nginx（80/888）、postfix（25，仅本机）——**宝塔保留**（Jack 给别人做演示用）
- 安全：SSH 有爆破尝试在发生；安全更新欠账 19377 条；**安全整改未做（计划中：fail2ban/安全更新/宝塔收敛/systemd 自启）**

## 2. 环境安装记录

```bash
# Python 3.11（dnf）
dnf install -y python3.11 python3.11-pip python3.11-devel

# 编译工具链（node-pty 编译需要）
dnf install -y gcc-c++ make python3-devel

# Swap（关键！2G 内存不够编译，OOM 会杀 npm）
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo "swapfile=/swapfile swap swap defaults 0 0" >> /etc/fstab

# node-gyp 必须用 Python 3.11（系统 3.6 会 SyntaxError）
npm_config_python=/usr/bin/python3.11 npm install ...
```

## 3. DSH 安装

```bash
# 1) 装 DSH CLI（用国内镜像；npx -y 会卡，直接 npm install 更稳）
mkdir -p /opt/dsh && cd /opt/dsh
cat > package.json <<'EOF'
{"name":"dsh-server","private":true,"dependencies":{"@deepseek-ai/dsh":"0.1.0-rc.6"}}
EOF
npm_config_python=/usr/bin/python3.11 npm install --registry=https://registry.npmmirror.com --no-audit --no-fund

# 2) 建 web profile（bundle 依赖用 dsh plugin 装）
mkdir -p /root/.dsh/profiles/web
#   → package.json（bundles: dsh-base + dsh-web-app）、cordis.yml、cordis.patch.yml、pnpm-workspace.yaml
export PATH=/opt/dsh/node_modules/.bin:$PATH
export COREPACK_NPM_REGISTRY=https://registry.npmmirror.com
dsh plugin --profile web install

# 3) 配置
#   /root/.dsh/.credentials.yaml  ← DEEPSEEK_API_KEY（chmod 600）
#   /root/.dsh/settings.yaml      ← 模型/权限/agent 预设（与本地一致）
```

## 4. 启动

```bash
export PATH=/opt/dsh/node_modules/.bin:$PATH
export DSH_HOME=/root/.dsh
nohup dsh web --host 127.0.0.1 --port 3080 > /var/log/dsh-web.log 2>&1 < /dev/null &
# 验证：ss -tlnp | grep 3080；curl http://127.0.0.1:3080/
```

## 5. 本机隧道（Mac）

```bash
# 本机 3081 → 服务器 3080（3080 被本地 DSH 占用，必须用 3081！）
ssh -i ~/.ssh/citic-demo -o BatchMode=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -N -L 3081:127.0.0.1:3080 root@39.97.234.216
# 浏览器开 http://127.0.0.1:3081
```

## 6. 数据迁移（Mac → 服务器）

```bash
# 本机没有 rsync，用 tar 管道（排除 node_modules 与 .git）
cd /Users/suyukun && tar czf - --exclude='.dsh/profiles/node_modules' --exclude='.dsh/profiles/web/node_modules' --exclude='.dsh/.git' .dsh |   ssh -i ~/.ssh/citic-demo root@39.97.234.216 'tar xzf - -C /root'
cd /Users/suyukun/Documents && tar czf - --exclude='OntoRun/.git' --exclude='__pycache__' OntoRun |   ssh -i ~/.ssh/citic-demo root@39.97.234.216 'mkdir -p /opt && tar xzf - -C /opt'
# 迁移后重启服务器 DSH 生效；/opt/OntoRun/.env chmod 600
```

## 7. 踩坑记录（重要）

1. **本机 3080 被本地 DSH 占用**：隧道必须映射到 3081，否则 curl 命中的是本机服务（验证时须比对响应 rev，不能只看 200）。
2. **2G 内存编译 OOM**（npm install 被 kill，exit 137）：加 swap 解决。
3. **node-gyp 用 Python 3.6 报 SyntaxError**：`npm_config_python=/usr/bin/python3.11`（新版 npm 不认 `npm config set python`）。
4. **pkill -f "dsh web" 会匹配远程 shell 自身**（exit 255）：重启用精确 PID 或直接起（端口空时无需先杀）。
5. **npx -y 下载会卡**：用 `npm install` 到固定目录 + 国内镜像。
6. **rsync 本机未装**：用 tar 管道替代。

## 8. 待办（安全整改轮）

- [ ] fail2ban（SSH 爆破防护）
- [ ] `dnf update` 全量安全更新（19377 条，会重启，选低峰）
- [ ] 宝塔面板收敛（改端口/限 IP）
- [ ] DSH systemd 服务（开机自启）
- [ ] 隧道 Mac 开机自启脚本（或公网方案：备案+Caddy 或自签）
- [ ] DeepSeek key 轮换（曾明文暴露）
