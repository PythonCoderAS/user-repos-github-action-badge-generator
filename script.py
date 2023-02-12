from pathlib import Path
from os import environ
from yaml import safe_load

def main():
    repo_path = Path(environ.get("REPO_PATH", "."))
    workflow_path = repo_path / ".github/workflows"
    if workflow_path.is_dir():
        printed_header = False
        repo = environ.get("REPO")
        repo_name = repo.split("/")[1]
        for workflow in workflow_path.iterdir():
            if workflow.suffix == ".yml" and workflow.is_file():
                with workflow.open() as f:
                    workflow_dict = safe_load(f)
                    if on_dict := workflow_dict.get(True, {}):
                        not_excluding_main_branch = False
                        if isinstance(on_dict, str):
                            not_excluding_main_branch = on_dict == "push"
                        elif isinstance(on_dict, list):
                            not_excluding_main_branch = "push" in on_dict
                        else:
                            if on_push_duct := on_dict.get("push", {}):
                                if branches := on_push_duct.get("branches", []):
                                    not_excluding_main_branch = "!main" not in branches and "!master" not in branches
                                else:
                                    not_excluding_main_branch = True
                                if branches_ignore := on_push_duct.get("branches-ignore", []):
                                    not_excluding_main_branch = "main" not in branches_ignore and "master" not in branches_ignore
                            if on_dict.get("schedule", []):
                                not_excluding_main_branch = True
                        if not_excluding_main_branch:
                            if not printed_header:
                                print(f"## [{repo_name}](https://github.com/{repo})")
                                printed_header = True
                            name = workflow_dict.get("name", workflow.stem)
                            print(f"[![{name}](https://github.com/{repo}/actions/workflows/{workflow.name}/badge.svg)](https://github.com/{repo}/actions/workflows/{workflow.name})", end=" ")
        print()

if __name__ == "__main__":
    main()