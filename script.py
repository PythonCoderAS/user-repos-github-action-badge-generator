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
        other = []
        for workflow in sorted(workflow_path.iterdir(), key=lambda f: str(f).lower()):
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
                        name = workflow_dict.get("name", workflow.stem)
                        if not_excluding_main_branch:
                            if not printed_header:
                                print(f"## [{repo_name}](https://github.com/{repo})")
                                printed_header = True
                            print(f"[![{name}](https://github.com/{repo}/actions/workflows/{workflow.name}/badge.svg)](https://github.com/{repo}/actions/workflows/{workflow.name})", end=" ")
                        else:
                            other.append({"name": name, "workflow_file_name": workflow.name})
        if printed_header:
            print("\n")
        if other:
            if not printed_header:
                print(f"## [{repo_name}](https://github.com/{repo})")
                printed_header = True
            print("### Other Workflows")
            for workflow in other:
                name = workflow["name"]
                workflow_file_name = workflow["workflow_file_name"]
                print(f"[![{name}](https://github.com/{repo}/actions/workflows/{workflow_file_name}/badge.svg)](https://github.com/{repo}/actions/workflows/{workflow_file_name})", end=" ")
        if printed_header:
            print("\n")

if __name__ == "__main__":
    main()
