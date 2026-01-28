import os
from typing import Generator
import git


# [https://stackoverflow.com/a/74677730]
def scan_tree_for_dirs(path: str) -> Generator[os.DirEntry]:
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        try:
            if entry.is_dir(follow_symlinks=False):
                yield entry
                yield from scan_tree_for_dirs(entry.path)
        except PermissionError:
            continue

username = input("your Git username: ")

print("finding repos ...")

repos: list[git.Repo] = []

# [https://stackoverflow.com/a/6227623]
path = os.path.expanduser("~/Documents")

for entry in scan_tree_for_dirs(path):
    if entry.name == ".git":
        repos.append( git.Repo(path=entry.path) )

        print(entry.path)

print(f"found: {len(repos)} repos!")

print("\nStats:")

for repo in repos:
    commits = list(repo.iter_commits("--all"))
    authors = set( commit.author for commit in commits )
    names = [ author.name for author in authors if author.name is not None ]

    # only repos i contributed to
    if username not in names:
        continue

    print("\nrepo: " + os.path.basename(repo.working_dir))
    print("path: " + os.path.dirname(repo.working_dir))
    print(f"remotes: {len(repo.remotes)}")

    print("active branch: " + repo.active_branch.name)

    print(f"total commits: {len(commits)}")

    print(f"authors: {", ".join(names)}")