import matplotlib.pyplot as plt
import matplotlib
import matplotlib.figure
matplotlib.use('agg')  # turn off interactive backend [https://stackoverflow.com/q/79604132]

import numpy as np
import io

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style
import rich.color

from textual_image.renderable import Image as TextualImage
import PIL.Image

class PieChart:

    data: dict[str, float] = {}
    size: tuple[int, int] = (16, 8)

    def resize(self, width: int, height: int) -> None:
        self.size = (width, height)

    # [https://stackoverflow.com/a/79604175]
    def fig_to_PIL_img(self, fig: matplotlib.figure.Figure) -> PIL.Image.Image:
        # img: PIL.Image
        with io.BytesIO() as buffer:  
            fig.canvas.draw()
            fig.savefig(buffer, transparent=True, bbox_inches='tight')
            buffer.seek(0)
            img = PIL.Image.open(buffer)
            img.load()  # <-- force PIL to load image
        plt.close()
        
        return img.convert("RGBA")

    def background_on_PIL_img(self, img: PIL.Image.Image, background_colour: tuple[int,int,int]):
        background = PIL.Image.new(mode="RGBA", size=img.size, color=background_colour)
        return PIL.Image.alpha_composite(background, img)

    def terminal_color_to_rgb(self, colour_name: str) -> tuple[int,int,int]:
        color = rich.color.Color.parse(colour_name).get_truecolor()
        return ( color.red, color.green, color.blue )

    def __init__(self, data: dict[str, float], size: tuple[int, int], background_colour_rgb: tuple[int, int, int] | None = None, show_headings: bool = True) -> None:
        self.show_headings = show_headings
        self.data = data
        self.size = size

        dataset = np.array( list(data.values()) )

        fig, ax = plt.subplots()

        # create pie chart [https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html]
        ax.pie(
            x=dataset,
            labels=list(data.keys()) if show_headings else None,
            labeldistance=0.5,
            textprops={
                "color": "w",
                "fontweight": "bold",
                "size": "15"
            },
            # autopct="%1.1f%%" # percentages
        )

        # [https://stackoverflow.com/a/61754995]
        fig = plt.gcf()

        self.image = self.fig_to_PIL_img(fig=fig)

        self.image = self.background_on_PIL_img(
            img=self.image,
            background_colour=(background_colour_rgb if background_colour_rgb is not None else self.terminal_color_to_rgb("black"))
        )



    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        
        yield TextualImage(image=self.image, width=self.size[0], height=self.size[1])
        yield Segment.line()

    def __rich_measure__(
        self, console: "Console", options: ConsoleOptions
    ) -> Measurement:
        return Measurement(1, self.size[0]) # width