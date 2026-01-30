import os
from typing import Generator

import git
import git.config
from git_wrapper import GitRepo
from contributions_heatmap import ContributionsHeatmap
from pie_chart import PieChart

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.color import Color
from rich.align import Align


from textual_image.renderable import Image
from PIL import Image as PILImage

console = Console()


# [https://stackoverflow.com/a/6227623]
path = os.path.expanduser("~\\Documents")

folder = " "
while folder != "" and not os.path.isdir(folder):
    folder = console.input(f"Git repo path ({path}): ")

folder = folder or path

repo: GitRepo

try:
    repo = GitRepo(path=folder, search_parent_directories=True)
    
    console.log(f"loaded repo at: {folder}")
except git.InvalidGitRepositoryError:
    console.log(f"Repo is invalid (Repo folder: {folder})")
    exit(1)

console.log("Generating report ...")


# get all my contributions (excluding repeats)
commits = list(set(repo.commits))

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

table = Table(title="Contribution Statistics")

table.add_column("contributor", style="white", no_wrap=False)
table.add_column("commits", style="green", no_wrap=True)
# table.add_column("branches", style="orange3", no_wrap=True)

# repo.untracked_files

# sort the authors by commit count
authors = list(repo.authors)
authors.sort(key=lambda author: author.commits, reverse=True)

for author in authors:

    table.add_row(
        author.name,
        str(author.commits),
    )

table_view = Table(
    box=None,
    expand=False,
    show_header=False,
    show_edge=False,
    pad_edge=False,
)
table_view.add_column(justify="right", vertical="middle")
table_view.add_column(justify="center", vertical="middle")

data: dict[str, float] = {}
for author in authors:
    data[author.name or ""] = author.commits

table_view.add_row(table, PieChart(data=data, size=(32, 16), background_colour_rgb=(12,12,12), show_headings=True))

console.print(Panel(Align.center(table_view), title="Table view"))

#endregion