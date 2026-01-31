import os

import git
from git_wrapper import GitActor, GitRepo
from contributions_heatmap import ContributionsHeatmap
from pie_chart import PieChart

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.color import Color
from rich.align import Align
from rich.columns import Columns


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

#region project stats

# local_branches = [ head.name for head in repo.heads ]

# [https://stackoverflow.com/a/60606447]
remote_branches = list(repo.remote().refs)

branches_list: list[str] = []

for head in list(repo.heads):
    # remote_names = map(lambda remote: remote.name.removeprefix(remote_branches[0].remote_name + "/"), remote_branches)

    remote = [ remote for remote in remote_branches if remote.name.removeprefix(remote_branches[0].remote_name + "/") == head.name ]

    if len(remote) > 0:
        urls = ""
        for remote_repo in list(repo.remotes):
            if repo.remote().url.startswith("https://github.com"):
                url = repo.remote().url.removesuffix(".git") + "/tree/" + head.name

                urls += f"([link={url}]{remote_repo}[/]) "


        branches_list.append(f"{head.name} {urls}")
        
    else:
        branches_list.append(f"{head.name}")



project_stats_table = Table(
    # title="Project Info",
    box=None,
    expand=False,
    show_header=False,
    show_edge=False,
    pad_edge=False,
    padding=(1,1)
)

project_stats_table.add_row("Name", repo.name)
project_stats_table.add_row("Path", str(repo.working_dir))
project_stats_table.add_row("Remotes", "\n".join( [f"[link={remote.url}]{remote.url} ({remote.name})[/]" for remote in repo.remotes] ))
project_stats_table.add_row("Branches", "\n".join( branches_list ))
project_stats_table.add_row("Description", repo.description)

#endregion

#region contribution stats

def create_contributions_statistics_table(authors: list[GitActor]) -> Table:

    table = Table(title="Contribution Statistics")

    table.add_column("contributor", style="white", no_wrap=False)
    table.add_column("commits", style="green", no_wrap=True)
    # table.add_column("branches", style="orange3", no_wrap=True)

    # repo.untracked_files

    for author in authors:

        table.add_row(
            author.name,
            str(author.commits),
        )
    
    return table

# sort the authors by commit count
authors = list(repo.authors)
authors.sort(key=lambda author: author.commits, reverse=True)

# create pie chart data
data: dict[str, float] = {}
for author in authors:
    data[author.name or ""] = author.commits

contributions_stats = Columns(
    [
        create_contributions_statistics_table(authors=authors),
        PieChart(data=data, size=(32, 16), background_colour_rgb=(12,12,12), show_headings=True)
    ],
    align="right"
)
#endregion


# combine stats
all_stats_table = Table(
    box=None,
    expand=False,
    show_header=False,
    show_edge=False,
    pad_edge=False
)
all_stats_table.add_row(project_stats_table, Align.right(contributions_stats))


console.print(Panel(all_stats_table, title="Table view"))
