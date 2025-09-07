import tkinter as tk
from tkinter import simpledialog

from utils.expr import *
from circuit import *

class PointLineEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("CircuitAnalyzer")
        self.root.geometry("800x600")

        self.current_mode = None
        self.drag_data = {"item": None, "x": 0, "y": 0}
        self.temp_line_start = None
        self.points = []
        self.lines = []
        self.anode = None
        self.cathode = None
        self.electrode_mode = False
        self.electrode_symbols = []
        self.point_counter = 1
        self.point_id_to_num = {}
        self.point_id_to_label = {}

        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_point = tk.Button(
            toolbar_frame, text="Generate Node", width=15,
            command=self.toggle_point_mode
        )
        self.btn_point.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_line = tk.Button(
            toolbar_frame, text="Generate Edge", width=15,
            command=self.toggle_line_mode
        )
        self.btn_line.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_electrode = tk.Button(
            toolbar_frame, text="Set Electrode", width=15,
            command=self.toggle_electrode_mode
        )
        self.btn_electrode.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_analyze = tk.Button(
            toolbar_frame, text="Analyze", width=15,
            command=self.analyze
        )
        self.btn_analyze.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_console = tk.Button(
            toolbar_frame, text="Console", width=15,
            command=self.console_text
        )
        self.btn_console.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.canvas = tk.Canvas(
            self.root, bg="white", 
            width=800, height=550
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        self.status = tk.StringVar()
        self.status.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def console_text(self):
        cmd = simpledialog.askstring("控制台", "输入指令：", parent=self.root)
        if cmd is not None:
            exec(cmd)
    
    def create_line(self, start_point, end_point):
        start_coords = self.canvas.coords(start_point)
        end_coords = self.canvas.coords(end_point)
        
        start_x = (start_coords[0] + start_coords[2]) / 2
        start_y = (start_coords[1] + start_coords[3]) / 2
        end_x = (end_coords[0] + end_coords[2]) / 2
        end_y = (end_coords[1] + end_coords[3]) / 2
        
        line = self.canvas.create_line(
            start_x, start_y, end_x, end_y, 
            width=3, fill="black", tags=("line", "deletable")
        )
        
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        label = simpledialog.askstring("Resistance", "Input Resistance (Default: 0):", parent=self.root).strip()
        if label is None or label == "": 
            label = "0"
        
        label_id = self.canvas.create_text(
            mid_x, mid_y, 
            text="" if label == "0" else label, 
            fill="blue", 
            font=("Arial", 15),
            tags=("line_label", "deletable")
        )
        
        self.lines.append({
            "id": line,
            "start": start_point,
            "end": end_point,
            "label": label,
            "label_id": label_id
        })
        
        return line
        
    def update_line_position(self, line_id):
        line_info = next((line for line in self.lines if line["id"] == line_id), None)
        if line_info:
            start_coords = self.canvas.coords(line_info["start"])
            end_coords = self.canvas.coords(line_info["end"])
            
            start_x = (start_coords[0] + start_coords[2]) / 2
            start_y = (start_coords[1] + start_coords[3]) / 2
            end_x = (end_coords[0] + end_coords[2]) / 2
            end_y = (end_coords[1] + end_coords[3]) / 2
            
            self.canvas.coords(line_id, start_x, start_y, end_x, end_y)
            
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            self.canvas.coords(line_info["label_id"], mid_x, mid_y)
    
    def delete_item(self, item_id):
        if "line_label" in self.canvas.gettags(item_id):
            for line_info in self.lines:
                if line_info["label_id"] == item_id:
                    self.canvas.delete(line_info["id"])
                    self.canvas.delete(item_id)
                    self.lines.remove(line_info)
                    return
        
        if "line" in self.canvas.gettags(item_id):
            line_info = next((line for line in self.lines if line["id"] == item_id), None)
            if line_info:
                self.canvas.delete(line_info["label_id"])
                self.lines.remove(line_info)

        if item_id in (self.anode, self.cathode):
            if item_id == self.anode and self.cathode:
                self.canvas.itemconfig(self.cathode, fill="black")
            elif item_id == self.cathode and self.anode:
                self.canvas.itemconfig(self.anode, fill="black")
            self.remove_electrode_symbols()
            self.anode = None
            self.cathode = None
            self.electrode_mode = False
            self.btn_electrode.config(relief=tk.RAISED)
            self.status.set("Deleted")
        
        if "point" in self.canvas.gettags(item_id):
            lines_to_delete = [line for line in self.lines 
                             if line["start"] == item_id or line["end"] == item_id]
            
            for line in lines_to_delete:
                self.canvas.delete(line["label_id"])
                self.canvas.delete(line["id"])
                self.lines.remove(line)
            
            if item_id in self.points:
                self.points.remove(item_id)
            if item_id in self.point_id_to_label:
                label_id = self.point_id_to_label[item_id]
                self.canvas.delete(label_id)
                del self.point_id_to_label[item_id]
        
        self.canvas.delete(item_id)
    
    def toggle_electrode_mode(self):
        if self.anode or self.cathode:
            self.remove_electrode_symbols()
            if self.anode: 
                self.canvas.itemconfig(self.anode, fill="black")
            if self.cathode:
                self.canvas.itemconfig(self.cathode, fill="black")
            self.anode = None
            self.cathode = None
            self.btn_electrode.config(relief=tk.RAISED)

        self.cancel_mode()
        self.electrode_mode = True
        self.temp_electrode_start = None
        self.btn_electrode.config(relief=tk.SUNKEN)
        self.status.set("Select electrode")
    
    def cancel_electrode_mode(self):
        if self.electrode_mode:
            if self.anode: 
                self.canvas.itemconfig(self.anode, fill="black")
            if self.cathode:
                self.canvas.itemconfig(self.cathode, fill="black")
            self.remove_electrode_symbols()
            self.anode = None
            self.cathode = None
            self.anode_potential = None
            self.cathode_potential = None
            self.electrode_mode = False
            self.btn_electrode.config(relief=tk.RAISED)
    
    def remove_electrode_symbols(self):
        for symbol in self.electrode_symbols:
            self.canvas.delete(symbol)
        self.electrode_symbols = []
    
    def mark_electrode(self, point_id, symbol, potential):
        coords = self.canvas.coords(point_id)
        x_center = (coords[0] + coords[2]) / 2
        y_top = coords[1] - 15
        
        color = "red" if symbol == "+" else "blue"
        
        symbol_id = self.canvas.create_text(
            x_center, y_top,
            text=f"{symbol} ({potential})", font=("Arial", 12, "bold"),
            fill=color, tags="electrode_symbol"
        )

        self.electrode_symbols.append(symbol_id)
    
    def toggle_point_mode(self):
        if self.current_mode == "point":
            self.cancel_mode()
        else:
            self.set_mode("point")
            self.cancel_electrode_mode()
    
    def toggle_line_mode(self):
        if self.current_mode == "line":
            self.cancel_mode()
        else:
            self.set_mode("line")
            self.cancel_electrode_mode()
    
    def set_mode(self, mode):
        if self.current_mode == "line" and self.temp_line_start:
            self.canvas.itemconfig(self.temp_line_start, fill="black")
            self.temp_line_start = None
        
        self.current_mode = mode
        self.btn_point.config(relief=tk.SUNKEN if mode == "point" else tk.RAISED)
        self.btn_line.config(relief=tk.SUNKEN if mode == "line" else tk.RAISED)

        if mode == "point":
            self.status.set("Create node - Click to place node on canvas")
        elif mode == "line":
            self.status.set("Create edge - Select two nodes to connect")

    def cancel_mode(self):
        if self.current_mode == "line" and self.temp_line_start:
            self.canvas.itemconfig(self.temp_line_start, fill="black")

        self.current_mode = None
        self.temp_line_start = None
        self.status.set("Ready")
        self.btn_point.config(relief=tk.RAISED)
        self.btn_line.config(relief=tk.RAISED)

    def on_canvas_click(self, event):
        x, y = event.x, event.y

        if self.electrode_mode:
            clicked_point = None
            for point in self.points:
                coords = self.canvas.coords(point)
                if (coords[0] <= x <= coords[2] and
                    coords[1] <= y <= coords[3]):
                    clicked_point = point
                    break

            if clicked_point:
                if self.temp_electrode_start is None:
                    self.temp_electrode_start = clicked_point
                    self.anode = clicked_point
                    self.canvas.itemconfig(clicked_point, fill="red")
                    potential = simpledialog.askstring("Potential", "Input potential (Default: U0):", parent=self.root).strip()
                    if potential is None or potential == "":
                        potential = "U0"
                    self.anode_potential = potential
                    self.status.set("Select electrode")
                else:
                    if clicked_point == self.temp_electrode_start:
                        pass
                    else:
                        self.cathode = clicked_point
                        self.canvas.itemconfig(clicked_point, fill="blue")
                        potential = simpledialog.askstring("Potential", "Input potential (Default: 0):", parent=self.root).strip()
                        if potential is None or potential == "":
                            potential = "0"
                        self.cathode_potential = potential
                        self.remove_electrode_symbols()
                        self.mark_electrode(self.anode, "+", self.anode_potential)
                        self.mark_electrode(self.cathode, "-", self.cathode_potential)
                        self.status.set("Electrode setted")
                        self.btn_electrode.config(relief=tk.RAISED)
                        self.electrode_mode = False
            else:
                self.status.set("Select electrode")
                return

        if self.current_mode is None:
            for point in self.points:
                coords = self.canvas.coords(point)
                if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                    self.drag_data["item"] = point
                    self.drag_data["x"] = x
                    self.drag_data["y"] = y
                    return

        if self.current_mode == "point":
            self.create_point(x, y)

        elif self.current_mode == "line":
            clicked_point = None
            for point in self.points:
                coords = self.canvas.coords(point)
                if (coords[0] <= x <= coords[2] and
                    coords[1] <= y <= coords[3]):
                    clicked_point = point
                    break

            if clicked_point:
                if not self.temp_line_start:
                    self.temp_line_start = clicked_point
                    self.canvas.itemconfig(clicked_point, fill="green")
                else:
                    if self.anode == self.temp_line_start:
                        self.canvas.itemconfig(self.temp_line_start, fill="red")
                    elif self.cathode == self.temp_line_start:
                        self.canvas.itemconfig(self.temp_line_start, fill="blue")
                    else:
                        self.canvas.itemconfig(self.temp_line_start, fill="black")
                    self.create_line(self.temp_line_start, clicked_point)
                    self.temp_line_start = None

    def create_point(self, x, y):
        point_id = self.canvas.create_oval(
            x-5, y-5, x+5, y+5,
            fill="black", outline="black", width=1,
            tags=("point", "draggable", "deletable")
        )
        self.points.append(point_id)

        point_num = self.point_counter
        self.point_counter += 1
        self.point_id_to_num[point_id] = point_num

        text_id = self.canvas.create_text(x, y+15, text=str(point_num),
                                            tags=("point_label", "deletable"))
        self.point_id_to_label[point_id] = text_id
        return point_id

    def get_nodes(self):
        return [self.point_id_to_num[point] for point in self.points]

    def get_line_relationships(self):
        relationships = []
        for line in self.lines:
            start_id = line["start"]
            end_id = line["end"]
            label = line["label"]
            
            if start_id in self.point_id_to_num and end_id in self.point_id_to_num:
                start_num = self.point_id_to_num[start_id]
                end_num = self.point_id_to_num[end_id]
                relationships.append((start_num, end_num, label))
        return relationships
    
    def on_drag(self, event):
        item = self.drag_data["item"]
        if item and "draggable" in self.canvas.gettags(item):
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            self.canvas.move(item, dx, dy)
            self.update_connected_lines(item)
            
            if self.anode == item or self.cathode == item:
                self.remove_electrode_symbols()
                if self.anode:
                    self.mark_electrode(self.anode, "+", self.anode_potential)
                if self.cathode:
                    self.mark_electrode(self.cathode, "-", self.cathode_potential)
            
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            if item in self.point_id_to_label:
                label_id = self.point_id_to_label[item]
                self.canvas.move(label_id, dx, dy)
    
    def on_drag_end(self, event):
        self.drag_data["item"] = None
    
    def on_right_click(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        for item in items:
            tags = self.canvas.gettags(item)
            if "deletable" in tags:
                self.delete_item(item)
                self.status.set("Deleted")
                return
    
    def update_connected_lines(self, point):
        for line_info in self.lines:
            if line_info["start"] == point or line_info["end"] == point:
                self.update_line_position(line_info["id"])

    def analyze(self):
        nodes = self.get_nodes()
        nodes_map = {nodes[i] : i for i in range(len(nodes))}
        edges = self.get_line_relationships()

        circuit = Circuit(len(nodes))

        circuit.setElectrode(nodes_map[self.point_id_to_num[self.anode]], nodes_map[self.point_id_to_num[self.cathode]], asExpr(self.anode_potential), asExpr(self.cathode_potential))

        for edge in edges:
            circuit.addEdge(nodes_map[edge[0]], nodes_map[edge[1]], asExpr(edge[2]))

        circuit.solveCircuit()
        print([Node(sp.simplify(node.potential.subs(circuit.solveResult))) for node in circuit.nodes])
        print(circuit.fullVoltage)
        print(circuit.fullCurrent)
        print(circuit.fullResistance)

        self.status.set("Analyze finished")

        root = tk.Tk()
        root.title("Analyze result")
        root.geometry("500x400")

        label = tk.Label(root, text = f"Total voltage = {circuit.fullVoltage}\nTotal current = {circuit.fullCurrent}\nTotal resistance = {circuit.fullResistance}")
        label.pack(pady = 20)

        entry = tk.Entry(root, width=40)
        entry.pack(pady=10)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        def getPotential():
            text = entry.get()
            if not text:
                return
            potential = sp.simplify(circuit.nodes[nodes_map[int(text)]].potential.subs(circuit.solveResult))
            tk.messagebox.showinfo(f"Potential: {text}", f"Potential of Node {text} = {potential}")

        def getVoltage():
            text = entry.get().split(",")
            assert(len(text) == 2)
            edge = (nodes_map[int(text[0])], nodes_map[int(text[1])])
            if edge not in circuit.edges:
                raise ValueError(f"Edge {edge} does not exist")
            voltage = sp.simplify(circuit.edges[edge].voltage.subs(circuit.solveResult))
            tk.messagebox.showinfo(f"Voltage: {(int(text[0]), int(text[1]))}", f"Voltage of Edge {(int(text[0]), int(text[1]))} = {voltage}")

        def getCurrent():
            text = entry.get().split(",")
            assert(len(text) == 2)
            edge = (nodes_map[int(text[0])], nodes_map[int(text[1])])
            if edge not in circuit.edges:
                raise ValueError(f"Edge {edge} does not exist")
            current = sp.simplify(circuit.edges[edge].current.subs(circuit.solveResult))
            tk.messagebox.showinfo(f"Current: {(int(text[0]), int(text[1]))}", f"Current of Edge {(int(text[0]), int(text[1]))} = {current}")

        def exit_tk():
            root.destroy()

        tk.Button(button_frame, text = "Get potential", command = getPotential).pack(side = tk.LEFT, padx = 10)
        tk.Button(button_frame, text = "Get voltage (u, v)", command = getVoltage).pack(side = tk.LEFT, padx = 10)
        tk.Button(button_frame, text = "Get current (u, v)", command = getCurrent).pack(side = tk.LEFT, padx = 10)
        tk.Button(button_frame, text = "Exit", command = exit_tk).pack(side=tk.LEFT, padx=10)

        root.mainloop()

root = tk.Tk()
app = PointLineEditor(root)
root.mainloop()