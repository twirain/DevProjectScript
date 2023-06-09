import argparse
import os
import shutil
import sys
import zipfile

join = os.path.join

version = '1.0.0'
# env
# 工作目录
work_dir = join(sys.path[0], 'work')


def clean_workspace(build_dir):
    print('清理工作室...')
    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir, exist_ok=True)
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)


def has_executable(program):
    return shutil.which(program) is not None


def build_channel_apk(apk_path, apk_channel_path, channel_list, output_dir, jks_path, jks_pass):
    """
    打渠道包
    :param apk_path: apk文件路径
    :param apk_channel_path: apk内渠道文件路径
    :param channel_list: 渠道列表文件，一行一个渠道
    :param output_dir: 输出文件路径
    :param jks_path: 密钥路径
    :param jks_pass: 密钥口令
    :return:
    """
    apk_name = os.path.splitext(os.path.basename(apk_path))[0]

    print('执行环境检测...')
    if not has_executable('zipalign'):
        raise Exception('zipalign命令不存在，确认是否将`ANDROID_SDK/build-tools/`下任意版本加入到环境变量中')
    if not has_executable('apksigner'):
        raise Exception('apksigner命令不存在，确认是否将`ANDROID_SDK/build-tools/`下任意版本加入到环境变量中')
    if not os.path.exists(apk_path):
        raise Exception("文件不存在")

    verify_ret = os.system(f"apksigner verify {apk_path}")
    if verify_ret == 0:
        raise RuntimeError("apk文件不应包含签名")

    print('生成渠道文件...')
    channel_file_name = os.path.split(apk_channel_path)[-1]
    channel_file_compress_type = None
    new_channel_file_path = join(work_dir, channel_file_name)
    with open(new_channel_file_path, mode='x'):
        pass

    print('生成无渠道文件包...')
    # 这里生成无渠道文件包的原因是：Window环境下，默认目录大小写不敏感，
    # 高版本Gradle默认开启混淆，如果全解压到目录，则会导致部分文件被覆盖
    not_channel_apk_path = join(work_dir, 'not_channel_apk.apk')
    not_channel_apk = zipfile.ZipFile(not_channel_apk_path, mode='x')
    origin_apk = zipfile.ZipFile(apk_path, 'r')
    for item in origin_apk.infolist():
        if item.filename == apk_channel_path:
            # 记录渠道文件的压缩状态
            channel_file_compress_type = item.compress_type
            continue
        # 这里主要是维持原包的压缩状态，兼容androidR+的要求（resources.arsc不能被压缩）
        # 因为加固一般都是用的apktool去反编译，因此这里只要维持原压缩状态就行了
        not_channel_apk.writestr(item, origin_apk.read(item.filename), item.compress_type)
    not_channel_apk.close()
    origin_apk.close()

    print('处理渠道...')
    fd = open(channel_list, mode='r')
    channels = fd.readlines()
    for channel_name in channels:
        channel_name = channel_name.strip('\n')
        print('==================================')
        print('渠道：' + channel_name)
        product_path = join(output_dir, f'{apk_name}_{channel_name}.apk')

        # 写入渠道信息
        with open(new_channel_file_path, mode='w') as p:
            p.write(channel_name)

        # 拷贝无渠道包体
        shutil.copy(not_channel_apk_path, product_path)

        # 写入渠道文件
        with zipfile.ZipFile(product_path, mode='a') as z:
            z.write(new_channel_file_path, apk_channel_path, channel_file_compress_type)

        # 对齐
        zipalign_temp = join(work_dir, 'zipalign_temp.apk')
        zipalign_result = os.system(f'zipalign -p -f 4 {product_path} {zipalign_temp}')
        os.remove(product_path)
        shutil.move(zipalign_temp, product_path)
        print(f'对齐完成：{zipalign_result}')

        # 签名
        sign_result = os.system('apksigner sign --ks %s --ks-pass pass:%s %s' % (jks_path, jks_pass, product_path))
        print(f'签名完成：{sign_result}')

    print('清理工作室...')
    shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f"""
            apk_channel package build tools. v{version}
            The core functionality is modify assets/<apk_channel> files. input non-signal apk file
            and apk_channel list that each line contain one apk_channel name, output signal-apk_channel apk files.
        """)
    parser.add_argument("--apk", help='origin non-signal apk file', required=True)
    parser.add_argument("--apk-channel-path", help='apk_channel file path in apk', required=True)
    parser.add_argument("--apk_channel", help='apk_channel list', required=True)
    parser.add_argument("--jks", help='java keystore', required=True)
    parser.add_argument("--jks-pass", help='jks password', required=True)
    parser.add_argument("--output", help='output path, default value is <pwd>/build', required=False,
                        default=join(sys.path[0], 'build'))
    args = parser.parse_args()
    clean_workspace(args.output)
    build_channel_apk(args.apk, args.apk_channel_path, args.apk_channel, args.output, args.jks, args.jks_pass)
