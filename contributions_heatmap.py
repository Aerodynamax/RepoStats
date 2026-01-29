from datetime import date, datetime, timedelta
import git
import math
import statistics

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style

# from rich (`python -m rich`'s ColorBox)
class ContributionsHeatmap:
    # [https://github.com/williambelle/github-contribution-color-graph/blob/master/src/js/contentscript.js]
    commit_heatmap_colours = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
    year_divider_colour = '#2e3948'

    all_commits: list[git.Commit] = []

    commits_by_date: dict[date, int] = {}
    
    total_commits: int = 0

    max_brightness: int = 1

    def __init__(self, all_commits: list[git.Commit], console: Console) -> None:
        self.console = console

        self.all_commits = all_commits

        self.this_mondays_date = datetime.today() - timedelta(days=datetime.today().weekday())
        
        self.total_commits = len(all_commits)

        # done on render
        # self.load_commit_dates(all_commits)

    q1: float = 0
    q2: float = 0
    q3: float = 0

    def calculate_quartiles(self):
        commit_counts = [ commit_count for commit_count in self.commits_by_date.values() ]

        quartiles = statistics.quantiles(data=commit_counts, n=4)

        # iqr = quartiles[2] - quartiles[0]

        # # remove outliers & do calculation again
        # commit_counts = [ commit_count for commit_count in commit_counts if commit_count < (quartiles[1] + iqr) and commit_count > (quartiles[1] - iqr) ]

        # quartiles = statistics.quantiles(data=commit_counts, n=4)

        self.q1 = quartiles[0]
        self.q2 = quartiles[1]
        self.q3 = quartiles[2]
    
    def colour_from_quartile(self, commit_count: int = 0) -> str:
        if commit_count > self.q3:
            return self.commit_heatmap_colours[4]
        if commit_count > self.q2:
            return self.commit_heatmap_colours[3]
        if commit_count > self.q1:
            return self.commit_heatmap_colours[2]
        if commit_count > 0:
            return self.commit_heatmap_colours[1]
        
        return self.commit_heatmap_colours[0]

    def load_commit_dates(self, commits: list[git.Commit], furthest_back: date):
        for commit in commits:
            
            if commit.committed_datetime.date() < furthest_back:
                continue

            if commit.committed_datetime.date() not in self.commits_by_date:
                self.commits_by_date[commit.committed_datetime.date()] = 1
            
            else:
                self.commits_by_date[commit.committed_datetime.date()] += 1


        self.total_commits = 0
        # find brightest
        for commits_date, count in self.commits_by_date.items():
            self.max_brightness = max(self.max_brightness, count)
            self.total_commits += count

        self.calculate_quartiles()

        self.console.log(f"highest commit count in one day: {self.max_brightness}")

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        # get amount of years shown
        first_date = self.this_mondays_date - timedelta(weeks=(options.max_width - 1))

        years = timedelta(weeks=(options.max_width - 1)).days / 365.25

        # load all commits
        self.commits_by_date = {}
        self.load_commit_dates(commits=self.all_commits, furthest_back=first_date.date())


        yield Segment(f"showing {self.total_commits} contributions over the past {round(years, 1) if int(years) != years else years} years")
        yield Segment.line()

        # render year lines on top as well
        for x in range(options.max_width - 1, -1, -1):

            target_day = self.this_mondays_date - timedelta(weeks=x)
            
            # show dash on last week of year
            last_week_num = datetime(target_day.year, 12, 28).isocalendar().week


            if ( target_day.isocalendar().week == last_week_num ):
                bottom_color = self.year_divider_colour
            else:
                bottom_color = 'black'

            
            yield Segment("▄", Style(color=bottom_color))
        yield Segment.line()


        # github graph starts at sunday & 2 days per row
        for y in range(-1, 6, 2):
            # go as far back as we can for the space & range() stops one before last
            for x in range(options.max_width - 1, -1, -1):
                # starting from mondays so add the days and subtract weeks
                target_day_top = self.this_mondays_date - timedelta(days=-y, weeks=x)
                target_day_bottom = self.this_mondays_date - timedelta(days=-(y+1), weeks=x)

                # get commits if present
                valid_commits_top = 0
                if target_day_top.date() in self.commits_by_date:
                    valid_commits_top = self.commits_by_date[ target_day_top.date() ]
                
                valid_commits_bottom = 0
                if target_day_bottom.date() in self.commits_by_date:
                    valid_commits_bottom = self.commits_by_date[ target_day_bottom.date() ]

                # self.console.log(f"bottom color: {valid_commits_bottom}")

                top_color: str = self.colour_from_quartile(commit_count=valid_commits_top)
                bottom_color: str = self.colour_from_quartile(commit_count=valid_commits_bottom)

                # don't show sunday again below
                if y+1 == 6:
                    bottom_color = 'black'


                # show dash on last week of year
                last_week_num = datetime(target_day_top.year, 12, 28).isocalendar().week
                
                if ( target_day_bottom.isocalendar().week == last_week_num ):
                    if valid_commits_top == 0:
                        top_color = self.year_divider_colour
                    if valid_commits_bottom == 0 or y+1 == 6:
                        bottom_color = self.year_divider_colour

                
                yield Segment("▄", Style(color=bottom_color, bgcolor=top_color))
            yield Segment.line()

    def __rich_measure__(
        self, console: "Console", options: ConsoleOptions
    ) -> Measurement:
        return Measurement(1, options.max_width)
