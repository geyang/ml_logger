import base64
import textwrap
from collections import defaultdict
from io import BytesIO
from textwrap import dedent

import PIL.Image as pImage
import numpy as np
from IPython.display import display, HTML


class Image:
    data = None
    title = None

    def __init__(self, rgb=None, filename=None, title=None):
        self.title = title
        if rgb is not None:
            self.data = np.array(rgb).astype(np.uint8)

        self.filename = filename

    @property
    def base64(self):
        if self.data is not None:
            with BytesIO() as buf:
                pImage.fromarray(self.data).save(buf, "png")
                return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')
        elif self.filename is not None:
            with open(self.filename, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                return encoded

    @property
    def _html(self):
        if self.title is not None:
            return f'<div><div style="text-align: center">{self.title}</div>' \
                   f'<img style="margin: 0.5em" src="{self.base64 or ""}"/></div>'
        return f'<img style="margin: 0.5em" src="{self.base64 or ""}"/>'


class Text:
    def __init__(self, *args, sep=" ", end="\n", dedent=None):
        t = sep.join(args) + end
        if len(args) == 1:
            dedent = True

        if dedent:
            t = textwrap.dedent(t)
        self._html = f"<div>{t}<div>"


buffer = []


def imshow(img=None, title=None):
    buffer.append(Image(rgb=img, title=title))


def text(*args, sep=" ", end="\n", dedent=None):
    buffer.append(Text(*[a if isinstance(a, str) else str(a) for a in args], sep=sep, end=end, dedent=dedent))


def show(*imgs, titles=None):
    # get parent stack code.

    if titles is None:
        titles = [None] * len(imgs)

    for img, title in zip(imgs, titles):
        buffer.append(Image(rgb=img, title=title))

    # todo: support titles shorter than images.
    string = dedent(
        f"""<div style="display: flex; flex-wrap:wrap; align-items: top; font-family: Times New Roman">{
        ''.join([el._html for el in buffer])}</div>""")

    buffer.clear()
    return display(HTML(string))
