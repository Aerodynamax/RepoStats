from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style
from rich.color import Color

from textual_image.renderable import Image as TextualImage
import PIL.Image

class Image:

    raw_image: PIL.Image.Image
    size: tuple[int | None, int | None]

    def __init__(self, image: str | PIL.Image.Image, size: tuple[int, int] | None = None, background_color: str | tuple[int, int, int] | None = None) -> None:
        self.size = size or (None, None)

        image = image if type(image) == PIL.Image.Image else PIL.Image.open(str(image)).convert("RGBA")

        # get background colour
        bg_color: tuple[int, int, int] = self.terminal_color_to_rgb("black")

        if type(background_color) == str:
            bg_color = self.terminal_color_to_rgb(background_color)
        elif type(background_color) == tuple:
            bg_color = background_color
        
        # create solid colour backgound & merge
        self.raw_image = self.background_on_PIL_img(img=image, background_colour=bg_color)
    
    
    def background_on_PIL_img(self, img: PIL.Image.Image, background_colour: tuple[int,int,int]):
        background = PIL.Image.new(mode="RGBA", size=img.size, color=background_colour)
        return PIL.Image.alpha_composite(background, img)

    def terminal_color_to_rgb(self, colour_name: str) -> tuple[int,int,int]:
        color = Color.parse(colour_name).get_truecolor()
        return ( color.red, color.green, color.blue )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
                
        yield TextualImage( image=self.raw_image, width=self.size[0], height=self.size[1] )
        yield Segment.line()

    def __rich_measure__(
        self, console: "Console", options: ConsoleOptions
    ) -> Measurement:
        
        return Measurement(1, self.size[0] if self.size[0] is not None else options.max_width)