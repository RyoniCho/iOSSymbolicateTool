//
//  ViewController.swift
//  iOSSymbolicator
//
//  Created by 조을연 on 2022/11/18.
//

import Cocoa

class ViewController: NSViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        
        let symbol = SymbolicateAPI()
        print(symbol.GetXcodePath())
        print(symbol.GetXcodeSymbolicateToolPath())
        symbol.HandleFileTest()
        
        // Do any additional setup after loading the view.
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }


}

