# v3-sfhm: Rust-Only SFHM Backend

**Branch:** `sfhm`
**Status:** Experimental, divergent from main, last updated Dec 2024

## Description

Stateless Functional Hierarchical Memory with a Rust-only backend and subprocess CLI integration. This version explores pure Rust performance for memory compression operations.

## Key Features

- Rust-only backend for performance
- Functional memory architecture (stateless design)
- Subprocess CLI integration
- Compression bug fixes

## Architecture

SFHM takes a functional programming approach to hierarchical memory — each compression operation is a pure function that takes the current memory state and returns a new state. The Rust backend provides significant performance improvements over the Python-based v1-core for compute-intensive compression operations.

## Status

This branch is experimental and divergent from main. It represents a performance-focused alternative that trades Python's flexibility for Rust's speed and safety guarantees.
