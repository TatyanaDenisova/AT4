import string
import random
import pytest
import yaml
from datetime import datetime

from checkers import ssh_checkout, getout, ssh_get, checkout
from files import upload_files

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)


@pytest.fixture(autouse=True, scope="module")
def make_folders():
    return ssh_checkout("0.0.0.0", "user2", "123",
                        "mkdir -p {} {} {} {}".format(data["folder_in"], data["folder_in"], data["folder_ext"],
                                                      data["folder_ext2"]),
                        "")


@pytest.fixture(autouse=True, scope="class")
def make_files():
    list_off_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if ssh_checkout("0.0.0.0", "user2", "123",
                        "cd {}; dd if=/dev/urandom of={} bs={} count=1 iflag=fullblock".format(data["folder_in"],
                                                                                               filename,
                                                                                               data["bs"]), ""):
            list_off_files.append(filename)
    return list_off_files


@pytest.fixture(autouse=True, scope="class")
def clear_folders():
    return ssh_checkout("0.0.0.0", "user2", "123",
                        "rm -rf {}/* {}/* {}/* {}/*".format(data["folder_in"], data["folder_in"], data["folder_ext"],
                                                            data["folder_ext2"]), "")


@pytest.fixture()
def make_bad_arx():
    ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z a {}/bad_arx".format(data["folder_in"], data["folder_out"]),
                 "Everything is Ok")
    ssh_checkout("0.0.0.0", "user2", "123", "truncate -s 1 {}/bad_arx.7z".format(data["folder_out"]), "")


@pytest.fixture()
def make_subfolder():
    testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if not ssh_checkout("0.0.0.0", "user2", "123", "cd {}; mkdir {}".format(data["folder_in"], subfoldername), ""):
        return None, None
    if not ssh_checkout("0.0.0.0", "user2", "123",
                        "cd {}/{}; dd if=/dev/urandom of={} bs=1M count=1 iflag=fullblock".format(data["folder_in"],
                                                                                                  subfoldername,
                                                                                                  testfilename), ""):
        return subfoldername, None
    else:
        return subfoldername, testfilename
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(autouse=True, scope="module")
def deploy():
    res = []
    upload_files("0.0.0.0", "user2", "123", "/home/user/p7zip-full.deb", "/home/user2/p7zip-full.deb")
    res.append(ssh_checkout("0.0.0.0", "user2", "123", "echo '123' | sudo -S dpkg -i /home/user2/p7zip-full.deb",
                            "Настраивается пакет"))
    res.append(ssh_checkout("0.0.0.0", "user2", "123", "echo '123' | sudo -S dpkg -s p7zip-full",
                            "Status: install ok installed"))
    return all(res)


@pytest.fixture(autouse=True)
def stat():
    yield
    stat = ssh_get("0.0.0.0", "user2", "123", "journalctl -q --since {}".format(datetime.now().strftime("%H:%M:%S.%f")))
    checkout("echo 'journal: {}' >> stat.txt".format(stat), "")
