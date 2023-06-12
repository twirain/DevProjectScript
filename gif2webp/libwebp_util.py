import os
import platform
import zipfile

linux_zip = os.path.join(os.path.dirname(__file__), 'libwebp', 'libwebp-1.3.0-linux-x86-64.tar.gz')
mac_arm_zip = os.path.join(os.path.dirname(__file__), 'libwebp', 'libwebp-1.3.0-mac-arm64.tar.gz')
mac_zip = os.path.join(os.path.dirname(__file__), 'libwebp', 'libwebp-1.3.0-mac-x86-64.tar.gz')
windows_zip = os.path.join(os.path.dirname(__file__), 'libwebp', 'libwebp-1.3.0-windows-x64.zip')


def _get_zip_by_system():
    system = platform.system()
    is_arm_arch = 'arm' in platform.machine()
    is_32bit = platform.architecture() == '32bit'
    if system == 'Linux':
        return linux_zip
    elif system == 'Windows':
        if is_32bit:
            return ''
        else:
            return windows_zip
    elif system == 'Darwin':
        if is_arm_arch:
            return mac_arm_zip
        else:
            return mac_zip


def get_gif2webp():
    libwebp_zip = _get_zip_by_system()
    tmp_libwebp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    system = platform.system()

    if not os.path.exists(tmp_libwebp_dir):
        with zipfile.ZipFile(libwebp_zip, 'r') as z:
            z.extractall(tmp_libwebp_dir)

    extension = ''
    if system == 'Windows':
        extension = '.exe'
    parent_dir_name = os.listdir(tmp_libwebp_dir)[0]
    return os.path.join(tmp_libwebp_dir, parent_dir_name, 'bin', f"gif2webp{extension}")
