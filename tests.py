import unittest
from DZ1 import *

class TestFileSystemFunctions(unittest.TestCase):

    def test_char_to_int_add_permission(self):
        self.assertEqual(char_to_int("+rw", 000), 666)

    def test_char_to_int_remove_permission(self):
        self.assertEqual(char_to_int("-x", 777), 666)

    def test_char_to_int_set_permission(self):
        self.assertEqual(char_to_int("=r", 744), 444)

    def test_abs_path_absolute_resolution(self):
        self.assertEqual(abs_path("/home/user", "/documents/file.txt", "/home/user"), "/home/user/documents/file.txt")

    def test_abs_path_navigate_up(self):
        self.assertEqual(abs_path("/home/user/documents", "..", "/home/user"), "/home/user")

    def test_abs_path_current_directory(self):
        self.assertEqual(abs_path("/home/user", ".", "/home/user"), "/home/user")

class TestEmulator(unittest.TestCase):

    def setUp(self):
        self.emulator = Emulator("test_user", "test_machine", "C:\\Users\\furmi\\Downloads\\gg.tar")

    def test_ls(self):
        # Assuming the tar file contains "file1.txt" and "file2.txt"
        self.assertEqual(self.emulator.ls("ls"), "dir1\ntext1.txt\ntext2.txt\n")

    def test_ls_specific_file(self):
        self.assertEqual(self.emulator.ls("ls text1.txt"), "text1.txt\n")

    def test_ls_non_existent_directory(self):
        self.assertEqual(self.emulator.ls("ls non_existent_directory"), "ls: cannot access 'non_existent_directory': No such file or directory")

    def test_cd_change_directory(self):
        self.assertEqual(self.emulator.cd("cd dir1"), "gg/dir1")

    def test_cd_too_many_arguments(self):
        self.assertEqual(self.emulator.cd("cd documents extra_arg"),"-bash: cd: too many arguments")

    def test_cd_non_existent_directory(self):
        self.assertEqual(self.emulator.cd("cd non_existent_directory"), "-bash: cd: non_existent_directory: No such file or directory")

    def test_cat_display_file_contents(self):
        self.assertEqual(self.emulator.cat("cat text1.txt"), "a\r\nb\r\nc\n")

    def test_cat_non_existent_file(self):
        self.assertEqual(self.emulator.cat("cat non_existent.txt"), "cat: non_existent.txt: No such file or directory\n")

    def test_cat_multiple_files(self):
        self.assertEqual(self.emulator.cat("cat text1.txt text2.txt"), "a\r\nb\r\nc\nd\r\ne\r\nf\n")

    def test_chmod_change_mode_numeric(self):
        self.assertEqual(self.emulator.chmod("chmod 755 text1.txt"),"text1.txt's mode: 438 -> 755")

    def test_chmod_invalid_mode(self):
        self.assertEqual(self.emulator.chmod("chmod 855 text1.txt"), "chmod: invalid mode: '855'")

    def test_chmod_symbolic_mode(self):
        self.assertEqual(self.emulator.chmod("chmod u+x text1.txt"), "text1.txt's mode: 438 -> 538")

if __name__ == '__main__':
    unittest.main()
