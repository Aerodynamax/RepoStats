import os
from typing import Generator

import git
from git_wrapper import GitRepo
from contributions_heatmap import ContributionsHeatmap

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.color import Color

from textual_image.renderable import Image
from PIL import Image as PILImage

console = Console()


# [https://stackoverflow.com/a/74677730]
def scan_tree_for_git_dirs(path: str) -> Generator[os.DirEntry]:
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        try:
            if entry.is_dir(follow_symlinks=False):
                yield entry
                
                if entry.name != ".git":
                    yield from scan_tree_for_git_dirs(entry.path)

        except PermissionError:
            continue

# [https://stackoverflow.com/a/6227623]
path = os.path.expanduser("~\\Documents")

folder = " "
while folder != "" and not os.path.isdir(folder):
    folder = console.input(f"folder to scan ({path}): ")

folder = folder or path

username = console.input("your Git username (empty for all repos): ")

repos: list[GitRepo] = []


with console.status("finding repos ..."):

    for entry in scan_tree_for_git_dirs(folder):
        if entry.name == ".git":

            try:
                repo = GitRepo(path=entry.path, search_parent_directories=True)

                if username != "":

                    # only repos i contributed to
                    if not any( username == author.name for author in repo.authors ):
                        continue

                # skip exact duplicate repos
                if repo.commits in [ repo.commits for repo in repos]:
                    console.log(f"skipping repeat repo at: {entry.path}")
                    continue
                
                repos.append( repo )

                console.log(f"found repo at: {entry.path}")
            except git.InvalidGitRepositoryError:
                console.log(f"skipping invalid repo at: {entry.path}")

console.log(f"found: {len(repos)} repos!")

console.log("Generating report ...")

common_prefix = os.path.commonprefix([ repo.working_dir for repo in repos ])

# get all my contributions
commits = sum([ repo.commits for repo in repos ], [])
commits = [ commit for commit in commits if (not username) or commit.author.name == username ]

heatmap = ContributionsHeatmap(all_commits=commits, console=console)

#region render git icon

# image from: https://git-scm.com/community/logos
img = PILImage.open("assets/Git-Icon.png").convert("RGBA")

# my terminal's bg colour
background_color = Color.from_rgb(12, 12, 12).get_truecolor()

background = PILImage.new(mode="RGBA", size=img.size, color=(background_color.red, background_color.green, background_color.blue))

img = PILImage.alpha_composite(background, img)

image = Image(image=img, width=16, height=8)

#endregion

contributions_table = Table(
    box=None,
    expand=False,
    show_header=False,
    show_edge=False,
    pad_edge=False
)
contributions_table.add_row(image, Panel(heatmap, title="Contributions heatmap"))

console.print( contributions_table )


#region render stats table

table = Table(title="Statistics")

table.add_column("repo name", style="cyan", no_wrap=True)
table.add_column("path", style="bright_black", no_wrap=False)
table.add_column("remotes", style="cyan", no_wrap=False)
table.add_column("commits", style="green", no_wrap=True)
table.add_column("branches", style="orange3", no_wrap=True)
table.add_column("contributors", style="white", no_wrap=False)

repos.sort(key=lambda repo: len(repo.commits), reverse=True)

for repo in repos:
    # sort the authors by commit count
    authors = list(repo.authors)
    authors.sort(key=lambda author: author.commits, reverse=True)

    names = [ author.name for author in authors if author.name is not None ]
    remotes = list(repo.remotes)

    table.add_row(
        repo.name,
        os.path.dirname(repo.working_dir).replace(common_prefix, "…\\"),
        "\n".join(f"[link={remote.url}]{remote.name}[/]" for remote in remotes[:4]) if any(remotes) else "None",
        str(len(repo.commits)),
        str(len(repo.branches)),
        ", ".join(names[:4]) + ( ", …" if len(names) > 4 else "" ) if any(names) else "None"
    )

console.print(Panel(table, title="Table view"))

#endregion