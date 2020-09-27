import click
import re
from . import ffmpeg
from .utils import _run_command


def _is_mp4(ctx, param, value):
    if not re.match(r"\.mp4$", value):
        raise click.BadParameter("Output file must be .mp4")


@ffmpeg.command(help="Convert to mp4 for import to DaVinci Resolve.")
@click.argument("input_filename", type=click.Path(exists=True))
@click.argument("output_filename", required=True, type=str, callback=_is_mp4)
def resolve_mp4(input_filename, output_filename):
    _run_command(
        f"""
        ffmpeg -i "{input_filename}" \
        -c:v libx264 -pix_fmt yuv420p -crf 16 \
        -force_key_frames 'expr:gte(t,n_forced/2)' -bf 2 \
        -vf yadif -use_editlist 0 \
        -movflags +faststart \
        -c:a aac -q:a 1 \
        -ac 2 -ar 48000 \
        -f mp4 "{output_filename}"
        """
    )
