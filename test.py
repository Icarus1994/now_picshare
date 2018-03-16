import unittest
from nowstagram import app

#通过manager中的函数跑该函数时，会找到以TesT开头的函数认为是测试用例去跑，
#并且跑之前会跑seTup,跑之后会跑TearDown
class nowstagramTest(unittest.TestCase):
    def setUp(self):
        print('setup')
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        print('tearDown')

# 测试注册，app.posT函数的功能与postman一样
    def register(self,username,password):
        #开启重定向,即当需要重定向时重定向
        return self.app.post('/reg/',data = {'username':username,'password':password},follow_redirects = True)

    def login(self,username,password):
        return self.app.post('/login/',data = {'username':username,'password':password},follow_redirects = True)

    def logout(self):
        return self.app.get('/logout/')

    def test_reg_logout_login(self):
        # 注册后的返回值是页面返回的response，200表示返回成功
        assert self.register('hello','world').status_code == 200
        assert "-hello" in str(self.app.open('/').data)
        self.logout()
        assert '-hello' not in str(self.app.open('/').data)
        assert self.login('hello','world')
        assert '-hello' in str(self.app.open('/').data)

    # 验证查看别人的profIle页面需要先登录
    def test_profile(self):
        #r = response
        r = self.app.open('/profile/3/',follow_redirects = True)
        assert r.status_code == 200
        assert 'password' in str(r.data)
        self.register('hello2','world')
        assert '-hello' in str(self.app.open('/profile/5/',follow_redirects = True).data)