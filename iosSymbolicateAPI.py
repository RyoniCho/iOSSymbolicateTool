import subprocess
import sys
from PyQt5.QtCore import *
import ftplib

class SymbolicateAPI():
    def __init__(self):
        pass

    def StartDownloadFiles(self,_progressBar,_region,_serviceType,_branch,_buildNum):
        
        self.qaArchiveFileName="MapleM_Stage_{}.{}_1.xcarchive.zip".format(_branch,_buildNum)
        self.iapArchiveFileName_kor="MapleM_StageIAP_{}.0_3.xcarchive.zip".format(_branch) #Korea
        self.iapArchiveFileName="MapleM_Stage_IAP_{}.0_3.xcarchive.zip".format(_branch) #Global,Japan
        self.liveArchiveFileName="MapleStoryM_{}.{}_{}.xcarchive.zip".format(_branch,_buildNum,_buildNum)

        if _serviceType == "QA":
            self.downloadFile=self.qaArchiveFileName
        elif _serviceType =="IAP":
            if _region=='Korea':
                self.downloadFile=self.iapArchiveFileName_kor
            else:
                self.downloadFile=self.iapArchiveFileName
        else:
            self.downloadFile=self.liveArchiveFileName


        self.ftpCurl="curl ftp://mmjenkins:~tjqjxla1234@10.10.56.197/Client/{0}/{1}/IOS/{2}/{3} -o ./{4}".format(_region,_branch,_serviceType,self.downloadFile,self.downloadFile)

        try:
            subprocess.call(self.ftpCurl,shell=True)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
        

class DownloadThread(QThread):
    def __init__(self,region,serviceType,branch,buildNum):
        super().__init__()
        self.region=region
        self.serviceType=serviceType
        self.branch=branch
        self.buildNum=buildNum

    data_downloaded=pyqtSignal(object)
    data_progress=pyqtSignal(object)
    onFailed=pyqtSignal(object)
    onSuccess=pyqtSignal(object)

    def run(self):
        self.data_downloaded.emit("FTP Status: Connecting..")

        with ftplib.FTP('10.10.56.197') as ftp:
            try:
                ftp.login(user='mmjenkins',passwd='~tjqjxla1234')
            except:
                self.onFailed.emit("FTP Authentication Failed")
                return
            try:
                ftp.cwd('/Client/{0}/{1}/IOS/{2}/'.format(self.region,self.branch,self.serviceType))
            except:
                self.onFailed.emit("Could not found Folder")
                return


            
            self.qaArchiveFileName="MapleM_Stage_{}.{}_1.xcarchive.zip".format(self.branch,self.buildNum)
            self.iapArchiveFileName_kor="MapleM_StageIAP_{}.0_3.xcarchive.zip".format(self.branch) #Korea
            self.iapArchiveFileName="MapleM_Stage_IAP_{}.0_3.xcarchive.zip".format(self.branch) #Global,Japan
            self.liveArchiveFileName="MapleStoryM_{}.{}_{}.xcarchive.zip".format(self.branch,self.buildNum,self.buildNum)

            if self.serviceType == "QA":
                self.downloadFile=self.qaArchiveFileName
            elif self.serviceType =="IAP":
                if self.region=='Korea':
                    self.downloadFile=self.iapArchiveFileName_kor
                else:
                    self.downloadFile=self.iapArchiveFileName
            else:
                self.downloadFile=self.liveArchiveFileName
            
            
            print("DownloadFile:"+self.downloadFile)
           




            #self.downloadFile='1.60.0_aos_gitHistory.txt'
            try:
                totalSize=ftp.size(self.downloadFile)
            except:
                self.onFailed.emit("File Not Found")
                return
            print("totalSize:{}".format(totalSize))

            self.data_progress.emit(str(totalSize))

            self.data_downloaded.emit('FTP Status: Downloading..')
            with open(self.downloadFile,'wb') as self.localFile:
                ftp.retrbinary('RETR '+self.downloadFile,self.file_write)
                
        self.onSuccess.emit(['FTP Status: File Download Success',self.downloadFile])
    def file_write(self,data):
        self.localFile.write(data)
        self.data_progress.emit(str(len(data)))



    