# -*- coding: utf-8 -*-
# Molar mass calculator

import json
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_main_window
import sys

def split_form(arg: str) -> list:
    '''
    Splits the formula in separate elements
    returns list: the 1st value is splitted formula,
    the 2nd value is an error message 
    like which elements doesn't exist or WFW (Wrong formula written)
    '''
    error_word=''
    i = 0
    data = []
    arg += '+'
    while i < len(arg)-1:
        if arg[i-1].isupper() and arg[i].islower():
            if arg[i-1]+arg[i] not in elems:
                error_word = arg[i-1]+arg[i]
                break

            if i==0:
                error_word = arg[i]
                break

            data.append(arg[i-1]+arg[i])
            i+=1

        
        elif arg[i].isupper() and arg[i+1].isupper(): 
            if arg[i]  not in elems:
                error_word = arg[i]
                break

            data.append(arg[i])
            i+=1

        elif arg[i].isupper():
            if arg[i]+arg[i+1] in elems:
                i+=1
                continue

            if arg[i] not in elems:
                error_word = arg[i]
                break

            data.append(arg[i])
            i+=1
        
        elif arg[i] == '(':
            ind_end = arg.rfind(')')
            l = arg[i+1:ind_end]
            if arg[ind_end+1].isdigit():
                cnt = arg[ind_end+1]
                i = ind_end+2
                while True:
                    if arg[i].isdigit():
                        cnt += arg[i]
                    
                    else:
                        break
                    i+=1
                

                cnt = int(cnt)


            else:
                cnt = 1
            
            added = split_form(l)
            if added[1]:
                error_word=added[1]
                break
            
            added[0].append(cnt)
            data.append(added[0])
            if cnt==1:
                i = ind_end + 1
            
        
        elif arg[i].islower() and arg[i+1].islower():
            error_word = arg[i]+arg[i+1]
            break

        elif arg[i].isdigit():
            if i == 0:
                error_word = 'WFW'
                break
            data[-1] += arg[i]
            i+=1

        else:
            error_word = 'WFW'
            break
    return [data, error_word]

def split_elem(arg: str):
    '''
    Splits the element and its index
    '''

    if len(arg) == 1:
        return arg, 1
    
    elif len(arg) == 2 and arg[1].islower():
        return arg, 1
    
    elif len(arg) == 2 and arg[1].isdigit():
        return arg[0], int(arg[1])
    
    elif len(arg) > 2 and arg[1].islower():
        return arg[0:2], int(arg[2:])
    
    else:
        return arg[0], int(arg[1:])

def count_mass(arg: list, amount = 1) -> int:
    '''
    Count molar mass of the argument
    '''
    res = 0
    for item in arg:
        if type(item) == list:
            res += count_mass(item[:-1], item[-1])
        
        else:
            elem, cnt = split_elem(item)
            res += masses[elem]*cnt
    
    return res*amount

def rounding_masses(n: int) -> dict:
    '''
    Rounds molar mass data, based on the chemical rules
    '''
    res = {}
    for key, value in origin_masses.items():
        if n==0 and key == 'Cl':
            res['Cl'] = 35.5
            continue

        res[key] = round(value, n)
    
    return res

def main_func():
    '''
    Functing, which is launched, 
    when the user presses the button to calculate molar mass.
    Shows the result or an error message.
    '''

    form = ui.formula_entry.text()
    cnt = int(ui.decimal_cb.currentText())
    form = list(form)

    for i in range(form.count('[')):
        form = form.replace('[', '(')

    for i in range(form.count(']')):
        form = form.replace(']', ')')

    for i in range(form.count('{')):
        form = form.replace('{', '(')

    for i in range(form.count('}')):
        form = form.replace('}', ')')

    form = list(form)
    for i in range(len(form)-1):
        if form[i]==')' and form[i+1] == '1':
            form[i+1] = ''
    
    global masses, elems

    masses = rounding_masses(cnt)
    form = ''.join(form)
    elems = list(masses.keys())
    a = split_form(form)

    if a[1]:
        ui.result_label.setText('')
        if a[1] == 'WFW':
            ui.error_label.setText('Error: wrong formula written')

        else:
            ui.error_label.setText(f'Error: element "{a[1]}" does not exist')

    else:
        total_mass = count_mass(a[0])
        ui.error_label.setText('')
        ui.result_label.setText(f'Result: {total_mass}')

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = Ui_main_window()

    with open("masses.json", 'r', encoding='utf-8') as file:
        file_content = file.read()
        origin_masses = json.loads(file_content)

    ui.setupUi(main_window)
    ui.pushButton.clicked.connect(main_func)
    main_window.show()
    sys.exit(app.exec_())