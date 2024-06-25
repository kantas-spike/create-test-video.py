import argparse
import logging
import os
import sys
import xml.dom.minidom
import tempfile
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="テンプレートSVG画像をもとに、指定された時間分のフレーム画像を作成し、そのフレーム画像からテストビデオを作成します。"
        "フレーム画像作成時、テンプレートSVG画像のフレーム番号用テキスト要素に自動的にフレーム番号を挿入します。"
    )
    parser.add_argument(
        "-t",
        "--template_svg",
        metavar="SVG_FILE",
        required=True,
        help="テンプレートSVG画像ファイルのパス",
    )
    DEFAULT_OUTPUT_PATH = "output.mp4"
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT_FILE",
        default=DEFAULT_OUTPUT_PATH,
        help=f"作成するテストビデオのパス(デフォルト値: {DEFAULT_OUTPUT_PATH})",
    )
    DEFAULT_FPS = 60
    parser.add_argument(
        "--fps",
        default=DEFAULT_FPS,
        type=int,
        help=f"作成するテストビデオのFPS(デフォルト値: {DEFAULT_FPS})",
    )
    DEFAULT_DURATION = 1
    parser.add_argument(
        "-d",
        "--duration",
        default=DEFAULT_DURATION,
        type=int,
        help=f"作成するテストビデオの長さ[単位:秒] (デフォルト値: {DEFAULT_DURATION})",
    )
    parser.add_argument(
        "--workdir",
        help="フレーム画像生成用の作業ディレクトリのパス。未指定時は一時ディレクトリを採用",
    )
    DEFAULT_FRAMENO_ID = "frame_no"
    parser.add_argument(
        "--frameno_id",
        default=DEFAULT_FRAMENO_ID,
        help=f"SVG内でフレーム番号が記載されたtext要素のID(デフォルト値: {DEFAULT_FRAMENO_ID})",
    )
    DEFAULT_FFMPEG = "/usr/local/bin/ffmpeg"
    parser.add_argument(
        "--ffmpeg",
        metavar="FFMPEG_PATH",
        default=DEFAULT_FFMPEG,
        help=f"ffmpegコマンドのパス(デフォルト値: {DEFAULT_FFMPEG})",
    )
    parser.add_argument(
        "-v", "--verbose", help="詳細なログを出力します。", action="store_true"
    )

    return parser.parse_args()


def setup_logger(verbose=False):
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s:%(message)s")


def get_text_element(dom: xml.dom.minidom.Document, frameno_id):
    elms = dom.getElementsByTagName("text")
    target_text = None
    for elm in elms:
        if elm.getAttribute("id") == frameno_id:
            target_text = elm
            break
    return target_text


def update_frameno_in_dom(text_element: xml.dom.minidom.Element, frame_no):
    elms = text_element.getElementsByTagName("tspan")
    if len(elms) > 0:
        tspan = elms[0]
        tspan.firstChild.nodeValue = str(frame_no)
    else:
        text_element.firstChild.nodeValue = str(frame_no)


def create_frame_images(template_path, num_of_frames, wkdir_path, frameno_id):
    logger.debug(f"テンプレートファイル({template_path})をread..")
    dom = xml.dom.minidom.parse(template_path)
    text_elm = get_text_element(dom, frameno_id)
    for i in range(num_of_frames):
        frame_no = i + 1
        update_frameno_in_dom(text_elm, frame_no)
        frame_img_path = os.path.join(wkdir_path, "{:0=6}.svg".format(frame_no))
        with open(frame_img_path, "w") as f:
            dom.writexml(f, encoding="utf-8")


def create_test_video(wkdir_path, output_path, fps, ffmpeg_path):
    logger.debug(
        f"作業ディレクトリ内のフレーム画像からテストビデオ({output_path})を生成.."
    )
    glob_pattern = os.path.join(wkdir_path, "*.svg")
    cmd_line = [
        ffmpeg_path,
        "-y",
        "-r",
        str(fps),
        "-pattern_type",
        "glob",
        "-i",
        f"{glob_pattern}",
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]
    logger.info(f"cmdline: {' '.join(cmd_line)}")
    proc = subprocess.run(
        cmd_line,
        capture_output=True,
    )
    if proc.returncode == 0:
        logger.info(f"テストビデオ({output_path})の生成完了")
    else:
        logger.error("テストビデオの生成に失敗しました。")
        if proc.stdout:
            logger.debug(proc.stdout)
        if proc.stderr:
            logger.error(proc.stderr)


def main():
    args = parse_args()

    setup_logger(args.verbose)
    global logger
    logger = logging.getLogger(__name__)
    logger.debug(args)

    # region 入力情報の確認
    logger.debug("入力情報の確認..")
    template_path = os.path.abspath(os.path.expanduser(args.template_svg))
    if not os.path.isfile(template_path):
        logger.error(f"テンプレートファイル({template_path})は存在しません。")
        return 1
    logger.info(f"テンプレート: {template_path}")

    output_path = os.path.abspath(os.path.expanduser(args.output))
    if not os.path.isfile(output_path):
        output_dir = os.path.dirname(output_path)
        if not os.path.isdir(output_dir):
            logger.debug(f"出力先のディレクトリ({output_dir})が存在しないため作成..")
            os.makedirs(output_dir)
    logger.info(f"出力ファイル: {output_path}")

    logger.info(f"FPS: {args.fps}")
    num_of_frames = args.fps * args.duration
    logger.info(f"フレーム数: {num_of_frames}")

    wkdir_path = args.workdir
    tmpdir = None
    if wkdir_path is not None:
        wkdir_path = os.path.abspath(os.path.expanduser(wkdir_path))
        if not os.path.isdir(wkdir_path):
            logger.debug(f"作業ディレクトリ({wkdir_path})が存在しないため作成..")
            os.makedirs(wkdir_path)
    else:
        tmpdir = tempfile.TemporaryDirectory()
        wkdir_path = tmpdir.name
    logger.info(f"作業ディレクトリ: {wkdir_path}")
    logger.info(f"フレーム番号のID: {args.frameno_id}")

    ffmpeg_path = args.ffmpeg
    if not os.path.isfile(ffmpeg_path):
        logger.error(f"ffmpegが存在しません: {ffmpeg_path}")
        return 1
    logger.info(f"ffmpeg: {args.ffmpeg}")
    # endregion

    try:
        logger.debug("テンプレートからフレーム画像を生成..")
        create_frame_images(template_path, num_of_frames, wkdir_path, args.frameno_id)
        logger.debug("フレーム画像からテストビデオを生成..")
        create_test_video(wkdir_path, output_path, args.fps, ffmpeg_path)
    finally:
        if tmpdir:
            logger.info(f"cleanup tempdir({tmpdir.name}) ..")
            tmpdir.cleanup()


logger = None


if __name__ == "__main__":
    sys.exit(main())
