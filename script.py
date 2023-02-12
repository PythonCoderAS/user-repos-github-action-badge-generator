from pathlib import Path
from os import environ
from yaml import safe_load

def main():
    repo_path = Path(environ.get("REPO_PATH", "."))
    workflow_path = repo_path / ".github/workflows"
    if workflow_path.is_dir():
        printed_header = False
        repo = environ.get("REPO")
        for workflow in workflow_path.iterdir():
            if workflow.suffix == ".yml" and workflow.is_file():
                with workflow.open() as f:
                    workflow_dict = safe_load(f)
                    if on_dict := workflow_dict.get("on", {}):
                        not_excluding_main_branch = False
                        if branches := on_dict.get("branches", []):
                            not_excluding_main_branch = "!main" not in branches and "!master" not in branches
                        if branches_ignore := on_dict.get("branches-ignore", []):
                            not_excluding_main_branch = "main" not in branches_ignore and "master" not in branches_ignore
                        if on_dict.get("schedule", []):
                            not_excluding_main_branch = True
                        if not_excluding_main_branch:
                            if not printed_header:
                                print(f"## {repo}")
                                printed_header = True
                            name = workflow_dict.get("name", workflow.stem)
                            print(f"[![{name}](https://github.com/{repo}/actions/workflows/{workflow.name}/badge.svg)](https://github.com/{repo}/actions/workflows/{workflow.name})", end=" ")
        print()

if __name__ == "__main__":
    main()