# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 12:23:22 2021

@author: Kardi
"""

import PySimpleGUI as sg
import TheoremProver as thp

def main():
    
    sg.ChangeLookAndFeel('SystemDefault') 
    
    # ------ Layout ------ # 
    column1=sg.Column([[sg.Button("Clean",key="btnClean")],
         [sg.Button("Prove",key="btnProve")],
         [sg.Button("Exit",key="btnExit")]])
    
    layout = [
        [sg.Text("Statements")],
        [sg.Multiline("",key='txtInput',size=(75, 5),enable_events=True,justification='left',font=("Helvetica", 8), text_color='blue',tooltip='Input Statements'),column1],
        [sg.Text("Result")],
        [sg.Multiline("",key='txtOutput',size=(85, 10), justification='left',font=("Helvetica", 8), text_color='blue',tooltip='Result')],
        ]

    # Create the window
    window = sg.Window("Theorem Prover", layout, 
                       finalize=True,
                       grab_anywhere=False,
                       return_keyboard_events=True, 
                       use_default_focus=False, location=(150, 150))
    
    # set initial values
    window['txtOutput'].update(thp.help())
    window['txtInput'].update('axiom P implies Q\naxiom Q implies R\naxiom P\nlemma R')

    # ---===--- Loop taking in user input --- #
    while True:
        event, value = window.read()
        
        # End program if user closes window or press Exit button
        if event =='Exit' or event == "btnExit" or event == sg.WIN_CLOSED:
            print(event, "exiting")
            break
        
        if event == 'btnClean':
            window['txtOutput'].update("")
            window['txtInput'].update('')
        if event == 'btnProve':
            try:
                textInput=value['txtInput']
                statement=textInput.splitlines()
                print(statement)
                # statement=textInput.split(",")
                # statement=re.split("^\S",textInput)
                # statement = ' '.join(statement).split() # remove empty strings from list
                
                
                output,proof=thp.prove(statement)
                print("proof",proof)
                s="\nProof:\n"
                for p in proof:
                    s=s+p+"\n"
                
                window['txtOutput'].update(output+s)
            except Exception as e:
                print('Error=',e)
            
        # for debugging event and value
        # print('event= {}'.format(event))
        # print('element= {}'.format(value))

    window.close()
    
if __name__=='__main__':
    main()