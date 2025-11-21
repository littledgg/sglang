#!/usr/bin/env python3
"""
PR Analysis Tool for SGLang Repository

This script fetches and categorizes pull requests from the SGLang GitHub repository
to help understand the latest inference technologies and development directions.

Usage:
    python analyze_prs.py --days 7
    python analyze_prs.py --days 30 --state all
    python analyze_prs.py --days 7 --output json

Note: To avoid GitHub API rate limits, set the GITHUB_TOKEN environment variable
with your GitHub personal access token.
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib import request
from urllib.error import HTTPError, URLError


class PRAnalyzer:
    """Analyzes GitHub Pull Requests for the SGLang repository."""

    # Category keywords for classification
    CATEGORIES = {
        "Performance Optimization": [
            "performance", "optimization", "optimize", "faster", "speed", "throughput",
            "latency", "benchmark", "perf", "efficient", "cache", "memory",
        ],
        "Model Support": [
            "model", "llama", "deepseek", "qwen", "mistral", "mixtral", "gemma",
            "phi", "gpt", "falcon", "mpt", "baichuan", "chatglm", "internlm",
            "yi", "llava", "clip", "vision", "multimodal",
        ],
        "Inference Engine": [
            "engine", "runtime", "kernel", "cuda", "triton", "flashinfer",
            "attention", "flashattention", "paged", "kv cache", "radix",
            "scheduler", "batch", "continuous batching",
        ],
        "Distributed & Parallelism": [
            "distributed", "parallel", "tp", "pp", "ep", "tensor parallel",
            "pipeline parallel", "expert parallel", "multi-gpu", "multi-node",
            "disaggregation", "prefill", "decode",
        ],
        "Quantization & Compression": [
            "quantization", "quant", "int4", "int8", "fp8", "gptq", "awq",
            "smoothquant", "marlin", "compress", "prune",
        ],
        "API & Interface": [
            "api", "openai", "endpoint", "protocol", "http", "grpc", "websocket",
            "client", "server", "frontend", "backend",
        ],
        "Structured Output": [
            "json", "structured", "grammar", "constrained", "regex", "schema",
            "format", "output control",
        ],
        "Testing & CI": [
            "test", "ci", "unittest", "integration test", "pytest", "workflow",
            "github action", "build", "lint",
        ],
        "Documentation": [
            "doc", "documentation", "readme", "guide", "tutorial", "example",
            "comment", "typo",
        ],
        "Bug Fix": [
            "fix", "bug", "error", "issue", "crash", "fail", "broken",
            "regression", "hotfix",
        ],
        "Infrastructure": [
            "docker", "build", "setup", "install", "dependency", "requirement",
            "packaging", "release", "version",
        ],
        "Observability": [
            "logging", "metric", "monitor", "trace", "debug", "profile",
            "telemetry", "prometheus", "grafana",
        ],
    }

    def __init__(self, repo_owner: str = "sgl-project", repo_name: str = "sglang"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def fetch_prs(
        self,
        state: str = "all",
        days: int = 7,
        max_pages: int = 10,
    ) -> List[Dict]:
        """
        Fetch pull requests from GitHub API with pagination.

        Args:
            state: PR state - 'open', 'closed', or 'all'
            days: Number of days to look back
            max_pages: Maximum number of pages to fetch (100 PRs per page)

        Returns:
            List of PR dictionaries
        """
        since_date = datetime.now() - timedelta(days=days)
        all_prs = []
        page = 1

        print(f"Fetching PRs from {self.repo_owner}/{self.repo_name}...")
        print(f"State: {state}, Looking back: {days} days")
        print(f"Since: {since_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)

        while page <= max_pages:
            url = (
                f"{self.base_url}/pulls?"
                f"state={state}&"
                f"sort=created&"
                f"direction=desc&"
                f"per_page=100&"
                f"page={page}"
            )

            try:
                req = request.Request(url)
                req.add_header("Accept", "application/vnd.github.v3+json")
                # Add token if available via environment variable
                token = os.environ.get("GITHUB_TOKEN")
                if token:
                    req.add_header("Authorization", f"token {token}")

                with request.urlopen(req, timeout=30) as response:
                    prs = json.loads(response.read().decode())

                if not prs:
                    print(f"No more PRs found at page {page}")
                    break

                # Filter PRs by date
                filtered_prs = []
                for pr in prs:
                    created_at = datetime.strptime(
                        pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if created_at >= since_date:
                        filtered_prs.append(pr)
                    else:
                        # PRs are sorted by creation date, so we can stop
                        print(f"Reached PRs older than {days} days, stopping...")
                        all_prs.extend(filtered_prs)
                        return all_prs

                all_prs.extend(filtered_prs)
                print(
                    f"Page {page}: Found {len(filtered_prs)} PRs "
                    f"(Total: {len(all_prs)})"
                )

                # Check if we should continue
                if len(prs) < 100:
                    print("Reached last page")
                    break

                page += 1

            except HTTPError as e:
                print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
                if e.code == 403:
                    print(
                        "Rate limit exceeded. Please set GITHUB_TOKEN environment "
                        "variable for higher rate limits.",
                        file=sys.stderr,
                    )
                break
            except URLError as e:
                print(f"URL Error: {e.reason}", file=sys.stderr)
                break
            except Exception as e:
                print(f"Error fetching PRs: {e}", file=sys.stderr)
                break

        return all_prs

    def categorize_pr(self, pr: Dict) -> List[str]:
        """
        Categorize a PR based on title and body content.

        Args:
            pr: PR dictionary from GitHub API

        Returns:
            List of category names
        """
        title = pr.get("title", "").lower()
        body = pr.get("body", "") or ""
        body = body.lower()
        text = f"{title} {body}"

        categories = []
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    categories.append(category)
                    break

        return categories if categories else ["Other"]

    def analyze(
        self,
        state: str = "all",
        days: int = 7,
        max_pages: int = 10,
    ) -> Dict:
        """
        Analyze PRs and generate categorized report.

        Args:
            state: PR state - 'open', 'closed', or 'all'
            days: Number of days to look back
            max_pages: Maximum number of pages to fetch

        Returns:
            Dictionary with analysis results
        """
        prs = self.fetch_prs(state=state, days=days, max_pages=max_pages)

        if not prs:
            return {
                "total_prs": 0,
                "by_state": {},
                "by_category": {},
                "prs": [],
            }

        # Categorize PRs
        categorized_prs = defaultdict(list)
        by_state = defaultdict(int)

        for pr in prs:
            categories = self.categorize_pr(pr)
            pr_state = pr.get("state", "unknown")
            by_state[pr_state] += 1

            pr_info = {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr_state,
                "merged": pr.get("merged_at") is not None,
                "url": pr.get("html_url"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "user": pr.get("user", {}).get("login"),
                "categories": categories,
            }

            for category in categories:
                categorized_prs[category].append(pr_info)

        return {
            "total_prs": len(prs),
            "by_state": dict(by_state),
            "by_category": {
                cat: len(prs_list) for cat, prs_list in categorized_prs.items()
            },
            "categorized_prs": dict(categorized_prs),
            "all_prs": prs,
        }

    def print_report(self, analysis: Dict, show_details: bool = True):
        """Print analysis report to console."""
        print("\n" + "=" * 80)
        print("PR ANALYSIS REPORT")
        print("=" * 80)

        print(f"\nTotal PRs: {analysis['total_prs']}")
        print("\nBy State:")
        for state, count in sorted(analysis["by_state"].items()):
            print(f"  {state.capitalize()}: {count}")

        print("\nBy Category:")
        sorted_categories = sorted(
            analysis["by_category"].items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for category, count in sorted_categories:
            print(f"  {category}: {count}")

        if show_details and "categorized_prs" in analysis:
            print("\n" + "=" * 80)
            print("DETAILED PR BREAKDOWN BY CATEGORY")
            print("=" * 80)

            for category, prs in sorted(
                analysis["categorized_prs"].items(),
                key=lambda x: len(x[1]),
                reverse=True,
            ):
                print(f"\n{category} ({len(prs)} PRs):")
                print("-" * 80)

                for pr in prs[:10]:  # Show up to 10 PRs per category
                    status = "✓ Merged" if pr["merged"] else f"○ {pr['state']}"
                    print(f"  #{pr['number']} [{status}] {pr['title']}")
                    print(f"    URL: {pr['url']}")
                    print(f"    Author: {pr['user']}, Created: {pr['created_at'][:10]}")

                if len(prs) > 10:
                    print(f"  ... and {len(prs) - 10} more PRs")

        print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Pull Requests for SGLang repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze PRs from the last 7 days
  python analyze_prs.py --days 7

  # Analyze all open PRs from the last 30 days
  python analyze_prs.py --days 30 --state open

  # Get JSON output
  python analyze_prs.py --days 7 --output json

  # Analyze PRs from a forked repository
  python analyze_prs.py --days 7 --owner myuser --repo sglang

Environment Variables:
  GITHUB_TOKEN: GitHub personal access token for higher API rate limits
        """,
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)",
    )
    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="all",
        help="PR state to filter (default: all)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum pages to fetch (100 PRs per page, default: 10)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Hide detailed PR breakdown",
    )
    parser.add_argument(
        "--owner",
        default="sgl-project",
        help="Repository owner (default: sgl-project)",
    )
    parser.add_argument(
        "--repo",
        default="sglang",
        help="Repository name (default: sglang)",
    )

    args = parser.parse_args()

    analyzer = PRAnalyzer(repo_owner=args.owner, repo_name=args.repo)
    analysis = analyzer.analyze(
        state=args.state,
        days=args.days,
        max_pages=args.max_pages,
    )

    if args.output == "json":
        # Remove full PR objects for cleaner JSON output
        output = {
            "total_prs": analysis["total_prs"],
            "by_state": analysis["by_state"],
            "by_category": analysis["by_category"],
            "categorized_prs": analysis["categorized_prs"],
        }
        print(json.dumps(output, indent=2))
    else:
        analyzer.print_report(analysis, show_details=not args.no_details)


if __name__ == "__main__":
    main()
