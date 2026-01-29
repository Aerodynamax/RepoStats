from datetime import datetime, timedelta
import git

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style

# from rich (`python -m rich`'s ColorBox)
class ContributionsHeatmap:
    # [https://github.com/williambelle/github-contribution-color-graph/blob/master/src/js/contentscript.js]
    commit_heatmap_colours = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']


    def __init__(self, all_commits: list[git.Commit]) -> None:
        self.all_commits = all_commits
        
        self.this_mondays_date = datetime.today() - timedelta(days=datetime.today().weekday())



    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        # github graph starts at sunday & 2 days per row
        for y in range(-1, 6, 2):
            # go as far back as we can for the space
            for x in range(options.max_width - 1, -1, -1):
                # starting from mondays so add the days and subtract weeks
                target_day_top = self.this_mondays_date - timedelta(days=-y, weeks=x)
                target_day_bottom = self.this_mondays_date - timedelta(days=-(y+1), weeks=x)

                valid_commits_top = [ commit for commit in self.all_commits if datetime.fromtimestamp(commit.committed_date).date() == target_day_top.date() ]
                valid_commits_bottom = [ commit for commit in self.all_commits if datetime.fromtimestamp(commit.committed_date).date() == target_day_bottom.date() ]

                top_color: str = self.commit_heatmap_colours[min(len(valid_commits_top), 4)]
                
                # don't show sunday again below
                bottom_color: str = self.commit_heatmap_colours[min(len(valid_commits_bottom), 4)]
                if y+1 == 6:
                    # show dash on last week of year
                    last_week_num = datetime(2025, 12, 28).isocalendar().week

                    if ( target_day_top.isocalendar().week == last_week_num):
                        bottom_color = '#FFFFFF'
                    else:
                        bottom_color = '#000000'
                
                yield Segment("▄", Style(color=bottom_color, bgcolor=top_color))
            yield Segment.line()

    def __rich_measure__(
        self, console: "Console", options: ConsoleOptions
    ) -> Measurement:
        return Measurement(1, options.max_width)
