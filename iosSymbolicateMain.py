from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import uic
import sys
from iosSymbolicateAPI import *
import os
from PyQt6 import QtGui

def ResourcePath(relativePath):
    basePath=getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath,relativePath)

uiFile=ResourcePath('iosSymbolicate.ui')
#Load pyqt ui file
uiForm_class=uic.loadUiType(uiFile)[0]

class MainWindow(QMainWindow,uiForm_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        
        self.SetUI()
        self.config=Config()
        self.symbolicateApi=SymbolicateAPI(self.config)
        self.symbolicateApi.DeleteOutput()
        self.symbolicateApi.DeleteTempFolder()

    
    def SetUI(self):
        self.UI_dsymDownLoad_pushButton.clicked.connect(self.Callback_dsymDownloadPushButton)
        self.UI_dsymFile_toolButton.clicked.connect(self.Callback_dsymFileToolButton)
        self.UI_ipsFile_toolButton.clicked.connect(self.Callback_ipsFileToolButton)
        self.UI_symbolicate_pushButton.clicked.connect(self.Callback_SymbolicateButton)
        self.UI_convertIPS_pushButton.clicked.connect(self.Callback_convertIPSButton)
        self.UI_SaveAsPushButton.clicked.connect(self.Callback_saveAsButton)
        self.UI_newWindowPushButton.clicked.connect(self.Callback_newWindowButton)
        self.w2=None
    
       
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        self.symbolicateApi.DeleteTempFolder()
        return super().closeEvent(a0)

      

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
        filePath=QFileDialog.getOpenFileName(self,"Open Crash Report(ips/crash) File","","Crash File(*.ips *.crash)")
        self.UI_ipsPath_lineEdit.setText(filePath[0])
    
    def Callback_SymbolicateButton(self):

        self.SetEnableDownloadUI(False)
        message="Symbolicate Failed:{}"
        
        result=False
        msg=''

        result,msg=self.symbolicateApi.StartSymbolicate(self.UI_dsymPath_lineEdit.text(),self.UI_ipsPath_lineEdit.text())
        
        if result == True:
            message="Symbolicate Success"
            self.UI_textBrowser.setText(msg)
        else:
            message=message.format(msg)

        
        msgBox=QMessageBox() 
        msgBox.setWindowTitle("Process")
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()
        
        self.SetEnableDownloadUI(True)

        self.symbolicateApi.DeleteOutput()

    def Callback_convertIPSButton(self):
        self.SetEnableDownloadUI(False)
        result,msg=self.symbolicateApi.ConvertFromJsonIPS(self.UI_ipsPath_lineEdit.text())
        message=''
        if result == True:
            message="[Convert IPS File success]\n(다시 symbolicate버튼을 누르시면 됩니다)"
            self.statusbar.showMessage("Convert IPS File success. Start Symbolicate!")
            self.UI_ipsPath_lineEdit.setText(msg)
        else:
            message=f"Failed to convert IPS file : {msg}"
        
        msgBox=QMessageBox()
        msgBox.setWindowTitle("Process")
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()

        self.SetEnableDownloadUI(True)
        pass
    def Callback_saveAsButton(self):
        file_name=QFileDialog.getSaveFileName(self,"Save As","","Crash File(*.ips *.crash)")
        if file_name[0]:
            ipsText=self.UI_textBrowser.toPlainText()
            with open(file_name[0],'w',encoding='utf-8') as f:
                f.write(ipsText)
    def Callback_newWindowButton(self):

        if self.w2 is None:
            self.w2= SubWindow()

        text=self.UI_textBrowser.toPlainText()
        self.w2.SetSymbolicateTextToTextBrowser(text)
        self.w2.show()



    def DownloadStart(self,region,serviceType,branch,buildNum):
        self.thread=DownloadThread(self.config,region,serviceType,branch,buildNum)
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
        self.UI_symbolicate_pushButton.setEnabled(enable)
        self.UI_ipsPath_lineEdit.setEnabled(enable)
        self.UI_dsymPath_lineEdit.setEnabled(enable)
        self.UI_convertIPS_pushButton.setEnabled(enable)


    def OnDataReady(self,data):
        self.statusbar.showMessage(str(data))
        #print(str(data))
        
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
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()
        self.SetEnableDownloadUI(True)

    def OnSuccess(self,data):
        self.statusbar.showMessage(str(data[0]))
        self.SetEnableDownloadUI(True)
        self.UI_dsymPath_lineEdit.setText(str(data[1]))



        
    
class SubWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.button=QPushButton("Save as File")
        self.button.clicked.connect(self.Callback_SaveButton)

       
        self.tb=QTextBrowser() 
      
        
        layout=QVBoxLayout()

        layout.addWidget(self.button)
        layout.addWidget(self.tb)
        self.setLayout(layout)
        self.setMinimumSize(1200,500)
        print("sub windows")

    def SetSymbolicateTextToTextBrowser(self,_text):
        self.tb.setText(_text)

    def Callback_SaveButton(self):

        file_name=QFileDialog.getSaveFileName(self,"Save As","","Crash File(*.ips *.crash)")
        if file_name[0]:
            ipsText=self.tb.toPlainText()
            with open(file_name[0],'w',encoding='utf-8') as f:
                f.write(ipsText)
        




if __name__=="__main__":
    print(os.getcwd())

    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    app.exec()