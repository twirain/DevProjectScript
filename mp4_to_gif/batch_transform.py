import argparse
import os
import subprocess

import ffmpeg_util


def transform(mp4_file, output_gif_file, option=''):
    # .\ffmpeg.exe -i .\test.mp4 -vf scale=343:-1,fps=12 -gifflags +transdiff output.gif
    cmd = f"{ffmpeg_util.get_ffmpeg()} -i {mp4_file} {option} {output_gif_file}"
    p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    return_code = p.returncode
    log_process_ret(mp4_file, output_gif_file, return_code, stdout, stderr)


def log_process_ret(src, dst, return_code, stdout, stderr):
    # todo: why use -fs option will cause error return? but result is right.
    if return_code == 0 or return_code == 3753488571:
        dst_byte = os.stat(dst).st_size
        log(f"success: {dst} ({format_file_size(dst_byte)}).")
    else:
        log(f"failure! source={src}, err={stderr}")


def format_file_size(byte_size):
    """
    Format file size to human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if byte_size < 1024.0:
            return f"{byte_size:.2f} {unit}"
        byte_size /= 1024.0
    return f"{byte_size:.2f} TB"


def log(msg):
    print(msg)


def process(input_dir, output_dir, option=''):
    if os.path.isfile(input_dir):
        transform(input_dir, output_dir, args.option)
    elif os.path.isdir(input_dir):
        for file in os.listdir(input_dir):
            if not file.endswith('.mp4'):
                log(f"{file} is not a mp4 file.")
                continue
            src_mp4 = os.path.join(input_dir, file)
            dst_gif = os.path.join(output_dir, file.replace('.mp4', '.gif'))
            transform(src_mp4, dst_gif, option)
    else:
        raise RuntimeError(f"Unknown Input Args. {input_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help='input file or directory', required=True)
    parser.add_argument("--output", help='output file or directory', required=True)
    parser.add_argument("--option", help='ffmpeg option', required=False)
    args = parser.parse_args()
    process(args.input, args.ouput, args.option)
