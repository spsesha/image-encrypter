import os
import re
import file_encypt as fe


def get_items_list(path, hidden=False):
    """
    Get the list of files and directory in the provided path

    :param path: Path of the directory which content needs to be listed
    :param hidden: Flag to include hidden folders or not
    :return: Tuple of files and folders
    """
    arr = os.listdir(path)
    files = [f for f in arr if os.path.isfile(os.path.join(path, f)) and re.search('\.enc$', f)]
    files.sort(key=lambda y: y.lower())
    direc = [d for d in arr if os.path.isdir(os.path.join(path, d)) and (d != '.' and d != '..')]
    if not hidden:
        direc = [d for d in direc if not d.startswith('.')]
    direc.sort(key=lambda y: y.lower())
    return files, direc


def create_directory(parent_path, new_folder):
    """
    Create a new folder under the parent folder

    :param parent_path: Parent folder path
    :param new_folder: New folder name
    :return: Boolean based on directory created or not
    """
    newdir = os.path.join(parent_path, new_folder)
    if os.path.isdir(newdir):
        return False
    else:
        os.mkdir(newdir)
        return True


def read_raw(file_path):
    """
    Read the file content as raw and return

    :param file_path: File to be read
    :return: Raw content of the file
    """
    file = open(file_path, 'rb')
    content = file.read()
    file.close()
    return content


def write_raw(content, file_path):
    """
    Write the raw content to the file

    :param content: Raw content to be written
    :param file_path: Destination filename
    :return: None
    """
    file = open(file_path, 'wb')
    file.write(content)
    file.close()


def convert_content(file_path, key_str):
    """
    Convert the content of the file to encrypted data

    :param file_path: path of the file with name
    :param key_str: Security key
    :return: Encrypted content of the file
    """
    key, iv = fe.get_key_iv(key_str)
    image = read_raw(file_path)
    cipher = fe.create_cipher(key, iv)
    enc_data = cipher.encrypt(image)
    return iv + enc_data


def encrypt_file(file, target_path, key):
    """
    Encrypt the content of the file and write it to the target file

    :param file: Source file that needs to be encrypted
    :param target_path: Target file path
    :param key: Security key
    :return: None
    """
    file_name = file.split('/')[-1] + '.enc'
    image = convert_content(file, key)
    write_raw(image, os.path.join(target_path, file_name))


def decrypt_file(file, key_str):
    """
    Decrypt the encrypted file and return the data

    :param file: Encrypted file
    :param key_str: Security key
    :return: Decrypted image content
    """
    encrypt_data = read_raw(file)
    key = fe.key_encode(key_str)
    iv = encrypt_data[:fe.AES.block_size]
    cipher = fe.create_cipher(key, iv)
    image = cipher.decrypt(encrypt_data[fe.AES.block_size:])
    return image


def check_and_delete(file_loc):
    """
    Check and delete the file if presents

    :param file_loc: filename with path
    :return: None
    """
    if os.path.isfile(file_loc):
        os.remove(file_loc)