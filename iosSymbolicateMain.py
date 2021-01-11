from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import sys
from iosSymbolicateAPI import *


#Load pyqt ui file
uiForm_class=uic.loadUiType("iosSymbolicate.ui")[0]

class MainWindow(QMainWindow,uiForm_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.SetUI()
        self.symbolicateApi=SymbolicateAPI()

    
    def SetUI(self):
        self.UI_dsymDownLoad_pushButton.clicked.connect(self.Callback_dsymDownloadPushButton)
        self.UI_dsymFile_toolButton.clicked.connect(self.Callback_dsymFileToolButton)
        self.UI_ipsFile_toolButton.clicked.connect(self.Callback_ipsFileToolButton)
        

        pass

    def Callback_dsymDownloadPushButton(self):
        region=self.UI_Region_comboBox.currentText()
        serviceType=self.UI_Type_comboBox.currentText()
        branch=self.UI_branch_lineEdit.text()
        buildNum=self.UI_buildNum_lineEdit.text()
        #self.symbolicateApi.StartDownloadFiles(self.UI_dsymProgressBar,region,serviceType,branch,buildNum)
        self.DownloadStart(region,serviceType,branch,buildNum)
    
    def Callback_dsymFileToolButton(self):
        filePath=QFileDialog.getOpenFileName(self)
        self.UI_dsymPath_lineEdit.setText(filePath[0])

    def Callback_ipsFileToolButton(self):
        filePath=QFileDialog.getOpenFileName(self)
        self.UI_ipsPath_lineEdit.setText(filePath[0])


    def DownloadStart(self,region,serviceType,branch,buildNum):
        self.thread=DownloadThread(region,serviceType,branch,buildNum)
        self.thread.data_downloaded.connect(self.OnDataReady)
        self.thread.data_progress.connect(self.OnProgressReady)
        self.thread.onFailed.connect(self.OnFailed)
        self.thread.onSuccess.connect(self.OnSuccess)
        self.progress_initilized=False
        self.SetEnableDownloadUI(False)
        self.thread.start()

    def SetEnableDownloadUI(self,enable):
        self.UI_Region_comboBox.setEnabled(enable)
        self.UI_Type_comboBox.setEnabled(enable)
        self.UI_branch_lineEdit.setEnabled(enable)
        self.UI_buildNum_lineEdit.setEnabled(enable)
        self.UI_dsymDownLoad_pushButton.setEnabled(enable)


    def OnDataReady(self,data):
        self.statusbar.showMessage(str(data))
        print(str(data))
        
    def OnProgressReady(self,data):
        if self.progress_initilized:
            self.UI_dsymProgressBar.setValue(self.UI_dsymProgressBar.value()+int(data))
        else:
            self.UI_dsymProgressBar.setMaximum(int(data))
            self.progress_initilized=True

    def OnFailed(self,data):
        self.statusbar.showMessage("FTP Status: Failed")
        msgBox=QMessageBox()
        msgBox.setWindowTitle("ERROR")
        msgBox.setText(data)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        self.SetEnableDownloadUI(True)

    def OnSuccess(self,data):
        self.statusbar.showMessage(str(data[0]))
        self.SetEnableDownloadUI(True)
        self.UI_dsymPath_lineEdit.setText(str(data[1]))



        
    




if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    app.exec_()