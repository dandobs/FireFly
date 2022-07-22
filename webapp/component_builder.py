import io
import os
import base64
from dash import html
from PIL import Image


def gen_img_uri(img_index, img_path=None) -> str:
    """genImgURI Open image file at provided path with PIL and encode to
    img_uri string.

    Args:
        image_path (str): Path to image file.

    Returns:
        img_uri (str): str containing image bytes viewable by html.Img
    """

    if img_path:
        im = Image.open(img_path)
    # else:
    #     img_paths = get_img_paths(redis_client, session_id, dataset_name)
    #     im = Image.open(img_paths[img_index])

    # dump it to base64
    buffer = io.BytesIO()
    filename, file_extension = os.path.splitext(img_path)
    file_extension = file_extension[1:]
    try:
        im.save(buffer, format=file_extension)
    except:
        print("Warning! Converting to RGB!!")
        im = im.convert("RGB")
        im.save(buffer, format="jpeg")

    encoded_image = base64.b64encode(buffer.getvalue()).decode()
    im_url = "data:image/jpeg;base64, " + encoded_image
    return im_url


def empty_contained_img(id: str):
    component = html.Div(
        [
            html.Img(
                id=id,
                style={
                    "width": "100%",
                    "height": "100%",
                    "min-height": "30vh",
                    "max-height": "30vh",
                    "object-fit": "contain",
                },
            )
        ]
    )
    return component
