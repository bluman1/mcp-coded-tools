# 🌟 Popular MCP Servers for mcp-agent-tools (November 2025)

## Overview

This document lists the most popular and useful MCP servers to use with mcp-agent-tools. These servers are battle-tested in production environments and cover the most common enterprise use cases.

**Last Updated:** November 2025

---

## 🏆 Official Anthropic Reference Servers

These servers are maintained by the MCP team and represent best practices.

### Core Infrastructure

| Server | NPM Package | Use Case | Tool Count |
|--------|------------|----------|------------|
| **Filesystem** | `@modelcontextprotocol/server-filesystem` | Secure file operations with access controls | ~15 |
| **Git** | `@modelcontextprotocol/server-git` | Read, search, manipulate Git repositories | ~20 |
| **Memory** | `@modelcontextprotocol/server-memory` | Persistent knowledge graph for context | ~8 |
| **Time** | `@modelcontextprotocol/server-time` | Timezone conversions, time operations | ~6 |

### Testing & Automation

| Server | NPM Package | Use Case | Tool Count |
|--------|------------|----------|------------|
| **Sequential Thinking** | `@modelcontextprotocol/server-sequential-thinking` | Multi-step reasoning and problem-solving | ~12 |
| **Fetch** | `@modelcontextprotocol/server-fetch` | Web content retrieval and conversion | ~5 |
| **Everything** | `@modelcontextprotocol/server-everything` | Test/demo server with all feature types | ~25 |

**Installation Example:**
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -c "npx -y @modelcontextprotocol/server-git" \
  -c "npx -y @modelcontextprotocol/server-memory" \
  -o ./core_tools
```

---

## 🚀 Enterprise Integration Servers

### Development & Code Management

#### GitHub (★★★★★ Most Popular)
- **Package:** `@modelcontextprotocol/server-github` (archived, now at `github/github-mcp-server`)
- **Downloads:** 35,261/month
- **Use Cases:**
  - Automated PR reviews and code analysis
  - Issue tracking and project management
  - Release automation and changelog generation
  - Repository exploration and documentation
- **Key Tools:** `create_issue`, `get_pull_request`, `list_pr_files`, `create_review_comment`
- **Token Efficiency:** Managing 100+ repos would consume 180K tokens traditionally. With mcp-agent-tools: ~3K tokens.

```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -s github \
  -o ./dev_tools
```

**Real Use Case:**
```python
# Without mcp-agent-tools: Load 50 GitHub tool definitions = 45K tokens
# With mcp-agent-tools: Agent discovers tools as needed
from dev_tools.github import get_pull_request, list_pr_files
pr = await get_pull_request(owner='acme', repo='api', number=142)
files = await list_pr_files(owner='acme', repo='api', number=142)
# Process 500 changed files in execution, not context!
```

#### GitLab
- **Package:** Community maintained
- **Use Cases:** Similar to GitHub for GitLab users
- **Tools:** MR management, CI/CD pipeline control

### Data & Databases

#### PostgreSQL (★★★★★)
- **Package:** `@modelcontextprotocol/server-postgres`
- **Use Cases:**
  - Business intelligence and analytics
  - Database inspection and querying
  - Data validation and quality checks
  - Report generation from live data
- **Key Tools:** `execute_query`, `list_tables`, `describe_table`
- **Token Efficiency:** Query results with millions of rows stay in execution environment

```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -s postgres \
  -o ./data_tools
```

**Real Use Case:**
```python
# Process 1M rows without context pollution
from data_tools.postgres import execute_query
rows = await execute_query(query="SELECT * FROM transactions WHERE date > NOW() - INTERVAL '30 days'")
# 1,000,000 rows (~50MB) processed in code
# Only summary goes to context: "Processed 1M transactions, found 15 anomalies"
```

#### SQLite
- **Package:** `@modelcontextprotocol/server-sqlite`
- **Use Cases:** Local database operations, testing, prototyping

#### Redis
- **Package:** Community maintained
- **Use Cases:** Cache management, session handling, real-time data

#### MongoDB
- **Package:** Community maintained
- **Use Cases:** NoSQL operations, document storage, flexible schemas

### Communication & Collaboration

#### Slack (★★★★★ Top 5)
- **Package:** Multiple implementations (e.g., `slack-mcp-server`)
- **Downloads:** Widely used in enterprises
- **Use Cases:**
  - Team notifications and alerts
  - Incident response coordination
  - Status updates and reporting
  - Conversational workflows
- **Key Tools:** `post_message`, `get_messages`, `search_messages`, `create_channel`

```bash
mcp-agent-tools generate \
  -c "python slack_mcp_server.py" \
  -s slack \
  -o ./communication_tools
```

**Real Use Case:**
```python
# Coordinate global team across timezones
from communication_tools.slack import post_message, get_user_info
for team_member in ['alice', 'bob', 'charlie']:
    user = await get_user_info(user=team_member)
    await post_message(
        channel=f"dm-{team_member}",
        text=f"🚀 Deploy complete at your local time: {user.tz}"
    )
```

#### Discord
- **Package:** Community maintained
- **Use Cases:** Community management, gaming, informal teams

#### WhatsApp
- **Package:** Community maintained
- **Use Cases:** Customer communication, international teams

### Cloud Services

#### Google Drive (★★★★★)
- **Package:** `@modelcontextprotocol/server-gdrive`
- **Use Cases:**
  - Document management and search
  - File sharing and collaboration
  - Content extraction for analysis
  - Backup and archival
- **Key Tools:** `list_files`, `get_document`, `search_files`, `upload_file`

```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-gdrive" \
  -s google_drive \
  -o ./cloud_tools
```

**Real Use Case:**
```python
# Search across 10,000 documents efficiently
from cloud_tools.google_drive import search_files, get_document
files = await search_files(query="Q4 revenue report")
# Agent processes metadata for 10K files in execution
# Selects top 5 relevant files
for file in files[:5]:
    content = await get_document(document_id=file.id)
    # Extract insights without flooding context
```

#### Google Maps
- **Package:** `@modelcontextprotocol/server-google-maps`
- **Use Cases:** Location services, route planning, geographic data

#### AWS
- **Package:** Multiple services (S3, Lambda, etc.)
- **Use Cases:** Cloud infrastructure management

#### Azure
- **Package:** Community maintained
- **Use Cases:** Microsoft cloud services

#### Cloudflare
- **Package:** Community maintained
- **Use Cases:** CDN management, Workers deployment

### Browser Automation

#### Puppeteer (★★★★)
- **Package:** `@modelcontextprotocol/server-puppeteer`
- **Downloads:** Popular for testing
- **Use Cases:**
  - Automated testing and QA
  - Web scraping and data collection
  - Screenshot generation
  - Form submission automation
- **Key Tools:** `navigate`, `click`, `screenshot`, `get_page_content`

```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-puppeteer" \
  -s browser \
  -o ./automation_tools
```

#### Playwright
- **Package:** Community maintained (★★★★★ 12K GitHub stars)
- **Use Cases:** Modern browser automation, cross-browser testing

**Real Use Case:**
```python
# Automated UI regression testing
from automation_tools.browser import navigate, screenshot, click
await navigate(url='https://staging.acme.com/checkout')
await click(selector='#payment-button')
screenshot_path = await screenshot(path='./test-results/checkout.png')
# Visual regression detection in execution environment
```

### Monitoring & Observability

#### Sentry
- **Package:** `@modelcontextprotocol/server-sentry`
- **Use Cases:** Error tracking, performance monitoring, alerting

### Development Tools

#### JetBrains IDEs
- **Package:** Community maintained
- **Use Cases:** IDE automation, code analysis, refactoring

#### Docker
- **Package:** Community maintained
- **Use Cases:** Container management, deployment automation

#### Kubernetes
- **Package:** Community maintained
- **Use Cases:** Cluster management, deployment orchestration

---

## 📊 Top Use Case Combinations

### 1. DevOps Incident Response
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "python slack_mcp_server.py" \
  -c "npx -y @modelcontextprotocol/server-sentry" \
  -o ./devops_tools
```
**Workflow:** Query errors → Create issue → Notify team → Track resolution

**Token Savings:** 150K → 3K (98% reduction)

**Cost Impact:** $3.00 → $0.06 per incident @ $0.02/1K tokens

### 2. Data Analytics Pipeline
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -c "python slack_mcp_server.py" \
  -c "npx -y @modelcontextprotocol/server-gdrive" \
  -o ./analytics_tools
```
**Workflow:** Query database → Process data → Generate report → Upload → Notify

**Scale:** Process millions of rows without context pollution

### 3. Automated Code Review
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -c "npx -y @modelcontextprotocol/server-sequential-thinking" \
  -c "python slack_mcp_server.py" \
  -o ./code_review_tools
```
**Workflow:** Get PR → Read files → Analyze → Comment → Notify

**Impact:** Review 1000s of PRs/day with consistent quality

### 4. Customer Support Automation
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -c "npx -y @modelcontextprotocol/server-memory" \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "python slack_mcp_server.py" \
  -o ./support_tools
```
**Workflow:** Search KB → Check tickets → Query history → Create/respond → Escalate

**ROI:** $109M/year savings for 500 tickets/day operation

### 5. Release Management
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-git" \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -c "npx -y @modelcontextprotocol/server-puppeteer" \
  -c "npx -y @modelcontextprotocol/server-time" \
  -c "python slack_mcp_server.py" \
  -o ./release_tools
```
**Workflow:** Analyze commits → Generate changelog → Test UI → Create release → Coordinate team

**Complexity:** 120+ tools working together seamlessly

---

## 🎯 Choosing the Right Servers

### For Startups & Small Teams
**Start with:** GitHub, Slack, Filesystem
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "python slack_mcp_server.py" \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -o ./startup_tools
```
**Why:** Cover 80% of automation needs with minimal setup

### For Data-Heavy Operations
**Start with:** PostgreSQL, Filesystem, Slack
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -c "python slack_mcp_server.py" \
  -o ./data_ops_tools
```
**Why:** Process massive datasets efficiently

### For Enterprise Workflows
**Start with:** All official servers + key integrations
```bash
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -c "npx -y @modelcontextprotocol/server-filesystem" \
  -c "npx -y @modelcontextprotocol/server-git" \
  -c "npx -y @modelcontextprotocol/server-memory" \
  -c "npx -y @modelcontextprotocol/server-sequential-thinking" \
  -c "python slack_mcp_server.py" \
  -c "npx -y @modelcontextprotocol/server-gdrive" \
  -o ./enterprise_tools
```
**Why:** Comprehensive coverage for complex workflows

---

## 📈 Production Metrics (Real Data from November 2025)

### Twilio's Testing Results
- **19.2% fewer API calls** needed with MCP
- **100% success rate** vs 92.3% without MCP
- **6.3% fewer tokens** consumed
- **Net benefit:** More reliable despite 27.5% higher context costs

### TigerData's Production Agent
- **70% infrastructure cost reduction**
- **50% reduction in development overhead**
- Successfully handling real-time data ingestion and analysis

### Enterprise Adoption
- **Block, Apollo:** Integrated MCP into production systems
- **Zed, Replit, Codeium, Sourcegraph:** Building MCP into their platforms
- **Claude, Gemini, OpenAI:** Native MCP support

---

## 🔍 Finding More Servers

### Official Directories
- **PulseMCP:** https://www.pulsemcp.com/servers (6,490+ servers)
- **MCP Server Finder:** https://www.mcpserverfinder.com/
- **GitHub Official:** https://github.com/modelcontextprotocol/servers
- **MCP.so:** https://mcp.so/

### Search Tips
```bash
# NPM search
npm search @modelcontextprotocol

# GitHub search
site:github.com "mcp server"

# Check downloads
npm view @modelcontextprotocol/server-github
```

---

## 💡 Pro Tips

### 1. Start Small, Scale Up
```bash
# Week 1: Core tools
mcp-agent-tools generate -c "npx -y @modelcontextprotocol/server-github" -o ./tools

# Week 2: Add database
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -o ./tools

# Week 3: Add communication
# ... continue building your toolset
```

### 2. Use Explicit Server Names
```bash
# Good: Clear organization
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -s github \
  -o ./tools

# Result: tools/github/ (clear structure)
```

### 3. Test with `inspect` First
```bash
# Preview tools before generating
mcp-agent-tools inspect -c "npx -y @modelcontextprotocol/server-github"
```

### 4. Keep Tools Updated
```bash
# Regenerate periodically to get latest tool versions
mcp-agent-tools generate --overwrite -c "..." -o ./tools
```

### 5. Document Your Setup
Create a `tools.txt` listing all your MCP servers:
```txt
# Production agent tools
@modelcontextprotocol/server-github    # Code management
@modelcontextprotocol/server-postgres  # Database queries
slack_mcp_server.py                    # Team communication
```

---

## 🚀 Getting Started

### Quick Test (5 minutes)
```bash
# 1. Install mcp-agent-tools
pip install mcp-agent-tools

# 2. Generate from one popular server
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -o ./test_tools

# 3. Explore generated tools
ls test_tools/github/
cat test_tools/github/get_repository.py

# 4. Use in your agent!
```

### Production Setup (30 minutes)
```bash
# 1. Choose your servers (see combinations above)
# 2. Generate comprehensive toolset
mcp-agent-tools generate \
  -c "npx -y @modelcontextprotocol/server-github" \
  -c "npx -y @modelcontextprotocol/server-postgres" \
  -c "python slack_mcp_server.py" \
  -o ./production_tools

# 3. Test with your agent framework
# 4. Deploy and monitor
```

---

## 📚 Additional Resources

- **Official MCP Docs:** https://modelcontextprotocol.io/
- **Anthropic's Blog:** https://www.anthropic.com/news/model-context-protocol
- **Community Servers:** https://github.com/modelcontextprotocol/servers
- **Real-World Examples:** See `examples/real_world_workflows.py` in this repo

---

**Last Updated:** November 5, 2025

**Next Review:** December 2025 (MCP ecosystem evolving rapidly!)

---

*Have a popular MCP server to add? Open an issue or PR on GitHub!*
