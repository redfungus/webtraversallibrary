# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Module containing helper functions for graphics-related operations on webdrivers and snapshots.
"""

import importlib.resources
import logging

from PIL import Image, ImageDraw, ImageFont
from selenium.webdriver.remote.webdriver import WebDriver

from .color import Color
from .geometry import Point, Rectangle
from .javascript import JavascriptWrapper

logger = logging.getLogger("wtl")


def crop_image(image: Image.Image, rect: Rectangle) -> Image.Image:
    """
    Crops the part of the image specified by its ``rect``.

    Rectangle specified by ``rect`` must lie inside of the image bounds.
    """

    # Rectangle we crop out must be somewhere within the image
    image_rect = Rectangle(Point(0, 0), Point(image.width, image.height))
    if not image_rect.contains(rect):
        raise ValueError(f"Bounds {rect} outside of image area {image_rect}")

    return image.crop(rect.bounds)


def get_device_pixel_ratio(driver: WebDriver) -> float:
    """
    Get device pixel ratio from the browser, useful to handle high density screenshots, like the ones we get on macOS.
    """
    return JavascriptWrapper(driver).execute_script("return window.devicePixelRatio;") or 1.0


def take_element_screenshot(page_screenshot: Image.Image, bbox: Rectangle) -> Image.Image:
    """
    Returns the cropped subimage with the coordinates given.
    """

    w, h = page_screenshot.size

    if bbox.area == 0:
        raise ValueError(f"Rectangle {bbox} is degenerate")
    if bbox not in Rectangle(Point(0, 0), Point(w, h)):
        raise ValueError(f"Rectangle {bbox} not contained in the viewport {(0, 0, w, h)}")

    return crop_image(page_screenshot, bbox)


def draw_rect(image: Image.Image, rect: Rectangle, color: Color, width: int):
    """
    Draws a bounding box around the specified rectangle on the image.
    """
    draw = ImageDraw.Draw(image, mode="RGBA")
    draw.rectangle(rect.bounds, outline=color.to_tuple(with_alpha=True), width=width)


def draw_text(image: Image.Image, top_left: Point, color: Color, size: int, text: str):
    """
    Draws text on a PIL image.
    """
    padding = 2
    image_width, image_height = image.size

    with importlib.resources.path("webtraversallibrary.font", "OpenSans-Regular.ttf") as filepath:
        font = ImageFont.truetype(str(filepath), size)

    # Make sure text does not exceed image boundaries
    text_width, text_height = font.getsize(text)
    draw_text_x = min(top_left.x, image_width - text_width - padding)
    draw_text_y = min(top_left.y, image_height - text_height - padding)
    draw = ImageDraw.Draw(image, mode="RGB")
    draw.text(xy=(draw_text_x, draw_text_y), text=text, fill=color.to_tuple(), font=font)
