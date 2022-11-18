//
//  SymbolicateAPI.swift
//  iOSSymbolicator
//
//  Created by 조을연 on 2022/11/18.
//

import Foundation




class SymbolicateAPI
{
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
        //unzip dsym.zip
        //Copy dsym file/app file
        
        //iOS Symbolicate Command(Example)
        /*
         ips파일/ dsym파일/ app파일 세가지가 필요하다.
         
         export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
         
         /Applications/Xcode.app/Contents/SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash maplem.ips maplem.app.dsym --output maplm_output.ips
         
         */
        
    }
    
    func HandleFileTest()
    {
        let fileManager=FileManager()
        
        let documentDirectory=fileManager.urls(for:.documentDirectory,in: .userDomainMask).first
        let dataPath=documentDirectory?.appendingPathComponent("Symbolicate_Temp")
        
        print(dataPath!.path)
        var isDir=ObjCBool(true)
        let existDir=fileManager.fileExists(atPath: dataPath!.path, isDirectory: &isDir)
        print("Directory exist: \(existDir)")
        
        if existDir == true
        {
            return
        }
          
        do{
            try fileManager.createDirectory(atPath: dataPath!.path, withIntermediateDirectories: false, attributes: nil)
        }
        catch let error as NSError{
            print("Handle File Test Error:\(error)")
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
