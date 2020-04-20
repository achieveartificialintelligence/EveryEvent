# -*- coding: utf-8 -*-

import sys, peewee, re
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

# 数据库连接
db = peewee.MySQLDatabase(
    host="数据库地址",
    port=3306,
    database="数据库名",
    user="用户名",
    password="密码"
)

# 表设计
class MeiTian(peewee.Model):
    Name = peewee.CharField(default=0)
    Comment = peewee.CharField(default=0)
    Num = peewee.CharField(default=0)
    class Meta:
        database = db

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(833, 476)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.calendarWidget = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendarWidget.setGeometry(QtCore.QRect(450, 10, 371, 291))
        self.calendarWidget.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendarWidget.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendarWidget.setObjectName("calendarWidget")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 431, 441))
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setObjectName("listWidget")
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setGeometry(QtCore.QRect(720, 330, 101, 41))
        self.spinBox.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.spinBox.setMinimum(-100)
        self.spinBox.setMaximum(2000)
        self.spinBox.setObjectName("spinBox")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(450, 330, 251, 41))
        font = QtGui.QFont()
        font.setFamily("新宋体")
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.pushButtonYes = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonYes.setGeometry(QtCore.QRect(450, 390, 61, 41))
        self.pushButtonYes.setObjectName("pushButtonYes")
        self.pushButtonNo = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonNo.setGeometry(QtCore.QRect(530, 390, 61, 41))
        self.pushButtonNo.setObjectName("pushButtonNo")
        self.pushButtonDraw = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonDraw.setGeometry(QtCore.QRect(690, 390, 61, 41))
        self.pushButtonDraw.setObjectName("pushButtonDraw")
        self.pushButtonFresh = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonFresh.setGeometry(QtCore.QRect(620, 390, 61, 41))
        self.pushButtonFresh.setObjectName("pushButtonFresh")
        self.pushButtonMax = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonMax.setGeometry(QtCore.QRect(760, 390, 61, 41))
        self.pushButtonMax.setObjectName("pushButtonMax")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.lineEdit, self.spinBox)
        MainWindow.setTabOrder(self.spinBox, self.pushButtonYes)
        MainWindow.setTabOrder(self.pushButtonYes, self.pushButtonNo)
        MainWindow.setTabOrder(self.pushButtonNo, self.pushButtonDraw)
        MainWindow.setTabOrder(self.pushButtonDraw,self.pushButtonFresh)
        MainWindow.setTabOrder(self.pushButtonFresh,self.pushButtonMax)
        MainWindow.setTabOrder(self.pushButtonMax, self.calendarWidget)
        MainWindow.setTabOrder(self.calendarWidget, self.listWidget)

        self.calClick() # 启动时自动显示

        self.pushButtonYes.clicked.connect(self.YesClick) # 确认按键
        self.pushButtonNo.clicked.connect(self.NoClick) # 删除按键
        self.pushButtonDraw.clicked.connect(self.draw) # 画图
        self.pushButtonFresh.clicked.connect(self.fresh) # 刷新
        self.calendarWidget.selectionChanged.connect(self.calClick) # 日历日期切换
        self.listWidget.clicked.connect(self.singleClick) # 事项单击
        self.listWidget.doubleClicked.connect(self.doubleClick) # 事项双击
        self.pushButtonMax.clicked.connect(self.assist) #辅助

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "考研计划"))
        self.pushButtonYes.setText(_translate("MainWindow", "新增"))
        self.pushButtonNo.setText(_translate("MainWindow", "删除"))
        self.pushButtonDraw.setText(_translate("MainWindow", "画图"))
        self.pushButtonFresh.setText(_translate("MainWindow", "刷新"))
        self.pushButtonMax.setText(_translate("MainWindow", "辅助"))

    # QDate转string
    def StrDate(self,date):
        DD = str(date.year())
        if date.month() < 10:
            DD += '0'
        DD += str(date.month())
        if date.day() < 10:
            DD += '0'
        DD += str(date.day())
        return DD

    # 查询函数
    def Query(self):
        if db.is_closed():
            db.connect()
        self.listWidget.clear()

        boldFont = QtGui.QFont()
        boldFont.setBold(True)

        index = 0 # 颜色事项计数
        # 设置标题
        self.listWidget.addItem("进展\t今日\t项目(剩余%)")
        self.listWidget.item(index).setBackground(QtGui.QColor(187,187,187,255))
        self.listWidget.item(index).setFont(boldFont)

        #获取此日所有节点
        res = MeiTian.select().order_by(MeiTian.Name).where(
            MeiTian.Comment==self.StrDate(self.calendarWidget.selectedDate())
        ).execute()

        #此日单个节点
        for i in res:

            #计算此事件总和值
            iSum = 0
            for n in MeiTian.select(MeiTian.Num).where(
                (MeiTian.Name==i.Name)
                &(MeiTian.Comment!="MAXNUM")
            ).execute():
                iSum += int(n.Num)

            #计算此事件最大值
            iMax = int(MeiTian.get(
                (MeiTian.Name==i.Name)
                &(MeiTian.Comment=="MAXNUM")
            ).Num)
            
            # 显示事项
            if i.Name == self.lineEdit.text() :# 最后的变化行
                self.listWidget.addItem(str(iSum)+"\t"+i.Num+"\t"+i.Name+"("+str(iMax)+")")
                index += 1
                self.listWidget.item(index).setFont(boldFont)
                self.listWidget.item(index).setForeground(QtGui.QColor(0,148,148,255))
            else:
                self.listWidget.addItem(str(iSum)+"\t"+i.Num+"\t"+i.Name+"("+str((iMax-iSum)*100//iMax)+"%)")
                index += 1
            
            # 设置事项颜色
            # 根据当日数量改变，由红到绿
            if int(i.Num)<=10:
                self.listWidget.item(index).setBackground(QtGui.QColor(255,148,148,255-int(i.Num)*20))
            elif int(i.Num)<=20:
                self.listWidget.item(index).setBackground(QtGui.QColor(154,247,183,(int(i.Num)-10)*25))
            else:
                self.listWidget.item(index).setBackground(QtGui.QColor(154,247,183,255))

        if not db.is_closed():
            db.close()

    # 日历切换
    def calClick(self):
        if db.is_closed():
            db.connect()
        date = self.calendarWidget.selectedDate()

        # 显示所有事项，不存在的就创建
        AllEveRes = MeiTian.select().where(MeiTian.Comment=="MAXNUM").execute()
        for i in AllEveRes:
            MeiTian.get_or_create(Name=i.Name,Comment=self.StrDate(date))

        self.Query()

    def assist(self):
        if db.is_closed():
            db.connect()
        # 清除为0的事项
        self.statusbar.showMessage("【提示】正在删除无用日程")
        xRange = MeiTian.delete().where(
            (MeiTian.Num==0)
            &(MeiTian.Comment!=self.StrDate(QtCore.QDate.currentDate()))
        ).execute()
        self.statusbar.showMessage("【提示】删除无用日程完成")
        self.calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
        self.Query()

    # 刷新
    def fresh(self):
        self.calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
        self.lineEdit.setText("")
        self.spinBox.setValue(0)

    # 画图
    def draw(self):
        if db.is_closed():
            db.connect()
        xPos = []
        yPos = []
        if self.lineEdit.text() == "" : #为空，画出日线图
            xRange = MeiTian.select(MeiTian.Comment,MeiTian.Num).order_by(MeiTian.Comment).where(
                (MeiTian.Comment!="MAXNUM")
            ).execute()
            xDict = {}
            for x in xRange:
                if x.Comment[4:] in xDict:
                    xDict[x.Comment[4:]] += int(x.Num)
                else:
                    xDict[x.Comment[4:]] = int(x.Num)

            xPos=list(xDict.keys())
            yPos=list(xDict.values())
        else: #不为空，画出事件图
            xRange = MeiTian.select(MeiTian.Comment,MeiTian.Num).order_by(MeiTian.Comment).where(
                (MeiTian.Comment!="MAXNUM")
                &(MeiTian.Name==self.lineEdit.text())    
            ).execute()
            for x in xRange:
                xPos.append(x.Comment[4:])
                yPos.append(int(x.Num))

        plt.plot(xPos, yPos,'--')
        plt.scatter(xPos,yPos)
        plt.xticks(rotation=70)
        plt.title("Trends")
        plt.show()

        if not db.is_closed():
            db.close()
        
    # 事项单击
    def singleClick(self, index):
        s = self.listWidget.itemFromIndex(index).text().split("\t")
        if s[1]!="今日": # 去除首行，设置数据
            self.lineEdit.setText(re.sub("\(.*\)","",s[-1]))
            self.spinBox.setValue(int(s[0]))
            self.statusbar.showMessage("正在学习："+s[-1],0)
        else: # 刷新今日
            self.fresh()

    # 事项双击
    def doubleClick(self, index):
        if db.is_closed():
            db.connect()
        s = self.listWidget.itemFromIndex(index).text().split("\t")

        if s[1]!="今日": # 去除首行，更新数据
            nn = int(s[1])
            MeiTian.update({MeiTian.Num:nn+1}).where(
                (MeiTian.Name==self.lineEdit.text()) 
                & (MeiTian.Comment==self.StrDate(self.calendarWidget.selectedDate()))
            ).execute()

        self.Query()

    # 删除按键
    def NoClick(self):
        if db.is_closed():
            db.connect()
        if self.lineEdit.text() == "" : #检查输入框是否为空
            # 清除为0的事项
            self.statusbar.showMessage("【提示】正在删除无用日程")
            xRange = MeiTian.delete().where(
                (MeiTian.Num==0)
                &(MeiTian.Comment!=self.StrDate(QtCore.QDate.currentDate()))
            ).execute()
            self.statusbar.showMessage("【提示】删除无用日程完成")
        elif self.lineEdit.text() == "MeiTian" : #删表
            if QMessageBox().question(QMessageBox(), '注意', '确认删除表？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)==16384:
                MeiTian.drop_table()
                MeiTian.create_table()
        else: #删除项目
            #确认框
            if QMessageBox().question(QMessageBox(), '注意', '确认删除该项？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)==16384:
                MeiTian.delete().where(MeiTian.Name==self.lineEdit.text()).execute()

        self.Query()

    # 新增按键
    def YesClick(self):
        if db.is_closed():
            db.connect()
        if self.lineEdit.text() == "" : #检查输入框是否为空
            self.statusbar.showMessage("【警告】输入框为空",0)

        else: #检查是否 不存在事件
            if MeiTian.get_or_create(Name=self.lineEdit.text(),Comment="MAXNUM")[1]: #不存在返回true
                # 创建事项
                nValue = int(self.spinBox.text())
                if nValue<=0: #防止 MAXNUM 过小
                    nValue = 1
                MeiTian.update({MeiTian.Num:nValue}).where((MeiTian.Name==self.lineEdit.text()) & (MeiTian.Comment=="MAXNUM")).execute()
                
                # 创建节点
                MeiTian.insert(
                    Name=self.lineEdit.text(),
                    Comment=self.StrDate(self.calendarWidget.selectedDate())
                ).execute()
                self.spinBox.setValue(0)
            else: # 存在事项，直接修改节点值
                  # 因为节点在切换日历和新建事项时都被创建，所以一定存在节点，不必再检查

                # 查询今日的节点值
                iSum = 0
                for n in MeiTian.select().where(
                    (MeiTian.Name==self.lineEdit.text())
                    &(MeiTian.Comment!="MAXNUM")
                    &(MeiTian.Comment!=self.StrDate(self.calendarWidget.selectedDate())) #排除今日
                ).execute():
                    iSum += int(n.Num)
                st = int(self.spinBox.text())-iSum

                # 更新今日数据
                MeiTian.update({MeiTian.Num:st}).where(
                    (MeiTian.Name==self.lineEdit.text())
                    & (MeiTian.Comment==self.StrDate(self.calendarWidget.selectedDate()))
                ).execute()

        self.Query()


if __name__ == "__main__":
    if not MeiTian.table_exists():
        MeiTian.create_table()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
