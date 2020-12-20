import os, re
import hashlib
from Crypto.Cipher import AES
from Crypto import Random


def get_items_list(path):
    arr = os.listdir(path)
    files = [f for f in arr if os.path.isfile(os.path.join(path, f)) and re.search('\.enc$', f)]
    files.sort(key=lambda y: y.lower())
    direc = [d for d in arr if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
    direc.sort(key=lambda y: y.lower())
    return files, direc


def populate_files(file_view, path, files):
    file_view.delete(*file_view.get_children())
    for f in files:
        file_path = os.path.join(path, f)
        file_view.insert('', 'end', file_path, text=f)


def populate_dir_list(dir_view, dir_id, dirs):
    for d in dirs:
        iid = os.path.join(dir_id, d)
        dir_view.insert(dir_id, 'end', iid, text=d)


def check_and_populate(dir_view, file_view, parent):
    files, dirs = get_items_list(parent)
    if not parent == '':
        has_child = len(dir_view.get_children(parent))
        if not has_child:
            populate_dir_list(dir_view, parent, dirs)
    populate_files(file_view, parent, files)


def read_raw(file_path):
    file = open(file_path, 'rb')
    content = file.read()
    file.close()
    return content


def write_raw(content, file_path):
    file = open(file_path, 'wb')
    file.write(content)
    file.close()


def convert_file(file_path, key_str):
    key, iv = get_key_iv(key_str)
    image = read_raw(file_path)
    cipher = create_cipher(key, iv)
    enc_data = cipher.encrypt(image)
    return iv + enc_data


def encrypt_file(file: str, target_path: str, key: str):
    file_name = file.split('/')[-1] + '.enc'
    image = convert_file(file, key)
    write_raw(image, os.path.join(target_path, file_name))


def decrypt_file(file: str, key_str: str):
    # image = convert_file(file, key)
    encrypt_data = read_raw(file)
    key = key_encode(key_str)
    iv = encrypt_data[:AES.block_size]
    cipher = create_cipher(key, iv)
    image = cipher.decrypt(encrypt_data[AES.block_size:])
    return image


def get_key_iv(key_str):
    key = key_encode(key_str)
    iv = Random.new().read(AES.block_size)
    return key, iv


def key_encode(key_str):
    return hashlib.sha256(key_str.encode()).digest()


def create_cipher(key, iv=None):
    return AES.new(key, AES.MODE_CFB, iv)


def create_directory(parent_path, folder_path):
    newdir = os.path.join(parent_path, folder_path)
    if os.path.isdir(newdir):
        return False
    else:
        os.mkdir(newdir)
        return True


def scale_size(width, height):
    reverse = width < height
    if reverse:
        width, height = height, width
    ratio = width / height
    scale_ratio = 1000 / width
    scaled_width = int(width * scale_ratio)
    scaled_height = int(height * scale_ratio)
    if reverse:
        scaled_width, scaled_height = scaled_height, scaled_width
    return scaled_width, scaled_height


def check_and_delete(file_loc):
    if os.path.isfile(file_loc):
        os.remove(file_loc)