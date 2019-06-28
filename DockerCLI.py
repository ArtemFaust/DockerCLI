from PyQt5 import QtGui, QtWidgets, QtCore, uic
import sys, os, psutil
import os.path
from time import gmtime, strftime
import qdarkstyle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.style as style

from scapy.all import *
def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)
print(get_script_dir())
os.chdir(get_script_dir())

CPU_PERSENT_FOR_DOCKER_USAGE = []
MEM_PERSENT_FOR_DOCKER_USAGE = []
tableCollumn = []
logTextEdit = None
green_color = QtGui.QColor(50, 205, 50)
white_color = QtGui.QColor(255, 255, 255)
red_color = QtGui.QColor(249, 14, 14)
yelow_color = QtGui.QColor(196, 184, 69)
blue_color = QtGui.QColor(66, 224, 245)
selectedRunningConteiner = ''
item_selected = None
selected_row = None
selected_Column = None
selectedStartConteiner = None
startConteinerRow= None
startConteinerColumn = None
paused = []
style.use('dark_background')
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global logTextEdit
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('DockerCLI.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.psutilThread = PsuTilThread()
        self.psutilThread.emiter.connect(self.updateGraph)
        self.pushButton_4.setIcon(QtGui.QIcon('resurse/Stage_Script_icon.png'))
        self.pushButton.setIcon(QtGui.QIcon('resurse/Start-icon.png'))
        self.pushButton_2.setIcon(QtGui.QIcon('resurse/Stop-red-icon.png'))
        self.pushButton_6.setIcon(QtGui.QIcon('resurse/pause.png'))
        self.pushButton_7.setIcon(QtGui.QIcon('resurse/play-pause-icon-png-12.png'))
        self.pushButton_3.setIcon(QtGui.QIcon('resurse/save.ico'))
        self.pushButton_5.setIcon(QtGui.QIcon('resurse/delete.png'))
        self.toolButton.setIcon(QtGui.QIcon('resurse/rescan.png'))
        logTextEdit = self.textEdit
        self.getAllConteiners()
        self.runScriptWindow = RunScripConfWindow(table=self.tableWidget)
        self.runScriptWindow.setParent(self, QtCore.Qt.Sheet)
        self.pushButton_4.clicked.connect(lambda: self.runScriptWindow.show())
        self.timer = QtCore.QTimer()
        self.timer.start(3000)
        self.timerForThreadPsutil = QtCore.QTimer()
        self.timerForThreadPsutil.start(1000)
        self.timer.timeout.connect(self.updateStatusRunImage)
        self.timerForThreadPsutil.timeout.connect(lambda: self.psutilThread.start())
        self.tableWidget_2.cellClicked.connect(self.set_selectedRunningConteiner)
        self.pushButton_2.clicked.connect(self.stopRunningImage)
        self.pushButton.clicked.connect(self.startConteiner)
        self.tableWidget.cellClicked.connect(self.setselectedStartConteiner)
        self.pushButton_6.clicked.connect(self.pauseImage)
        self.pushButton_7.clicked.connect(self.unpauseImage)
        self.pushButton_3.clicked.connect(self.commitImage)
        self.toolButton.clicked.connect(self.reloadAllConteiner)
        self.pushButton_5.clicked.connect(self.deleteConteiner)
        # CPU USAGE
        self.figure_graph1 = plt.figure()
        self.figure_graph1.patch.set_alpha(0.)
        self.figure_graph1_canvas = FigureCanvas(self.figure_graph1)
        self.figure_graph1_ax = self.figure_graph1.add_subplot(111)
        self.figure_graph1_ax.grid(linestyle='-.', color='grey')
        self.figure_graph1_ax.set_title("CPU USAGE %")
        self.verticalLayout_8.addWidget(self.figure_graph1_canvas)
        # MEM USAGE
        self.figure_graph2 = plt.figure()
        self.figure_graph2.patch.set_alpha(0.)
        self.figure_graph2_canvas = FigureCanvas(self.figure_graph2)
        self.figure_graph2_ax = self.figure_graph2.add_subplot(111)
        self.figure_graph2_ax.grid(linestyle='-.', color='grey')
        self.figure_graph2_ax.set_title("MEM USAGE %")
        self.verticalLayout_8.addWidget(self.figure_graph2_canvas)


    def updateGraph(self):
        print(CPU_PERSENT_FOR_DOCKER_USAGE)
        print(MEM_PERSENT_FOR_DOCKER_USAGE)
        self.figure_graph1_ax.cla()
        self.figure_graph1_ax.grid(linestyle='-.', color='grey')
        self.figure_graph1_ax.axis((0, 60, 0, 100))
        if len(CPU_PERSENT_FOR_DOCKER_USAGE) >= 60:
            self.figure_graph1_ax.plot(CPU_PERSENT_FOR_DOCKER_USAGE[-60:], color='green', label='Current')
        else:
            self.figure_graph1_ax.plot(CPU_PERSENT_FOR_DOCKER_USAGE, color='green', label='Current')
        self.figure_graph1_ax.set_title("CPU USAGE %")
        self.figure_graph1_canvas.draw()

        self.figure_graph2_ax.cla()
        self.figure_graph2_ax.grid(linestyle='-.', color='grey')
        self.figure_graph2_ax.axis((0, 60, 0, 110))
        if len(MEM_PERSENT_FOR_DOCKER_USAGE) >= 60:
            self.figure_graph2_ax.plot(MEM_PERSENT_FOR_DOCKER_USAGE[-60:], color='green', label='Current')
        else:
            self.figure_graph2_ax.plot(MEM_PERSENT_FOR_DOCKER_USAGE, color='green', label='Current')
        self.figure_graph2_ax.set_title("MEM USAGE %")
        self.figure_graph2_canvas.draw()




    def deleteConteiner(self):
        message = QtWidgets.QMessageBox.information(self,'Delete Conteiner %s' % selectedStartConteiner,
                                                    'Are your sure delete %s' % selectedStartConteiner + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if message == QtWidgets.QMessageBox.Yes:
            rezult = os.popen('docker rmi %s' % selectedStartConteiner).read()
            logTextEdit.setTextColor(white_color)
            logTextEdit.append(
                strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": delete conteiner %s" % selectedStartConteiner + "\n" +
                str(rezult))
            logTextEdit.setTextColor(blue_color)
            logTextEdit.append('OK')
            logTextEdit.setTextColor(white_color)
        else:
            pass


    def reloadAllConteiner(self):
        for i in reversed(range(self.tableWidget.rowCount())):
            self.tableWidget.removeRow(i)
        for i in reversed(range(self.tableWidget.columnCount())):
            self.tableWidget.removeColumn(i)
        self.getAllConteiners()
        if selectedStartConteiner != '' and selectedRunningConteiner not in paused:
            items = self.tableWidget.findItems(selectedStartConteiner, QtCore.Qt.MatchExactly)
            for i in items:
                i.setBackground(green_color)
        elif selectedRunningConteiner in paused:
            items = self.tableWidget.findItems(selectedStartConteiner, QtCore.Qt.MatchExactly)
            for i in items:
                i.setBackground(blue_color)

    def commitImage(self):
        global item_selected
        if selected_Column == 0:
            item = self.tableWidget_2.item(selected_row, selected_Column)
        item.setBackground(red_color)
        item = self.tableWidget_2.item(selected_row, selected_Column + 1)
        image_commit_name = item.text()
        rezult = os.popen('docker commit ' + selectedRunningConteiner + " " + image_commit_name)
        print(rezult)
        logTextEdit.setTextColor(white_color)
        logTextEdit.append(
            strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": save image %s" + selectedRunningConteiner + " " + image_commit_name + "\n" +
            str(rezult))
        logTextEdit.setTextColor(green_color)
        logTextEdit.append('OK')
        logTextEdit.setTextColor(white_color)


    def unpauseImage(self):
        global item_selected, paused
        if selected_Column == 0:
            item = self.tableWidget_2.item(selected_row, selected_Column)
            item.setBackground(red_color)
            rezult = os.popen('docker unpause %s' % selectedRunningConteiner)
            logTextEdit.setTextColor(white_color)
            logTextEdit.append(
                strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": unpaused image %s" % selectedRunningConteiner + "\n" +
                str(rezult))
            logTextEdit.setTextColor(green_color)
            logTextEdit.append('OK')
            logTextEdit.setTextColor(white_color)
            item = self.tableWidget_2.item(selected_row, selected_Column + 1)
            image_stop_name = item.text()
            items = self.tableWidget.findItems(image_stop_name, QtCore.Qt.MatchExactly)
            for i in items:
                i.setBackground(green_color)
            if paused != []:
                paused.remove(selectedRunningConteiner)

    def pauseImage(self):
        global paused
        global item_selected
        if selected_Column == 0:
            item = self.tableWidget_2.item(selected_row, selected_Column)
            item.setBackground(red_color)
            rezult = os.popen('docker pause %s' % selectedRunningConteiner)
            logTextEdit.setTextColor(white_color)
            logTextEdit.append(
                strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": paused image %s" % selectedRunningConteiner + "\n" +
                str(rezult))
            logTextEdit.setTextColor(blue_color)
            logTextEdit.append('OK')
            logTextEdit.setTextColor(white_color)
            item = self.tableWidget_2.item(selected_row, selected_Column + 1)
            image_stop_name = item.text()
            items = self.tableWidget.findItems(image_stop_name, QtCore.Qt.MatchExactly)
            for i in items:
                i.setBackground(blue_color)
            if selectedRunningConteiner not in paused:
                    paused.append(selectedRunningConteiner)


    def setselectedStartConteiner(self,row, column):
        global selectedStartConteiner, startConteinerColumn, startConteinerRow
        if column == 0:
            item_selected = self.tableWidget.item(row, column)
            try:
                selectedStartConteiner = item_selected.text()
                startConteinerColumn = column
                startConteinerRow = row
            except:
                pass

    def startConteiner(self):
        rezult = os.popen('bash ./run_scripts/%s' % selectedStartConteiner).read()
        if rezult != '':
            logTextEdit.setTextColor(white_color)
            logTextEdit.append(
                strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": Conteiner %s running!" % selectedRunningConteiner)
            logTextEdit.setTextColor(green_color)
            logTextEdit.append(str(rezult))
            logTextEdit.append('OK')
            logTextEdit.setTextColor(white_color)
            item = self.tableWidget.item(startConteinerRow, startConteinerColumn)
            item.setBackground(green_color)
        else:
            item = self.tableWidget.item(startConteinerRow, startConteinerColumn)
            item.setBackground(red_color)
            logTextEdit.setTextColor(red_color)
            logTextEdit.append(
                strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": Error start conteiner %s" % selectedRunningConteiner + "\n" +
                str(rezult))
            logTextEdit.setTextColor(red_color)
            logTextEdit.append('Error')
            logTextEdit.setTextColor(white_color)

    def stopRunningImage(self):
        global item_selected, selectedStartConteiner, paused
        if selected_Column == 0:
            item = self.tableWidget_2.item(selected_row, selected_Column)
            item.setBackground(red_color)
            rezult = os.popen('docker stop %s' % selectedRunningConteiner)
            logTextEdit.setTextColor(white_color)
            logTextEdit.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": stopping image %s" %selectedRunningConteiner + "\n" +
                            str(rezult))
            logTextEdit.setTextColor(yelow_color)
            logTextEdit.append('OK')
            logTextEdit.setTextColor(white_color)
            item = self.tableWidget_2.item(selected_row, selected_Column+1)
            image_stop_name = item.text()
            items = self.tableWidget.findItems(image_stop_name, QtCore.Qt.MatchExactly)
            for i in items:
                i.setBackground(yelow_color)
            selectedStartConteiner = ''
            try:
                paused.remove(selectedRunningConteiner)
            except:
                pass


    def set_selectedRunningConteiner(self, row, collumn):
        global selectedRunningConteiner, item_selected, selected_Column, selected_row
        if collumn == 0:
            selected_Column = collumn
            selected_row = row
            item_selected = self.tableWidget_2.item(row, collumn)
            selectedRunningConteiner = item_selected.text()


    def updateStatusRunImage(self):
        rezult = os.popen("docker ps").read()
        if rezult != '':
            for i in reversed(range(self.tableWidget_2.rowCount())):
                self.tableWidget_2.removeRow(i)
            tableCollumnName = []
            runImageRows2 = []
            runImageRows3= []
            collumn = 0
            currentRowCount = self.tableWidget_2.rowCount()
            tableCollumnNameSource = [rezult.split('\n')[0]]
            tableCollumnNameSource = tableCollumnNameSource[0].split(' ')
            for i in tableCollumnNameSource:
                if i != '' and i != 'ID':
                    tableCollumnName.append(i)
            self.tableWidget_2.setColumnCount(len(tableCollumnName))
            self.tableWidget_2.setHorizontalHeaderLabels(tableCollumnName)
            runImageRows = []
            for i in rezult.split('\n'):
                runImageRows.append(i)
            runImageRows = runImageRows[1:]
            for i in runImageRows:
                if i != '':
                    runImageRows2.append(i.split('  '))
            for i in runImageRows2:
                for y in i:
                    if y != '':
                        runImageRows3.append(y)
                self.tableWidget_2.insertRow(currentRowCount)
                for a in runImageRows3:
                    item = QtWidgets.QTableWidgetItem(a)
                    if a not in paused:
                        item.setBackground(green_color)
                    else:
                        item.setBackground(blue_color)
                    self.tableWidget_2.setItem(currentRowCount, collumn, item)
                    collumn += 1
                self.tableWidget_2.insertRow(currentRowCount)
                runImageRows3 = []
            self.tableWidget_2.resizeColumnsToContents()


    def getAllConteiners(self):
        global tableCollumn
        collumn = 0
        string = ""
        rowForTable = []
        dockerPID = os.popen('pgrep -l Docker').read()
        if dockerPID == '':
            logTextEdit.setTextColor(red_color)
            logTextEdit.append('Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?\n')
            logTextEdit.setTextColor(white_color)
        else:
            logTextEdit.setTextColor(white_color)
            logTextEdit.setAlignment(QtCore.Qt.AlignCenter)
            logTextEdit.append("Docker run pid: %s" % dockerPID)
            logTextEdit.append("\n")
            logTextEdit.setAlignment(QtCore.Qt.AlignLeft)
        rezult = os.popen('docker images').read()
        rezult = rezult.split('\n')
        tableCollumnSorce = rezult[0].split(' ')
        for i in tableCollumnSorce:
            if i != '':
                tableCollumn.append(i)
        self.tableWidget.setColumnCount(len(tableCollumn))
        self.tableWidget.setHorizontalHeaderLabels(tableCollumn)
        for i in range(len(rezult))[1:]:
            for i in rezult[i].split(' '):
                if i != '':
                    rowForTable.append(i)
            currentRowCount = self.tableWidget.rowCount()
            self.tableWidget.insertRow(currentRowCount)
            rowForTable1 = rowForTable[:4]
            rowForTable2 = rowForTable[6:]
            rowForTable3 = rowForTable[3:6]
            for i in rowForTable3:
                string = string + i + " "
            rowForTable1.append(string)
            rowForTable4 = rowForTable1+rowForTable2
            if rowForTable4 != ['']:
                for i in rowForTable4:
                    item = QtWidgets.QTableWidgetItem(i)
                    self.tableWidget.setItem(currentRowCount, collumn, item)
                    self.tableWidget.resizeColumnsToContents()
                    collumn += 1
            rowForTable = []
            collumn = 0
            string = ""
            tableCollumn = []

class RunScripConfWindow(QtWidgets.QMainWindow):
    def __init__(self, table):
        global logTextEdit
        QtWidgets.QMainWindow.__init__(self, table)
        self.table = table
        self.ui = uic.loadUi('RunScriptWindow.ui', self)
        self.table.itemClicked.connect(self.itemClicked)
        self.pushButton_2.clicked.connect(self.saveScript)
        self.pixmap = QtGui.QPixmap('resurse/dockerlabel.png')
        self.pixmap = self.pixmap.scaled(30, 30)
        self.label_3.setPixmap(self.pixmap)

        logTextEdit.setAlignment(QtCore.Qt.AlignCenter)
        logTextEdit.append("###### Start app ######")
        logTextEdit.append("\n")
        logTextEdit.setAlignment(QtCore.Qt.AlignLeft)

    def itemClicked(self):
        item = self.table.selectedItems()
        containerName = item[0].text()
        self.label_2.setText(containerName)
        if """/""" in containerName:
            containerName = containerName[containerName.find("/") + 1 : ]
        if os.path.exists("""./run_scripts/""" + """%s""" % containerName) == False:
            script = open("""./run_scripts/""" + """%s""" % containerName, 'w')
            script.close()
        script = open("""./run_scripts/""" + """%s""" % containerName, 'r')
        scriptSRC = script.read()
        self.textEdit.setText(scriptSRC)
        script.close()

    def saveScript(self):
        logTextEdit.setTextColor(white_color)
        item = self.table.selectedItems()
        containerName = item[0].text()
        if """/""" in containerName:
            containerName = containerName[containerName.find("/") + 1 : ]
        script = open("""./run_scripts/""" + """%s""" % containerName, 'w')
        script.write(self.textEdit.toPlainText())
        script.close()
        logTextEdit.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": Save run script by name: %s" % containerName)
        if os.path.exists("""./run_scripts/""" + """%s""" % containerName) == True:
            logTextEdit.setTextColor(green_color)
            logTextEdit.append('OK\n')
            logTextEdit.setTextColor(white_color)
        else:
            logTextEdit.setTextColor(red_color)
            logTextEdit.append('Error save config!\n')
            logTextEdit.setTextColor(white_color)



        logTextEdit.setTextColor(white_color)
        self.hide()

class PsuTilThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
    emiter = QtCore.pyqtSignal(str)
    def run(self):
        global CPU_PERSENT_FOR_DOCKER_USAGE, MEM_PERSENT_FOR_DOCKER_USAGE
        try:
            dockerPIDCPU = os.popen('pgrep -l com.docker.hype').read()
            dockerPIDMEM = os.popen('pgrep -l Docker').read()
            pidCPU = dockerPIDCPU.split(" ")[0]
            pidMEM = dockerPIDMEM.split(" ")[0]
            processCPU = psutil.Process(int(pidCPU))
            processMEM = psutil.Process(int(pidMEM))
            CPU_PERSENT_FOR_DOCKER_USAGE.append(processCPU.cpu_percent(interval=0.1))
            MEM_PERSENT_FOR_DOCKER_USAGE.append(processMEM.memory_percent()*100)
            self.emiter.emit("UPDATE")
        except:
            pass

app = QtWidgets.QApplication(sys.argv)
Form = MainWindow()
Form.show()
sys.exit(app.exec_())