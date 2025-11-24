# Context7 MCP setup for Codex

This repository tracks how to register the Context7 MCP server with Codex so you can stream structured context directly into your prompts.

## Prerequisites
- Codex CLI installed locally (`codex` available on your PATH).
- Node.js 18+ so `npx` can fetch the MCP server package.

## Add the Context7 server
Run the following command to register the MCP server with Codex:

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

Codex will save the server under the name `context7` and will launch it via `npx` whenever you enable it for a conversation.

## Usage tips
- After adding the server, toggle it on within Codex to make the provider available in your tools list.
- Ensure you are signed in to Context7 (or have access keys configured) if your environment requires authentication for private repos.
- You can re-run the `codex mcp add` command to update the server to the latest version published on npm.
