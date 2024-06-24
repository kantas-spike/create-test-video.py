import argparse
import logging
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="テンプレートSVG画像から、指定された時間分のテストビデオを作成します。"
    )
    parser.add_argument(
        "--template_svg",
        metavar="SVG_FILE",
        required=True,
        help="テンプレートSVG画像ファイルのパス",
    )
    parser.add_argument(
        "--output",
        metavar="OUTPUT_FILE",
        default="output.mp4",
        help="作成するテストビデオのパス",
    )
    parser.add_argument("--fps", default=60, type=int, help="作成するテストビデオのFPS")
    parser.add_argument(
        "--duration", default=1, type=int, help="作成するテストビデオの長さ(単位:秒)"
    )
    parser.add_argument("--workdir", help="フレーム画像生成用の作業ディレクトリのパス")
    parser.add_argument(
        "--frameno_id",
        default="frame_no",
        help="SVG内でフレーム番号が記載されたtext要素のID",
    )
    parser.add_argument(
        "--ffmpeg", help="ffmpegコマンドのパス", default="/usr/local/bin/ffmpeg"
    )

    return parser.parse_args()


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)


def create_frame_images(template_path, num_of_frames, wkdir_path, frameno_id):
    logger.debug(f"テンプレートファイル({template_path})をread..")
    for i in range(num_of_frames):
        frame_no = i + 1
        frame_no % 10 == 0 and logger.debug(
            f"テンプレートのフレーム番号を{frame_no}に置換"
        )
        frame_no % 10 == 0 and logger.debug(
            f"テンプレートファイルから{frame_no}番目のフレーム画像をwrite.."
        )


def create_test_video(output_path, fps, ffmpeg_path):
    logger.debug(
        f"作業ディレクトリ内のフレーム画像からテストビデオ({output_path})を生成.."
    )


def main():
    args = parse_args()
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
    if wkdir_path is not None:
        wkdir_path = os.path.abspath(os.path.expanduser(wkdir_path))
        if not os.path.isdir(wkdir_path):
            logger.debug(f"作業ディレクトリ({wkdir_path})が存在しないため作成..")
            os.makedirs(wkdir_path)
    logger.info(f"作業ディレクトリ: {wkdir_path}")
    logger.info(f"フレーム番号のID: {args.frameno_id}")

    ffmpeg_path = args.ffmpeg
    if not os.path.isfile(ffmpeg_path):
        logger.error(f"ffmpegが存在しません: {ffmpeg_path}")
        return 1
    logger.info(f"ffmpeg: {args.ffmpeg}")
    # endregion

    logger.debug("テンプレートからフレーム画像を生成..")
    create_frame_images(template_path, num_of_frames, wkdir_path, args.frameno_id)
    logger.debug("フレーム画像からテストビデオを生成..")
    create_test_video(output_path, args.fps, ffmpeg_path)


setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    sys.exit(main())
