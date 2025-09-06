from sympy import Expr, Poly
import traceback, sys

from circuit import *

circuit = Circuit()

def asExpr(string : str) -> Expr:
    try:
        return Poly(string).as_expr()
    except Exception:
        return Poly(string, gens = sp.symbols("_")).as_expr()

while True:
    try:
        command = input()
        if command == "":
            continue
        command = command.strip().split()

        if command[0].lower() == "setnodes":
            circuit = Circuit(int(command[1]))
        elif command[0].lower() == "addnode":
            print("add", circuit.addNode())
        elif command[0].lower() == "addedge":
            if len(command) == 3:
                circuit.addEdge(int(command[1]), int(command[2]))
            else:
                circuit.addEdge(int(command[1]), int(command[2]), asExpr(command[3]))
        elif command[0].lower() == "setelectrode":
            if len(command) == 3:
                circuit.setElectrode(int(command[1]), int(command[2]))
            elif len(command == 4):
                circuit.setElectrode(int(command[1]), int(command[2]), asExpr(command[3]))
            else:
                circuit.setElectrode(int(command[1]), int(command[2]), asExpr(command[3]), asExpr(command[4]))
        elif command[0].lower() == "solve":
            circuit.solveCircuit()
            print([Node(node.potential.subs(circuit.solveResult)) for node in circuit.nodes])
            print(circuit.fullVoltage)
            print(circuit.fullCurrent)
            print(circuit.fullResistance)
        elif command[0].lower() == "solveresult":
            print([Node(node.potential.subs(circuit.solveResult)) for node in circuit.nodes])
            print(circuit.fullVoltage)
            print(circuit.fullCurrent)
            print(circuit.fullResistance)
        elif command[0].lower() == "quit" or command[0].lower() == "exit":
            break
        else:
            raise ValueError(f"Invalid command: {command}")
    except Exception as e:
        excType, excValue, excTraceback = sys.exc_info()
        filename = excTraceback.tb_frame.f_code.co_filename
        lineno = excTraceback.tb_lineno

        print(f"Error: {e}\n  File \"{filename}\", line {lineno}")
    except KeyboardInterrupt:
        break

"""
Example:

setnodes 8
addedge 0 1 1
addedge 0 3 1
addedge 1 2 1
addedge 1 5 1
addedge 0 4 1
addedge 2 3 1
addedge 2 6 1
addedge 4 7 1
addedge 4 5 1
addedge 5 6 1
addedge 6 7 1
addedge 3 7 1
setelectrode 0 3
solve
solveresult
"""