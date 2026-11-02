# Companies House MCP Server

> Work in progress. Read-only MCP server for the UK Companies House public register, with a reproducible tool-use eval suite.

## How this differs

Several community Companies House MCP servers already exist, for example:

- [AntonGMorris/companies-house-mcp](https://glama.ai/mcp/servers/AntonGMorris/companies-house-mcp/tree) (Node/npx, Docker)
- [aicayzer/companies-house-mcp](https://www.getdrio.com/mcp/io-github-aicayzer-companies-house/md) (Node, MCP server + CLI)
- `companies-house-mcp-server` on npm (broad API coverage: registers, insolvency, exemptions)
- [`companies-house-mcp`](https://pypi.org/project/companies-house-mcp/) on PyPI (Python)
- [Pipeworx hosted endpoint](https://www.getdrio.com/mcp/io-github-pipeworx-io-companies-house) (remote HTTP, bring your own key)

This project aims to be different in four ways:

1. **A published, reproducible tool-use eval.** 50 cases run offline against recorded API responses, with results per model and a changelog showing how scores moved as tool descriptions improved.
2. **Task-shaped tools.** Six tools return concise, LLM-friendly outputs with next-step hints, instead of passing the raw API JSON straight through.
3. **Responsible handling of personal data.** Officers and PSCs are real people, so dates of birth are dropped, addresses are cut to town and postcode, and logs contain no personal data.
4. **Both transports.** stdio for local use, and streamable HTTP with bearer-token auth for hosted use.
