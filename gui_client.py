"""
GUI界面对象
"""
from common.iterableTool import IterableTool
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5 import QtCore, QtWidgets, QtGui
from login_window import *
from python_dict import *
from register_page import *
import time, json, platform


class PythonDict(QMainWindow):
    """
    主界面
    """
    isLogin = False
    isRemMec = False

    def __init__(self, control, login_page, register_page):
        """
        param: control -->[class]

        主界面元素参数信息：
        笔记页区
        self.tabWidget = 笔记-笔记tabWidget控件[QTabWidget] 内含两个tab 分别是：
            self.tab_note 笔记-笔记tab[QWidget] index = 1
            self.tab_dict 笔记-字典tab[QWidget] index = 0
        self.note_edit = 笔记-笔记编辑区[QTextEdit对象]
        self.checkBoxNote = 笔记-编辑复选框[QCheckBox对象]
        self.note_profile = 笔记-显示笔记详细信息（如：创建时间）[QLabel对象]
        self.notes_list = 笔记-所有个人笔记列表显示区[QListWidget对象]
        字典页区
        self.search = 搜索按钮[QPushButton对象]
        self.search_bar = 搜索栏[QLineEdit对象]
        self.search_result_list = 搜索的结果列表[QListWidget对象]
        self.result_browser = 搜索的单个结果详细显示[QTextBrowser对象]
        """
        QMainWindow.__init__(self)
        # 传入的三个对象Control,LoginWindow,RegisterWindow
        self.control = control
        self.loginPage = login_page
        self.registerPage = register_page
        # 创建主窗口
        self.main_ui = Ui_MainWindow(self.loginPage, self.registerPage)
        self.initUI()
        self.main_ui.setupUi(self)
        # 字典查询结果
        self.dict_re_data = {}

    def initUI(self):
        """
            设置UI界面
        """
        # 设置窗口 Icon
        self.setWindowIcon(QtGui.QIcon('./img/Quantum light logo bold.png'))

    def search(self):
        """ 搜索按钮 点击 后执行此方法 """

        data = {'protocol': 'QUEDICT', 'word': self.main_ui.search_bar.text()}
        print(data)
        # 向control传信号 return---> data
        msg = self.control.signal_in('QUEDICT', data)
        print('last:', msg)
        if msg['protocol'] == 'QUEOK':
            self.show_query_result(msg)
        else:
            self.show_failed()

    def show_query_result(self, data):
        """
            根据参数data进行协议判定 最终在界面显示数据
            data: [dict]
        """
        # 删除字典中的协议
        del data['protocol']
        self.dict_re_data = data
        # 把单词查询结果 在界面列表显示出来
        # 清屏 --> search_result_list
        self.main_ui.search_result_list.clear()
        for value in data.values():
            # search_result_list添加条目
            self.main_ui.search_result_list.addItem(value['word'])
            # 判定 search_bar 中的搜索词 是否一样
            if value['word'] == self.main_ui.search_bar.text():
                # 清屏--> result_browser
                self.main_ui.result_browser.clear()
                self.dict_result_display_logic(value)

    def list_re_clicked(self):
        """
        当字典界面的 <search_result_list 搜索的结果列表> 中的条目被点击时 执行此函数
        :return: none
        """
        # 获取点击条目的单词 target_obj -->[string]
        target_obj = self.main_ui.search_result_list.currentItem().text()
        print(target_obj)
        # 清空字典界面中 <self.result_browser 搜索的单个结果详细显示>
        self.main_ui.result_browser.clear()
        print('screen clear')
        for key, value in self.dict_re_data.items():
            if value['word'] == target_obj:
                print(value)
                self.dict_result_display_logic(value)

    def show_failed(self):
        """
            当查询失败时 在界面提示
        """
        self.main_ui.result_browser.append('无查询结果')

    def dict_result_display_logic(self, item):
        """
            <self.result_browser 搜索的单个结果详细显示>显示逻辑
        :param item: 单词 -->{'id': '', 'word': '', 'mean': '', 'eg': ''}
        :return: none
        """
        for key, value in item.items():
            if value == '':
                continue
            if key == 'id' or key == 'word':
                continue
            elif key == 'mean':
                result = '中文释义: ' + value
                self.main_ui.result_browser.append(result)
            elif key == 'eg':
                result = '例子: ' + value
                self.main_ui.result_browser.append(result)
            elif key == 'eg_mean':
                result = '解释: ' + value
                self.main_ui.result_browser.append(result)

    # ------------------------------------------------------------------------------
    # Note 部分代码
    # ------------------------------------------------------------------------------
    def tabChange(self):
        """ 当主界面的两个页面的标签变换时 执行此方法"""
        # 先判定登录状态，如果已登录，则pass
        if PythonDict.isLogin == False and self.main_ui.tabWidget.currentWidget() == self.main_ui.tab_dict:
            # TODO: 显示登陆窗口，并提示“该功能需要登陆”
            self.loginPage.login_page.login_status_bar.setText('使用笔记功能需要登陆')
            self.loginPage.show()

    def queryNote(self, username):
        """当用户登录成功时 自动执行此方法"""
        # 创建笔记查询data
        data = {'protocol': 'QNT', 'name': username}
        # 当登录成功时，查询用户笔记
        msg = self.control.signal_in('QNT', data)
        # 将服务器返回的用户笔记显示出来
        self.showNotes(msg)

    def showNotes(self, msg):
        """笔记界面 显示服务器返回的用户笔记数据"""
        # 当登录成功时， 查询用户笔记
        self.qList = [] # 存放self.notes_list 中显示的内容
        self.notes_re = msg # 将msg赋值给实例变量 方便后续其它类实例使用

        if msg['protocol'] == 'QNTOK':
            del msg['protocol']
            print('notes_re', self.notes_re)
            for value in msg.values():
                note_list_item = value['title'] + '  ' + value['cre_date'] + ''
                self.qList.append(note_list_item)
            IterableTool.list_order(self.qList, self.list_order_condition)
            self.main_ui.notes_list.addItems(self.qList)
            print(self.qList)

    def notes_list_item_clicked(self):
        """笔记界面 笔记列表中的item被点击时 执行该方法"""
        target_obj = self.main_ui.notes_list.currentItem().text()
        print(target_obj[0:-12])
        for value in self.notes_re.values():
            if value['title'] == target_obj[0:-12]:
                self.main_ui.note_edit.setText(value['nt'])

    def noteCheckBoxChange(self):
        """笔记界面 编辑选框状态发生改变时 执行该方法"""
        # 选中 编辑
        if self.main_ui.checkBoxNote.isChecked():
            self.main_ui.checkBoxNote.setText('保存')
            self.main_ui.checkBoxNote.setIcon(QtGui.QIcon('./img/unlock.png'))
        # 取消选中 保存
        elif not self.main_ui.checkBoxNote.isChecked():
            self.main_ui.checkBoxNote.setText('编辑')
            self.main_ui.checkBoxNote.setIcon(QtGui.QIcon('./img/lock.png'))
            if self.main_ui.note_title in self.notes_list():
                # 提示笔记标题不能重复
                pass

    def newNote(self):
        """笔记界面的新建按钮点击时 执行该方法"""
        # 检测是否有正在编辑的内容
        if self.main_ui.checkBoxNote.isChecked():
            # 提示 先保存当前编辑的内容
            print('先保存当前编辑的内容')
        elif not self.main_ui.checkBoxNote.isChecked():
            # 新建笔记 清空目前的编辑框内内容
            self.num = 1 # 计数
            for tmp in self.notes_list():
                if tmp[0:4] == '新建笔记':
                    self.num += 1
            title = '新建笔记' + str(self.num)
            self.main_ui.note_title.setText(title)
            self.main_ui.note_edit.clear()
            self.main_ui.note_title.setDisabled(False)
            self.main_ui.note_edit.setDisabled(False)
            self.main_ui.checkBoxNote.setChecked(True)

    def notes_list(self):
        """
            获取笔记列表所有笔记标题
            :return --> [list]
        """
        self.tlist = [] # 存放笔记列表所有笔记标题
        count = self.main_ui.notes_list.count()
        for i in range(count):
            self.tlist.append(self.main_ui.notes_list.item(i).text()[0:-12])
        return self.tlist
    # def list_pop_menu(self):
    #     self.popMenu = QtWidgets.QMenu(self.main_ui.search_result_list)
    #     self.item_del = QtWidgets.QAction(QtGui.QIcon('./img/del.jpg'), '删除', self)
    #     self.popMenu.addAction(self.item_del)
    #     # popMenu出现在窗口的位置
    #     self.popMenu.exec_(QtGui.QCursor.pos())
    #     if self.item_del.isEnabled():
    #         self.del_item()
    #
    # def del_item(self):
    #     print('yes')

    # self.search_result_list.setContextMenuPolicy(3)
    # self.search_result_list.customContextMenuRequested[QtCore.QPoint].connect(MainWindow.list_pop_menu)

    # ------------------------------------------------------------------------------
    # 注册部分
    # ------------------------------------------------------------------------------
    def register(self):
        data = self.registerPage.register()
        if data['protocol'] == 'REGOK':
            print('mainpage', data)
            # 账户信息填入登录界面对应位置
            self.loginPage.login_page.username.setText(data['username'])
            self.loginPage.login_page.password.setText(data['pwd'])
            self.loginPage.login_page.login_status_bar.setText('注册成功')
            # 打开登录界面
            self.loginPage.show()
            # 关闭注册界面
            self.registerPage.close()

    # ------------------------------------------------------------------------------
    # 登录部分
    # ------------------------------------------------------------------------------

    def login(self):
        data = self.loginPage.login()
        if PythonDict.isLogin:
            title = 'Python Dictionary - ' + data['name']
            self.setWindowTitle(title)
            self.main_ui.tab_note.setDisabled(False)
            self.queryNote(data['name'])

    def autologin(self):
        try:
            # 打开储存的本地账户文件
            f = self.control.signal_in('OPENF', 'r')
            # 将字符串格式的字典 转换回字典
            data = json.loads(f.read())
        except Exception:
            pass
        else:
            if type(data) is dict:
                data = self.loginPage.autoLogin(data)
            self.autologin_2(data)

    def autologin_2(self, data):
        if PythonDict.isLogin:
            title = 'Python Dictionary - ' + data['name']
            self.setWindowTitle(title)
            self.main_ui.tab_note.setDisabled(False)
            self.queryNote(data['name'])



    @staticmethod
    def list_order_condition(i1, i2):
        """
            用来作为list_order 的func_condition参数
            定义了list_order对参数iterable进行排序的条件
        :param i1: 参数意义还请参考 list_order 源码
        :param i2: 参数意义还请参考 list_order 源码
        :return: bool
        """
        return time.mktime(time.strptime(i1[-10:], '%Y-%m-%d')) < time.mktime(time.strptime(i2[-10:], '%Y-%m-%d'))


class LoginWindow(QWidget):
    """
        登入界面
    元素:
    self.username = 用户名 [QLineEdit]
    self.password = 密码  [QLineEdit]
    self.login = 登录按钮   [QPushButton]
    self.cancel_login = 取消登录按钮  [QPushButton]
    self.remember_me_check = 记住用户 [QCheckBox]
    self.login_status_bar = 登录提示信息  [QLabel]
    """

    def __init__(self, control):
        QWidget.__init__(self)
        self.login_page = Ui_login_page()
        self.login_page.setupUi(self)
        self.control = control

    def autoLogin(self, data):
        result = self.control.signal_in('LOG', data)
        if result['protocol'] == 'LOGOK':
            self.show_status('LOGOK')
            PythonDict.isLogin = True
            return data
        elif result['protocol'] == 'LOGUNE':
            # 无此用户名
            self.show()
            self.show_status('autoLOGUNE')
        elif result['protocol'] == 'LOGWP':
            # 密码错误
            self.show()
            self.show_status('autoLOGWP')

    def login(self):
        """
            登录界面的确认按钮 点击后 执行该方法
        :return:
        """
        # remember_me_check
        data = {'protocol': 'LOG',
                'name': self.login_page.username.text(),
                'pwd': self.login_page.password.text()}
        # 向control传信号 return---> data
        result = self.control.signal_in('LOG', data)
        # 对data['protocol']判断
        if result['protocol'] == 'LOGOK':
            if self.login_page.remember_me_check.isChecked():
                f = self.control.signal_in('OPENF', 'w')
                content = json.dumps(data)
                f.write(content)
            elif not self.login_page.remember_me_check.isChecked():
                f = self.control.signal_in('OPENF', 'w')
                f.write('')

            self.show_status('LOGOK')
            PythonDict.isLogin = True
            return data
        elif result['protocol'] == 'LOGUNE':
            # 无此用户名
            self.show_status('LOGUNE')
        elif result['protocol'] == 'LOGWP':
            # 密码错误
            self.show_status('LOGWP')

    def show_status(self, data):
        """
            根据data内容，在客户端显示相应的信息
        :param data: string
        :return: none
        """
        if data == 'LOGOK':
            self.login_page.login_status_bar.setText('登录成功')
            # TODO: 登录- 解锁笔记功能 显示已登录状态
            print('登录成功')
            self.close()
        elif data == 'LOGUNE':
            self.login_page.login_status_bar.setText('用户名不存在')
        elif data == 'autoLOGUNE' or data == 'autoLOGWP':
            self.login_page.login_status_bar.setText('自动登录失败')
        elif data == 'LOGWP':
            self.login_page.login_status_bar.setText('用户名或密码错误')


class RegisterWindow(QWidget):
    """
    注册界面
    """

    def __init__(self, control):
        QWidget.__init__(self)
        self.register_page = Ui_Form()
        self.register_page.setupUi(self)
        self.control = control

    def register(self):
        # 检测两次输入密码是否相同
        if self.register_page.pwd1.text() == self.register_page.pwd2.text():
            data = {'protocol': 'REG',
                    'username': self.register_page.username_register.text(),
                    'pwd': self.register_page.pwd1.text()}
            # 发送账户到服务端验证
            response = self.control.signal_in('REG', data)
            # 如果验证通过
            if response['protocol'] == 'REGOK':
                data['protocol'] = 'REGOK'
                return data
            # 或是用户名不可用
            elif response['protocol'] == 'REGUU':
                self.register_page.hint_label.setText('用户名已存在')
                return response
        # 如果两次密码不同
        else:
            # 提示两次密码不一样
            self.register_page.hint_label.setText('两次的密码不一样')
            return {'protocol': 'REGUSP'}
