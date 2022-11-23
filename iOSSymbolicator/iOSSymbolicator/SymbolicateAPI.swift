//
//  SymbolicateAPI.swift
//  iOSSymbolicator
//
//  Created by 조을연 on 2022/11/18.
//

import Foundation

import Zip



class SymbolicateAPI
{
    var symbolicateTempFolderPath:URL?;
    
    func GetXcodePath()->String{
        let result = (try? safeShell("xcode-select -p"))!
        return result
    }
    
    func GetXcodeSymbolicateToolPath()->String{
        let symbolicatePath="SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash"
        
        
        var xcodePath=GetXcodePath()
        xcodePath = xcodePath.replacingOccurrences(of: "Developer", with: symbolicatePath)
        
        return xcodePath
        
    }
    
    func StartSymbolicate(_dsymZupFilePath:String,_ipsFilePath:String)
    {
        do {
            if let filePath = symbolicateTempFolderPath?.appendingPathComponent("dfd.zip")
            {
                let unzipDirectory = try Zip.quickUnzipFile(filePath) // Unzip
                
                print(unzipDirectory.path)
            }
            
        }
        catch {
            print("UnZip File: Something went wrong")
        }
        //unzip dsym.zip
        //Copy dsym file/app file
        
        //iOS Symbolicate Command(Example)
        /*
         ips파일/ dsym파일/ app파일 세가지가 필요하다.
         
         export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
         
         /Applications/Xcode.app/Contents/SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash maplem.ips maplem.app.dsym --output maplm_output.ips
         
         */
        
    }
    
    func DownloadFileViaFTP()
    {
        DispatchQueue.global(qos: .utility).async {
            var url = URL(string: "")
            var data:Data? = nil
            
            if let anUrl=url
            {
                do{
                    data = try Data(contentsOf: anUrl)
                }
                catch
                {
                    print("")
                }
               
            }
            
            DispatchQueue.main.async {
                print(data?.hashValue)
            }
        }
    }
    
    func SetConfig()
    {
        if let path = Bundle.main.path(forResource: "Config.json", ofType: nil)
        {
            print("file exist")
            do{
                let contents = try String(contentsOfFile: path)
               
                let config = try? JSONDecoder().decode(Config.self,from: contents.data(using: .utf8)!)
               
                print(config?.CommonSettings.symbolicatePath ?? "config null")
                
            }
            catch{
                print(error.localizedDescription)
            }
        }
        else{
            print("Config.json file not exit")
        }
           
        
      
        
    }
    
    func HandleFileTest()
    {
        let fileManager=FileManager()
        
        let documentDirectory=fileManager.urls(for:.documentDirectory,in: .userDomainMask).first
        symbolicateTempFolderPath=documentDirectory?.appendingPathComponent("Symbolicate_Temp")
        
        print(symbolicateTempFolderPath?.path ?? "symbolicate temp path is nil")
        
        var isDir=ObjCBool(true)
        
        if let path=symbolicateTempFolderPath?.path
        {
            let existDir=fileManager.fileExists(atPath: path, isDirectory: &isDir)
            
            print("Directory exist: \(existDir)")
            
            if existDir == true
            {
                return
            }
              
            do{
                try fileManager.createDirectory(atPath: path, withIntermediateDirectories: false, attributes: nil)
            }
            catch let error as NSError{
                print("Handle File Test Error:\(error)")
            }
            
        }
       
        
    }
    
    @discardableResult // Add to suppress warnings when you don't want/need a result
    func safeShell(_ command: String) throws -> String {
        let task = Process()
        let pipe = Pipe()
        
        task.standardOutput = pipe
        task.standardError = pipe
        task.arguments = ["-c", command]
        task.executableURL = URL(fileURLWithPath: "/bin/zsh")
        task.standardInput = nil

        try task.run()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        let output = String(data: data, encoding: .utf8)!
        
        return output
    }
    
}

struct Config : Codable
{
    var RegionInfo: [RegionInfo]
    var CommonSettings: CommonSettings
    
    struct RegionInfo: Codable
    {
        var Region :String
        var ftpServer:String
        var buildType:[BuildType]
        
        
        struct BuildType: Codable
        {
            var client_type:String
            var archiveFileName: String
            var app_dsymPath: String
            var app_filePath :String
        }
    }
    
    struct CommonSettings:Codable
    {
        var symbolicatePath :String
        var ftpCurlCommand : String
        var getXcodePathCommand:String
        var unityFramework_dsym_path:String
    }
    
   
}
