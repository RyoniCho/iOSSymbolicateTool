import subprocess
import sys
from PyQt5.QtCore import *
import ftplib
import os
import zipfile
import shutil

class SymbolicateAPI():
    def __init__(self):
        pass

    def UnZipFile(self,dsymFilePath):
        if os.path.exists(dsymFilePath)==False:
            return False
        try:
            with zipfile.ZipFile(dsymFilePath) as zf:
                zf.extractall()
        except:
            #print("Unzip failed")
            return False
            
        return True

    def GetXcodePath(self):
        try:
            xcodePath=subprocess.check_output("xcode-select -p",shell=True)
      
            return xcodePath.decode('utf-8')
        except:
            #print("xcode-select failed")
            return ""


    def GetXCodeSymbolicateToolPath(self):
        symbolicatePath="SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash"
        xcodePath=self.GetXcodePath()
        xcodePath=xcodePath.replace("Developer",symbolicatePath)
        return xcodePath
    
    def CopyDsymFile(self,dsymFileZipPath):
        splitPaths=dsymFileZipPath.split('/')
        xcarchiveFileName=splitPaths[-1].replace('.zip','')

        unityframework_dsym_path="./XCode/Archive/{}/dSYMs/UnityFramework.framework.dSYM".format(xcarchiveFileName)
        shutil.move(unityframework_dsym_path,"./UnityFramework.framework.dSYM")
        
        #KOREA/GLOBAL/JAPAN STAGE
        app_dsym_path="./XCode/Archive/{}/dSYMs/inhouse.app.dSYM".format(xcarchiveFileName)
        app_file_path="./XCode/Archive/{}/Products/Applications/inhouse.app".format(xcarchiveFileName)
        if os.path.exists(app_dsym_path):
            shutil.move(app_dsym_path,"./inhouse.app.dSYM")
            shutil.move(app_file_path,"./inhouse.app")
            return "./inhouse.app.dSYM"

        #KOREA IAP/LIVE
        app_dsym_path="./XCode/Archive/{}/dSYMs/maplem.app.dSYM".format(xcarchiveFileName)
        app_file_path="./XCode/Archive/{}/Products/Applications/maplem.app".format(xcarchiveFileName)
        if os.path.exists(app_dsym_path):
            shutil.move(app_dsym_path,"./maplem.app.dSYM")
            shutil.move(app_file_path,"./maplem.app")
            return "./maplem.app.dSYM"

        #GLOBAL IAP/LIVE
        app_dsym_path="./XCode/Archive/{}/dSYMs/global.app.dSYM".format(xcarchiveFileName)
        app_file_path="./XCode/Archive/{}/Products/Applications/global.app".format(xcarchiveFileName)
        if os.path.exists(app_dsym_path):
            shutil.move(app_dsym_path,"./global.app.dSYM")
            shutil.move(app_file_path,"./global.app")
            return "./global.app.dSYM"

        #JAPAN IAP/LIVE
        app_dsym_path="./XCode/Archive/{}/dSYMs/japan.app.dSYM".format(xcarchiveFileName)
        app_file_path="./XCode/Archive/{}/Products/Applications/japan.app".format(xcarchiveFileName)
        if os.path.exists(app_dsym_path):
            shutil.move(app_dsym_path,"./japan.app.dSYM")
            shutil.move(app_file_path,"./japan.app")
            return "./japan.app.dSYM"
        
        return ""
        

    def StartSymbolicate(self,dsymFileZipPath,ipsFilePath):
        self.UnZipFile(dsymFileZipPath)
        dsymFilePath=self.CopyDsymFile(dsymFileZipPath)
        symbolicatePath=self.GetXCodeSymbolicateToolPath()
        outputFile=ipsFilePath.replace(".ips","_output.ips")
        try:
            command='"{} {} {} --output {}"'.format(symbolicatePath,ipsFilePath,dsymFilePath,outputFile)
            #print(command)
            xcodePath='"{}"'.format(self.GetXcodePath().strip())
          
            #print(xcodePath)
            output=subprocess.check_output("bash symbolicate.sh {} {}".format(xcodePath,command),shell=True)
            #print(output)
           
        except:
           # print(sys.exc_info()[0])
           # print(sys.exc_info()[1])
            return False
        return True

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
        
        machineNumber="197"

        if _region=='Korea':
            machineNumber="187"


        self.ftpCurl="curl ftp://mmjenkins:~tjqjxla1234@10.10.56.{0}/Client/{1}/{2}/IOS/{3}/{4} -o ./{5}".format(machineNumber,_region,_branch,_serviceType,self.downloadFile,self.downloadFile)

        try:
            subprocess.call(self.ftpCurl,shell=True)
        except:
            pass
            #print(sys.exc_info()[0])
            #print(sys.exc_info()[1])
        

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
        ftpIp='10.10.56.197'
        if self.region=='Korea':
            ftpIp='10.10.56.187'

        with ftplib.FTP(ftpIp) as ftp:
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
            
            
            #print("DownloadFile:"+self.downloadFile)
           




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




# def StartSymbolicate():
   
#     dsymFilePath="./inhouse.app.dSYM"
#     symbolicatePath="/Applications/Xcode11.3.app/Contents/SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash "
#     outputFile="/Users/nexon/Desktop/symbol_test/inhouse-2021-01-06-114209_output.ips"
#     ipsFilePath="/Users/nexon/Desktop/symbol_test/inhouse-2021-01-06-114209.ips"
#     try:
#         command='"{}"'.format(symbolicatePath+ipsFilePath+" "+dsymFilePath+" --output "+outputFile)
#         print(command)
#         output=subprocess.check_output('bash symbolicate.sh "/Applications/Xcode11.3.app/Contents/Developer" {}'.format(command),shell=True)
#         print(output)
#         #subprocess.call("export DEVELOPER_DIR={}".format(self.GetXcodePath()),shell=True)
#         #subprocess.call(command,shell=True,env=dict(DEVELOPER_DIR=self.GetXcodePath()),**os.environ)
#     except:
#         print(sys.exc_info()[0])
#         print(sys.exc_info()[1])
#         return False
#     return True

# if __name__ == "__main__":
#     StartSymbolicate()


    

    