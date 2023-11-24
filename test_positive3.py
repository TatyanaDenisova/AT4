import yaml
from checkers import ssh_checkout, getout

with open('config.yaml') as f:
    data = yaml.safe_load(f)


class TestPositive:

    def test_step1(self):
        # test1 create files to archive
        result1 = ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z a {}/arx2 -t{}".format(data["folder_in"], data["folder_out"], data["type"]),
                           "Everything is Ok")
        result2 = ssh_checkout("0.0.0.0", "user2", "123", "cd {}; ls".format(data["folder_out"]), "arx2.{}".format(data["type"]))
        assert result1 and result2, "test1 FAIL"

    def test_step2(self, make_files):
        # test2 output from archive
        result1 = ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z e arx2.{} -o{} -y".format(data["folder_out"], data["type"], data["folder_ext"]),
                           "Everything is Ok")
        result2 = ssh_checkout("0.0.0.0", "user2", "123", "cd {}; ls".format(data["folder_ext"]), make_files[0])
        assert result1 and result2, "test2 FAIL"

    def test_step3(self):
        # test3 full archive
        assert ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z t arx2.{}".format(data["folder_out"], data["type"]),
                        "Everything is Ok"), "test3 FAIL"

    def test_step4(self):
        # test4 renew archive
        assert ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z u {}/arx2.{}".format(data["folder_in"], data["folder_out"], data["type"]),
                        "Everything is Ok"), "test4 FAIL"

    def test_step5(self):
        # test5 del files from archive
        assert ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z d arx2.{}".format(data["folder_out"], data["type"]),
                        "Everything is Ok"), "test5 FAIL"

    def test_step6(self):
        # test6 show archive content
        assert ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z l arx2.{}".format(data["folder_out"], data["type"]), "Listing archive"), "test6 FAIL"

    def test_step7(self, make_files, make_subfolder):
        # test7 unpacing subfolder
        res = []
        res.append(ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z a {}/arx -t{}".format(data["folder_in"], data["folder_out"], data["type"]),
                            "Everything is Ok"))
        res.append(ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z x arx.{} -o{} -y".format(data["folder_out"], data["type"], data["folder_ext2"]),
                            "Everything is Ok"))
        for i in make_files:
            res.append(ssh_checkout("0.0.0.0", "user2", "123", "ls {}".format(data["folder_ext2"]), i))
        res.append(ssh_checkout("0.0.0.0", "user2", "123", "ls {}".format(data["folder_ext2"]), make_subfolder[0]))
        res.append(ssh_checkout("0.0.0.0", "user2", "123", "ls {}/{}".format(data["folder_ext2"], make_subfolder[0]), make_subfolder[1]))
        assert all(res), "test7 FAIL"
    def test_step8(self, clear_folders, make_files):
        # test8
        res = []
        for i in make_files:
            res.append(ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z h {}".format(data["folder_in"], i), "Everything is Ok"))
            hash = getout("cd {}; crc32 {}".format(data["folder_in"], i)).upper()
            res.append(ssh_checkout("0.0.0.0", "user2", "123", "cd {}; 7z h {}".format(data["folder_in"], i), hash))
        assert all(res), "test8 FAIL"