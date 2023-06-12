import argparse
import os
import subprocess

import libwebp_util

version = '1.0.0'


def log(msg):
    print(msg)


def transform(src, dst, options):
    cmd = f"{libwebp_util.get_gif2webp()} {src} {options} -o {dst}"

    p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    log_process_ret(src, dst, p.returncode, stdout, stderr)


def log_process_ret(src, dst, return_code, stdout, stderr):
    if return_code == 0:
        dst_byte = os.stat(dst).st_size
        src_byte = os.stat(src).st_size
        log(f"success: {dst} ({format_file_size(dst_byte)}).  reduce {(1 - dst_byte / src_byte) * 100:.2f}% (origin={format_file_size(src_byte)})")
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


def process(input_dir, output_dir, option=''):
    if os.path.isfile(input_dir):
        transform(input_dir, output_dir, args.option)
    elif os.path.isdir(input_dir):
        for file in os.listdir(input_dir):
            if not file.endswith('.gif'):
                log(f"{file} is not a gif.")
                continue
            src_gif = os.path.join(input_dir, file)
            dst_webp = os.path.join(output_dir, file.replace('.gif', '.webp'))
            transform(src_gif, dst_webp, option)
    else:
        raise RuntimeError(f"Unknown Input Args. {input_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f"""
                batch gif2webp tools. v{version}
            """)
    parser.add_argument("--input", help='input file or directory', required=True)
    parser.add_argument("--output", help='output file or directory', required=True)
    parser.add_argument("--option", help='gif2webp option. default value is -lossy', required=False, default='-lossy')
    args = parser.parse_args()
    process(args.input, args.output, args.option)
