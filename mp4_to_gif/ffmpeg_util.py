import os
import platform
import zipfile

window_zip = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg-6.0-essentials_build.zip')


def get_ffmpeg():
    system = platform.system()
    if system != 'Windows':
        raise RuntimeError(f"Not Support Platform! {system}")

    tmp_install_dir = os.path.join(os.path.dirname(__file__), 'tmp')

    if not os.path.exists(tmp_install_dir):
        with zipfile.ZipFile(window_zip, 'r') as z:
            z.extractall(tmp_install_dir)

    extension = ''
    if system == 'Windows':
        extension = '.exe'
    parent_dir_name = os.listdir(tmp_install_dir)[0]
    return os.path.join(tmp_install_dir, parent_dir_name, 'bin', f"ffmpeg{extension}")
