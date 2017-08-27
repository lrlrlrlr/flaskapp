'''
1.test_password_setter:给密码赋值，能正常生成哈希密码。
2.test_no_password_getter:原文密码不能直接被读取，防止泄漏。
3.test_password_verification：验证密码功能。
4.test_password_salt_are_random:确保盐是随机的，即使相同的密码，生成的哈希密码也不相同。
'''

import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)#其实这里不写is not None也是可以的吧？
        pass

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            print(u.password)
        pass

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
        pass

    def test_password_salt_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)
        pass
