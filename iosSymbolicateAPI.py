import subprocess
import sys
from PyQt6.QtCore import *
import ftplib
import os
import zipfile
import shutil
import json
import traceback
from subprocess import CalledProcessError
import time

class SymbolicateAPI():
    def __init__(self,_config):
        self.config=_config

    def UnZipFile(self,dsymFilePath):
        
        if os.path.exists(dsymFilePath)==False:
            return False
        try:
            with zipfile.ZipFile(dsymFilePath) as zf:
                zf.extractall('./Output/')
        except:
            #print("Unzip failed")
            return False
            
        return True

    def GetXcodePath(self):
        try:
            xcodeSelectCommand = self.config.commonSettings.getXcodePathCommand
            xcodePath=subprocess.check_output(xcodeSelectCommand,shell=True)
      
            return xcodePath.decode('utf-8')
        except:
            #print("xcode-select failed")
            return ""

    def DeleteOutput(self):
        try:
            if os.path.exists('./Output'): 
                shutil.rmtree('./Output')
        except:
            pass
    def DeleteTempFolder(self):
        try:
            if os.path.exists('./Temp'):
                shutil.rmtree('./Temp')
        except Exception as e:
            print(e)



    def GetXCodeSymbolicateToolPath(self):
        symbolicatePath= self.config.commonSettings.symbolicatePath#"SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash"
        xcodePath=self.GetXcodePath()
        xcodePath=xcodePath.replace("Developer",symbolicatePath)
        return xcodePath
    
    def CopyDsymFile(self,dsymFileZipPath):
        
        splitPaths=dsymFileZipPath.split('/')
        xcarchiveFileName=splitPaths[-1].replace('.zip','')

        chinaAppVersion=xcarchiveFileName.split('_')[-2].replace('0','C')

        unityframework_dsym_path=self.config.commonSettings.unityFramework_dsym_path.format(xcarchiveFileName)
        #shutil.move(unityframework_dsym_path,"./UnityFramework.framework.dSYM")
        tempFolder=self.MakeTempFolder()

        self.MoveFile(unityframework_dsym_path,os.path.join(tempFolder,"UnityFramework.framework.dSYM"))
        region=["Korea","Global","Japan","China"]
        buildType=["QA","IAP","LIVE"]
        
        
        for rg in region:
            for bt in buildType:
                if rg == "China" and (bt =="IAP" or bt =="LIVE"):
                    continue
                if rg !="China":
                    app_dsym_path= self.config.regionInfos[rg].buildTypes[bt].app_dsymPath.format(xcarchiveFileName) #"./XCode/Archive/{}/dSYMs/inhouse.app.dSYM".format(xcarchiveFileName)
                    app_file_path=self.config.regionInfos[rg].buildTypes[bt].app_filePath.format(xcarchiveFileName)#"./XCode/Archive/{}/Products/Applications/inhouse.app".format(xcarchiveFileName)
                else:
                    app_dsym_path=self.config.regionInfos[rg].buildTypes[bt].app_dsymPath.format(xcarchiveFileName,chinaAppVersion) #"./Output/XCode/Archive/MapleM_Stage_{0}_1.xarchive/dSYMs/{1}.app.dSYM
                    app_file_path=self.config.regionInfos[rg].buildTypes[bt].app_filePath.format(xcarchiveFileName,chinaAppVersion)#"./Output/XCode/Archive/MapleM_Stage_{0}_1.xarchive/Products/Applications/{1}.app

                
                app_dsym_file=app_dsym_path.split("/")[-1]
                app_file=app_file_path.split("/")[-1]
               
                if os.path.exists(app_dsym_path):
                    
                    #shutil.move(app_dsym_path,f"./{app_dsym_file}")
                    #shutil.move(app_file_path,f"./{app_file}")

                    self.MoveFile(app_dsym_path,tempFolder)#f"./{app_dsym_file}")
                    self.MoveFile(app_file_path,tempFolder)#f"./{app_file}")
                  
                    return os.path.join(tempFolder,"UnityFramework.framework.dSYM")#"./UnityFramework.framework.dSYM"
    

        return ""
        

    def StartSymbolicate(self,dsymFileZipPath,ipsFilePath):
        if os.path.exists(dsymFileZipPath) is False:
            return (False,"dSym File Path is wrong path(not found)")
        if os.path.exists(ipsFilePath) is False:
            return (False,"ips File Path is wrong path(not found)")

        self.UnZipFile(dsymFileZipPath)
        dsymFilePath=self.CopyDsymFile(dsymFileZipPath)
        symbolicatePath=self.GetXCodeSymbolicateToolPath()
        #outputFile=ipsFilePath.replace(".ips","_output.ips")
        symbolicatedOutput=""
        time.sleep(3)
        
        try:
            command='"{} {} {}"'.format(symbolicatePath,ipsFilePath,dsymFilePath)
            print("COMMAND:"+command)
            #command='"{} {} {} --output {}"'.format(symbolicatePath,ipsFilePath,dsymFilePath,outputFile)
            #print(command)
            xcodePath='"{}"'.format(self.GetXcodePath().strip())
           
            #print(xcodePath)
            output=subprocess.run("bash symbolicate.sh {} {}".format(xcodePath,command),shell=True,check=True,capture_output=True)
            symbolicatedOutput=output.stdout.decode('utf-8')
           
        except CalledProcessError as e:
            callProcessErr=e.stderr.decode('utf-8')
            errorMessage=f"Something Wrong: {callProcessErr}"
            if "No crash report version in" in callProcessErr:
                errorMessage="[IPS file format needed to convert]\nips파일포맷이 최근포맷이라 포맷변경이 필요합니다.\n\nConvert버튼을 누르세요"
            return (False,errorMessage)
        return (True,symbolicatedOutput)

    def ConvertFromJsonIPS(self,ipsPath):
        try:
            if ipsPath is None or ipsPath == "":
                return False,"Fail to convert : ips file path is blank"
            
            tempFolderPath=self.MakeTempFolder()

            inputIpsFileName=os.path.basename(ipsPath)
            outputIpsFileName=inputIpsFileName.replace(".ips","_Converted.ips")

            inputIpsFilePath=os.path.join(tempFolderPath,inputIpsFileName)
            outputIpsPath=os.path.join(tempFolderPath,outputIpsFileName)

            print(ipsPath)
            print(outputIpsPath)

            

            if os.path.exists(ipsPath):
                shutil.copy(ipsPath,inputIpsFilePath)
            else:
                False,"Fail to convert : ips file not found"
            

            o=subprocess.run(f"swift convertFromJSON.swift -i Temp/{inputIpsFileName} -o Temp/{outputIpsFileName}",shell=True,check=True,capture_output=True,cwd=None)
           
        except CalledProcessError as e:
            return (False,f"Failed to convert :{e.stderr.decode('utf-8')}")
        
        return (True,outputIpsPath)
    def MakeTempFolder(self):
        tempFolderPath=os.path.join(os.getcwd(),"Temp")
        if not os.path.exists(tempFolderPath):
            os.makedirs(tempFolderPath)
        return tempFolderPath
    def MoveFile(self,src,dst):
        try:
            proc=subprocess.Popen(f"mv {src} {dst}",shell=True)
            proc.wait()
            
            
        except Exception as e:
            print(f"MoveFile error: {e}")
            

            

        

    
class Config():
    def __init__(self) -> None:
        self.SetConfig()

    def SetConfig(self):


        try:
            currentPath= os.path.abspath(os.path.dirname(__file__))
            configFilePath=f"{currentPath}/Config.json"

            if True== os.path.exists(configFilePath):
                print('ConfigFile Exist')

            
            with open(configFilePath,'r') as f:
                info=json.load(f)
            
            self.commonSettings=self.CommonSettings(info["CommonSettings"])

            infos=info["RegionInfo"]
            if infos is not None and len(infos)>0:
                self.regionInfos = dict()
                for info in infos:
                    regionInfo=self.RegionInfo(info)
                    if regionInfo is not None:
                        self.regionInfos[regionInfo.Region]=regionInfo
                



            
        except Exception as e:
            print(e)
            return

    class RegionInfo():
        def __init__(self,info):
            self.Region=info["Region"]
            self.ftpServer=info["ftpServer"]
            self.ftpPath=info["ftpPath"]
            self.buildTypes=dict()


            jsonBts=info["buildType"]
            if jsonBts is not None and len(jsonBts)>0:
                for bt in jsonBts:
                    _bt=self.BuildType(bt)
                    if _bt is not None:
                        self.buildTypes[_bt.Type]=_bt
            
           
        class BuildType():
            def __init__(self,_buildType):
                self.Type=_buildType["Type"]
                self.archiveFileName=_buildType["archiveFileName"]
                self.app_dsymPath=_buildType["app_dsymPath"]
                self.app_filePath=_buildType["app_filePath"]

    class CommonSettings():
        def __init__(self, commonSettingsDict):
            try:
                self.symbolicatePath= commonSettingsDict["symbolicatePath"]
                self.ftpCurlCommand =commonSettingsDict["ftpCurlCommand"]
                self.getXcodePathCommand=commonSettingsDict["getXcodePathCommand"]
                self.unityFramework_dsym_path=commonSettingsDict["unityFramework_dsym_path"]
                self.ftpUserName=commonSettingsDict["ftpUserName"]
                self.ftpPassword=commonSettingsDict["ftpPassword"]
            except Exception as e:
                print(e)
            



     

class DownloadThread(QThread):
    def __init__(self,_config,region,serviceType,branch,buildNum):
        super().__init__()
        self.region=region
        self.serviceType=serviceType
        self.branch=branch
        self.buildNum=buildNum
        self.config=_config

       
        
        self.archiveFileName =""
        self.ftpServer=""
        self.ftpPath=""


        regionInfo = self.config.regionInfos[self.region]
        if regionInfo is not None:
            
            self.ftpServer=regionInfo.ftpServer
            self.ftpPath=regionInfo.ftpPath

            buildtypeInfo= regionInfo.buildTypes[self.serviceType]
            if buildtypeInfo is not None:
                self.archiveFileName = buildtypeInfo.archiveFileName


    data_downloaded=pyqtSignal(object)
    data_progress=pyqtSignal(object)
    onFailed=pyqtSignal(object)
    onSuccess=pyqtSignal(object)

    def run(self):
        self.data_downloaded.emit("FTP Status: Connecting..")

        with ftplib.FTP(self.ftpServer) as ftp:
            try:
                ftp.login(user=self.config.commonSettings.ftpUserName,passwd=self.config.commonSettings.ftpPassword)
            except:
                self.onFailed.emit("FTP Authentication Failed")
                return
            try:
                ftp.cwd(self.ftpPath.format(self.region,self.branch,self.serviceType))
            except:
                self.onFailed.emit("Could not found Folder")
                return

          
            
            self.downloadFile=self.archiveFileName.format(self.branch,self.buildNum)
            print(self.downloadFile)
          
            try:
                totalSize=ftp.size(self.downloadFile)
            except:
                self.onFailed.emit("File Not Found")
                return
            #print("totalSize:{}".format(totalSize))

            self.data_progress.emit(str(totalSize))

            self.data_downloaded.emit('FTP Status: Downloading..')
            currentDir=os.getcwd()
            if os.path.isdir(currentDir+"/Output") is False:
                os.mkdir(currentDir+"/Output")
            


            with open(currentDir+"/Output/"+self.downloadFile,'wb') as self.localFile:
                ftp.retrbinary('RETR '+self.downloadFile,self.file_write)
                
        self.onSuccess.emit(['FTP Status: File Download Success',"./Output/"+self.downloadFile])
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
#     pass
    



    

    