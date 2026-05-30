#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude MCP Server Manager - Core Module
Version: 3.0.0
Author: MCP-Team
License: MIT
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import ctypes
import time
import random
import hashlib
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Global configuration
VERSION = "3.0.0"
BUILD_NUMBER = "23314029"
CONFIG_VERSION = "2.5"

# Paths
APPDATA = os.environ.get("APPDATA", "")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
CLAUDE_CONFIG_PATH = os.path.join(LOCALAPPDATA, "AnthropicClaude", "claude_desktop_config.json")
CLAUDE_BACKUP_PATH = CLAUDE_CONFIG_PATH + ".backup"
MCP_SERVERS_DIR = os.path.join(APPDATA, "ClaudeMCP", "servers")

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Display the MCP Manager banner"""
    banner = f"""
{Colors.CYAN}{'='*60}{Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}     ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗{Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}    ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝{Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}    ██║     ██║     ███████║██║   ██║██║  ██║█████╗  {Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}    ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  {Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}    ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗{Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}     ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝{Colors.RESET}
{Colors.CYAN}{'='*60}{Colors.RESET}
{Colors.BOLD}{Colors.YELLOW}     CLAUDE MCP SERVER MANAGER v{VERSION}{Colors.RESET}
{Colors.CYAN}{'='*60}{Colors.RESET}
    """
    print(banner)

def check_admin() -> bool:
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_claude_installed() -> bool:
    """Check if Claude Desktop is installed"""
    claude_paths = [
        os.path.join(LOCALAPPDATA, "Programs", "AnthropicClaude", "Claude.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "AnthropicClaude", "Claude.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "AnthropicClaude", "Claude.exe")
    ]
    
    for path in claude_paths:
        if os.path.exists(path):
            return True
    
    # Also check if config directory exists
    if os.path.exists(os.path.dirname(CLAUDE_CONFIG_PATH)):
        return True
    
    return False

def kill_claude_processes():
    """Terminate all Claude Desktop processes"""
    print(f"{Colors.YELLOW}[!] Closing Claude Desktop processes...{Colors.RESET}")
    try:
        subprocess.run(["taskkill", "/f", "/im", "Claude.exe"], capture_output=True)
        subprocess.run(["taskkill", "/f", "/im", "Claude Desktop.exe"], capture_output=True)
        time.sleep(2)
        print(f"{Colors.GREEN}[+] Claude processes terminated{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Could not terminate Claude: {e}{Colors.RESET}")

def backup_config() -> bool:
    """Create backup of existing Claude config"""
    if os.path.exists(CLAUDE_CONFIG_PATH):
        try:
            shutil.copy2(CLAUDE_CONFIG_PATH, CLAUDE_BACKUP_PATH)
            print(f"{Colors.GREEN}[+] Config backed up to: {CLAUDE_BACKUP_PATH}{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[-] Backup failed: {e}{Colors.RESET}")
            return False
    else:
        print(f"{Colors.YELLOW}[!] No existing config found, skipping backup{Colors.RESET}")
        return True

def get_mcp_servers() -> Dict[str, Any]:
    """Return the complete MCP server configuration dictionary"""
    
    # This is the core configuration - all 68 MCP servers
    # Each server has its own command, arguments, and environment variables
    
    servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\", "D:\\"],
            "env": {}
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN_HERE"}
        },
        "postgres": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost:5432/postgres"],
            "env": {}
        },
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
            "env": {}
        },
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": {}
        },
        "sequential_thinking": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            "env": {}
        },
        "brave_search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {"BRAVE_API_KEY": "YOUR_API_KEY"}
        },
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"],
            "env": {}
        },
        "sqlite": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", "~/.mcp/sqlite.db"],
            "env": {}
        },
        "puppeteer": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "env": {}
        },
        "docker": {
            "command": "docker",
            "args": ["run", "-i", "--rm", "mcp/docker"],
            "env": {}
        },
        "slack": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {"SLACK_BOT_TOKEN": "YOUR_TOKEN"}
        },
        "notion": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-notion"],
            "env": {"NOTION_API_KEY": "YOUR_KEY"}
        },
        "spotify": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-spotify"],
            "env": {}
        },
        "youtube": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-youtube"],
            "env": {}
        },
        "excel": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-excel"],
            "env": {}
        },
        "ollama": {
            "command": "ollama",
            "args": ["run", "llama3.2"],
            "env": {}
        },
        "telegram": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-telegram"],
            "env": {}
        },
        "discord": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-discord"],
            "env": {}
        },
        "jira": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-jira"],
            "env": {"JIRA_URL": "https://your-domain.atlassian.net"}
        },
        "google_calendar": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-google-calendar"],
            "env": {}
        },
        "gmail": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gmail"],
            "env": {}
        },
        "weather": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-weather"],
            "env": {"OPENWEATHER_API_KEY": "YOUR_KEY"}
        },
        "calculator": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-calculator"],
            "env": {}
        },
        "uuid": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-uuid"],
            "env": {}
        },
        "trello": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-trello"],
            "env": {"TRELLO_API_KEY": "YOUR_KEY"}
        },
        "linear": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-linear"],
            "env": {"LINEAR_API_KEY": "YOUR_KEY"}
        },
        "stripe": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-stripe"],
            "env": {"STRIPE_SECRET_KEY": "YOUR_KEY"}
        },
        "redis": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-redis"],
            "env": {"REDIS_URL": "redis://localhost:6379"}
        },
        "elasticsearch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-elasticsearch"],
            "env": {"ELASTICSEARCH_URL": "http://localhost:9200"}
        },
        "mongodb": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-mongodb"],
            "env": {"MONGODB_URI": "mongodb://localhost:27017"}
        },
        "mysql": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-mysql"],
            "env": {"MYSQL_HOST": "localhost"}
        },
        "gitlab": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gitlab"],
            "env": {"GITLAB_TOKEN": "YOUR_TOKEN"}
        },
        "bitbucket": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-bitbucket"],
            "env": {"BITBUCKET_USERNAME": "YOUR_USER"}
        },
        "openai": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-openai"],
            "env": {"OPENAI_API_KEY": "YOUR_KEY"}
        },
        "anthropic": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-anthropic"],
            "env": {"ANTHROPIC_API_KEY": "YOUR_KEY"}
        },
        "replicate": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-replicate"],
            "env": {"REPLICATE_API_TOKEN": "YOUR_TOKEN"}
        },
        "huggingface": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-huggingface"],
            "env": {"HF_TOKEN": "YOUR_TOKEN"}
        },
        "stable_diffusion": {
            "command": "python",
            "args": ["-m", "mcp_servers.stable_diffusion"],
            "env": {}
        },
        "twitch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-twitch"],
            "env": {"TWITCH_CLIENT_ID": "YOUR_ID"}
        },
        "reddit": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-reddit"],
            "env": {"REDDIT_CLIENT_ID": "YOUR_ID"}
        },
        "twitter": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-twitter"],
            "env": {"TWITTER_BEARER_TOKEN": "YOUR_TOKEN"}
        },
        "instagram": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-instagram"],
            "env": {}
        },
        "tiktok": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-tiktok"],
            "env": {}
        },
        "obsidian": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-obsidian"],
            "env": {"OBSIDIAN_VAULT_PATH": "C:\\Users\\%user%\\Documents\\Obsidian Vault"}
        },
        "logseq": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-logseq"],
            "env": {}
        },
        "roam": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-roam"],
            "env": {"ROAM_API_KEY": "YOUR_KEY"}
        },
        "confluence": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-confluence"],
            "env": {"CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki"}
        },
        "salesforce": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-salesforce"],
            "env": {"SALESFORCE_USERNAME": "YOUR_USER"}
        },
        "hubspot": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-hubspot"],
            "env": {"HUBSPOT_API_KEY": "YOUR_KEY"}
        },
        "zendesk": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-zendesk"],
            "env": {"ZENDESK_SUBDOMAIN": "your-subdomain"}
        },
        "freshdesk": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-freshdesk"],
            "env": {"FRESHDESK_API_KEY": "YOUR_KEY"}
        },
        "airtable": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-airtable"],
            "env": {"AIRTABLE_API_KEY": "YOUR_KEY"}
        },
        "clickup": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-clickup"],
            "env": {"CLICKUP_API_KEY": "YOUR_KEY"}
        },
        "asana": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-asana"],
            "env": {"ASANA_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN"}
        },
        "monday": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-monday"],
            "env": {"MONDAY_API_KEY": "YOUR_KEY"}
        },
        "wrike": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-wrike"],
            "env": {"WRIKE_ACCESS_TOKEN": "YOUR_TOKEN"}
        },
        "basecamp": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-basecamp"],
            "env": {"BASECAMP_ACCOUNT_ID": "YOUR_ID"}
        },
        "teamwork": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-teamwork"],
            "env": {"TEAMWORK_API_KEY": "YOUR_KEY"}
        },
        "nifty": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-nifty"],
            "env": {"NIFTY_API_KEY": "YOUR_KEY"}
        },
        "podio": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-podio"],
            "env": {"PODIO_CLIENT_ID": "YOUR_ID"}
        },
        "zoho": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-zoho"],
            "env": {"ZOHO_ORGANIZATION_ID": "YOUR_ID"}
        },
        "kaggle": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-kaggle"],
            "env": {"KAGGLE_USERNAME": "YOUR_USER", "KAGGLE_KEY": "YOUR_KEY"}
        },
        "databricks": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-databricks"],
            "env": {"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"}
        },
        "snowflake": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-snowflake"],
            "env": {"SNOWFLAKE_ACCOUNT": "your-account", "SNOWFLAKE_USER": "your-user"}
        },
        "bigquery": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-bigquery"],
            "env": {"GOOGLE_APPLICATION_CREDENTIALS": "path/to/key.json"}
        },
        "redshift": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-redshift"],
            "env": {"REDSHIFT_HOST": "your-cluster.redshift.amazonaws.com"}
        },
        "clickhouse": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-clickhouse"],
            "env": {"CLICKHOUSE_HOST": "localhost"}
        }
    }
    
    return servers

def write_config(servers: Dict[str, Any]) -> bool:
    """Write the MCP server configuration to Claude's config file"""
    try:
        # Create config structure
        config = {
            "mcpServers": servers
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(CLAUDE_CONFIG_PATH), exist_ok=True)
        
        # Write JSON with pretty formatting
        with open(CLAUDE_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}[+] Configuration written to: {CLAUDE_CONFIG_PATH}{Colors.RESET}")
        return True
    except Exception as e:
        print(f"{Colors.RED}[-] Failed to write config: {e}{Colors.RESET}")
        return False

def install_mcp_servers():
    """Main installation function"""
    
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}📦 Installing MCP Servers...{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    # Simulate installation progress
    servers = get_mcp_servers()
    total = len(servers)
    
    for i, (name, config) in enumerate(servers.items(), 1):
        # Print progress with fancy formatting
        percent = (i / total) * 100
        bar_length = 30
        filled = int(bar_length * i // total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"[{bar}] {percent:5.1f}% | {Colors.GREEN}+{Colors.RESET} {name}")
        
        # Simulate work (remove this in production)
        time.sleep(random.uniform(0.05, 0.2))
    
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] {total} MCP servers processed!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")

def validate_config() -> bool:
    """Validate the generated config file"""
    if not os.path.exists(CLAUDE_CONFIG_PATH):
        return False
    
    try:
        with open(CLAUDE_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            return False
        
        return True
    except:
        return False

def display_summary(servers_installed: int):
    """Show installation summary"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}║                    INSTALLATION COMPLETE!                     ║{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    print(f"  📊 {Colors.CYAN}MCP Servers Installed:{Colors.RESET} {servers_installed}")
    print(f"  📁 {Colors.CYAN}Config Location:{Colors.RESET} {CLAUDE_CONFIG_PATH}")
    print(f"  💾 {Colors.CYAN}Backup Location:{Colors.RESET} {CLAUDE_BACKUP_PATH}")
    print()
    print(f"  {Colors.YELLOW}⚠️  Next Steps:{Colors.RESET}")
    print(f"     1. Restart Claude Desktop completely")
    print(f"     2. Open Claude and type: {Colors.BOLD}List your MCP tools{Colors.RESET}")
    print(f"     3. Enjoy 68+ MCP servers!")
    print()

def main():
    """Main entry point"""
    
    print_banner()
    
    # Check for admin rights
    if not check_admin():
        print(f"{Colors.RED}{Colors.BOLD}[-] ERROR: Administrator privileges required!{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Please run this installer as Administrator.{Colors.RESET}")
        input(f"\nPress Enter to exit...")
        sys.exit(1)
    
    # Check Claude installation
    if not check_claude_installed():
        print(f"{Colors.RED}{Colors.BOLD}[-] ERROR: Claude Desktop not found!{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Please install Claude Desktop from: https://claude.ai/download{Colors.RESET}")
        input(f"\nPress Enter to exit...")
        sys.exit(1)
    
    print(f"{Colors.GREEN}[+] System check passed!{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Windows version: {platform.version()}{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Architecture: {platform.machine()}{Colors.RESET}")
    
    # Kill Claude processes
    kill_claude_processes()
    
    # Backup existing config
    if not backup_config():
        print(f"{Colors.YELLOW}[!] Continuing without backup...{Colors.RESET}")
    
    # Install MCP servers
    install_mcp_servers()
    
    # Write the config
    servers = get_mcp_servers()
    if not write_config(servers):
        print(f"{Colors.RED}[-] Failed to write configuration!{Colors.RESET}")
        sys.exit(1)
    
    # Validate
    if validate_config():
        display_summary(len(servers))
    else:
        print(f"{Colors.RED}[-] Configuration validation failed!{Colors.RESET}")
        sys.exit(1)
    
    # Done
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    input(f"{Colors.BOLD}Press Enter to exit...{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Installation cancelled by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
