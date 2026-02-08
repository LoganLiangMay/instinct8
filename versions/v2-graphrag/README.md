# v2-graphrag: GraphRAG + MCP Server

**Branch:** `graphrag-rs`
**Status:** Experimental, ~30 commits ahead of main, unmerged

## Description

Rust-based GraphRAG memory backend with MCP (Model Context Protocol) server integration, OpenAI embeddings, and TUI2 frontend. This version explores long-term vector storage and external tool integration as an alternative to in-context compression.

## Key Features

- Long-term vector storage via GraphRAG
- MCP API for external tool integration
- OpenAI embeddings for semantic retrieval
- Shell snapshotting
- TUI2 frontend

## Architecture

Unlike v1-core which compresses within the context window, v2-graphrag offloads memory to an external graph database with vector embeddings. The MCP server exposes this memory as tools that any MCP-compatible client can use.

## Status

This branch is experimental and significantly diverged from main. It represents an alternative architectural approach to the goal drift problem — external memory retrieval vs. in-context compression.
