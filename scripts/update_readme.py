import yaml
import os
import re
from collections import defaultdict

# This script's file path to determine the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# File paths from project root
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")

# Markers for the auto-generated section in README.md
README_MARKER_START = "<!-- readme-generator:start -->"
README_MARKER_END = "<!-- readme-generator:end -->"


def generate_readme_content(config_data):
    """Generates Markdown string from the YAML configuration data."""
    lines = []

    # 1. Title
    title = config_data.get("title", "My Profile")
    lines.append(f"# {title}\n\n")

    # 2. Free-form sections
    free_sections = config_data.get("free_sections", [])
    if free_sections:
        for section in free_sections:
            sec_title = section.get("title")
            content = section.get("content", "")
            if sec_title:
                lines.append(f"## {sec_title}\n\n")

            if section.get("type") == "table":
                headers = section.get("headers", [])
                rows = section.get("rows", [])
                if headers and rows:
                    lines.append(f"| {' | '.join(headers)} |\n")
                    lines.append(f"|{'|'.join(['---'] * len(headers))}|\n")
                    for row in rows:
                        lines.append(f"| {' | '.join(row)} |\n")
                lines.append("\n")
            elif content:  # For regular content
                lines.append(f"{content}\n\n")

    # 3. Project Tables
    project_tables = config_data.get("project_tables", [])
    if project_tables:
        for table in project_tables:
            table_title = table.get("title")
            headers = table.get("headers", [])
            groups = table.get("groups", [])

            if not table_title or not headers or not groups:
                continue

            lines.append(f"## {table_title}\n\n")
            lines.append(f"| {' | '.join(headers)} |\n")
            lines.append(f"|{'|'.join(['---'] * len(headers))}|\n")

            for group in groups:
                category = group.get("category", "")
                for i, project in enumerate(group.get("projects", [])):
                    name = project.get("name", "N/A")
                    repo = project.get("repo", "")
                    description = project.get("description", "")
                    repo_url = f"https://{repo}" if repo else ""

                    first_col = category if i == 0 else ""
                    desc_with_link = f"{description} [Repo]({repo_url})" if repo_url else description

                    lines.append(f"| {first_col} | {name} | {desc_with_link} |\n")
            lines.append("\n")

    return "".join(lines)


def main():
    """Main process to update README.md."""
    print(f"Reading configuration from '{CONFIG_FILE}'...")

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{CONFIG_FILE}' not found.")
        return
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse '{CONFIG_FILE}': {e}")
        return

    print("Generating new content...")
    new_content = generate_readme_content(data)

    print(f"Reading current README from '{README_FILE}'...")
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: '{README_FILE}' not found.")
        return

    if README_MARKER_START in readme_content and README_MARKER_END in readme_content:
        print("Found markers. Replacing content...")

        before_marker = readme_content.split(README_MARKER_START)[0]
        after_marker = readme_content.split(README_MARKER_END)[1]

        # Ensure clean separation and no double newlines
        updated_readme = (
            before_marker.rstrip() +
            "\n" +
            README_MARKER_START +
            "\n" +
            new_content.strip() +
            "\n" +
            README_MARKER_END +
            "\n" +
            after_marker.lstrip()
        )

        print("Writing updated content to README.md...")
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(updated_readme)
        print(f"Successfully updated '{README_FILE}'.")
    else:
        print(f"ERROR: Markers '{README_MARKER_START}' and '{README_MARKER_END}' not found in '{README_FILE}'.")
        return


if __name__ == "__main__":
    main()
