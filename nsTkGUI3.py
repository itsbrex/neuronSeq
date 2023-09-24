# ... (previous code)
import networkx as nx
import math
import numpy as np
import tkinter as tk
import neuronSeq2 as ns
import threading
import time

running = True   
width, height = 800, 800
zoom_factor = 1.0
pan_offset = [0, 0]
neuronSeq = ns.NeuronSeq()
G = ns.NetworkGraph(neuronSeq)

def print_neuronSeq_nnotes():
    print("Neurons:")
    for nnote in neuronSeq.nnotes:
        print(nnote.id, nnote.channel, nnote.note, nnote.velocity, nnote.duration)
    return

def print_neuronSeq_connections():
    print("Connections:")
    for connection in neuronSeq.connections:
        print(connection.name, connection.source.id + "->" + connection.destination.id, connection.weight_0_to_1, connection.weight_1_to_0)
    return

class AddNeuronWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Neuron")
        self.geometry("300x300")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.master = master
        self.create_widgets()

    def close_window(self):
        self.destroy()

    def create_widgets(self):
        self.neuron_name_label = tk.Label(self, text="Neuron Name")
        self.neuron_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.neuron_name_entry = tk.Entry(self)
        self.neuron_name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.midi_channel_label = tk.Label(self, text="MIDI Channel")
        self.midi_channel_label.grid(row=1, column=0, padx=10, pady=10)
        self.midi_channel_entry = tk.Entry(self)
        self.midi_channel_entry.grid(row=1, column=1, padx=10, pady=10)
        self.midi_note_label = tk.Label(self, text="MIDI Note")
        self.midi_note_label.grid(row=2, column=0, padx=10, pady=10)
        self.midi_note_entry = tk.Entry(self)
        self.midi_note_entry.grid(row=2, column=1, padx=10, pady=10)
        self.velocity_label = tk.Label(self, text="Velocity")
        self.velocity_label.grid(row=3, column=0, padx=10, pady=10)
        self.velocity_entry = tk.Entry(self)
        self.velocity_entry.grid(row=3, column=1, padx=10, pady=10)
        self.duration_label = tk.Label(self, text="Duration")
        self.duration_label.grid(row=4, column=0, padx=10, pady=10)
        self.duration_entry = tk.Entry(self)
        self.duration_entry.grid(row=4, column=1, padx=10, pady=10)
        self.add_button = tk.Button(self, text="Add", command=self.add_neuron)
        self.add_button.grid(row=5, column=0, padx=10, pady=10)
        
    def add_neuron(self):
        global G
        neuron_name = self.neuron_name_entry.get()
        midi_channel = int(self.midi_channel_entry.get())
        midi_note = int(self.midi_note_entry.get())
        velocity = int(self.velocity_entry.get())
        duration = float(self.duration_entry.get())
        note, distance_vector = G.add_nnote(midi_channel=midi_channel, note=midi_note, duration=duration, id=neuron_name, velocity=velocity, lenX=2**16)
        note.set_activation_function(1)
        G.DVpos[note.get_id()] = distance_vector

        nn_conn_str="Neurons:\n"
        for nnote in neuronSeq.nnotes:
            nn_conn_str += str(nnote.id) + ": " + str(nnote.channel) + " " + str(nnote.note) + " " + str(nnote.velocity) + " " + str(nnote.duration) + "\n"
        nn_conn_str += "\nConnections:\n"
        for connection in neuronSeq.connections:
            nn_conn_str += str(connection.name) + ": " + str(connection.source.id) + "->" + str(connection.destination.id) + str(connection.weight_0_to_1)+str(connection.weight_1_to_0)+"\n"
        self.master.nn_conn_label.config(text=nn_conn_str)

        print_neuronSeq_nnotes()
        self.close_window()
        return
    
class AddConnectionWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Connection")
        self.geometry("300x300")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.master = master
        self.create_widgets()

    def close_window(self):
        self.destroy()

    def create_widgets(self):
        connection_name_label = tk.Label(self, text="Connection Name")
        connection_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.connection_name_entry = tk.Entry(self)
        self.connection_name_entry.grid(row=0, column=1, padx=10, pady=10)
        source_label = tk.Label(self, text="Source")
        source_label.grid(row=1, column=0, padx=10, pady=10)
        self.source_entry = tk.Entry(self)
        self.source_entry.grid(row=1, column=1, padx=10, pady=10)
        target_label = tk.Label(self, text="Target")
        target_label.grid(row=2, column=0, padx=10, pady=10)
        self.target_entry = tk.Entry(self)
        self.target_entry.grid(row=2, column=1, padx=10, pady=10)
        self.weight0_label = tk.Label(self, text="Weight 0")
        self.weight0_label.grid(row=3, column=0, padx=10, pady=10)
        self.weight0_entry = tk.Entry(self)
        self.weight0_entry.grid(row=3, column=1, padx=10, pady=10)
        self.weight1_label = tk.Label(self, text="Weight 1")
        self.weight1_label.grid(row=4, column=0, padx=10, pady=10)
        self.weight1_entry = tk.Entry(self)
        self.weight1_entry.grid(row=4, column=1, padx=10, pady=10)
        self.add_connection_button = tk.Button(self, text="Add", command=self.add_connection)
        self.add_connection_button.grid(row=5, column=0, padx=10, pady=10)

    def add_connection(self):
        global G
        connection_name = self.connection_name_entry.get()
        nnotedict = {}
        for nnote in neuronSeq.nnotes:
            nnotedict[nnote.id] = nnote

        source = nnotedict[self.source_entry.get()]
        target = nnotedict[self.target_entry.get()]
        weight0 = float(self.weight0_entry.get())
        weight1 = float(self.weight1_entry.get())
        source_idx = neuronSeq.nnotes.index(source)
        target_idx = neuronSeq.nnotes.index(target)
        connection, distance_vectors = G.add_connection(connection_name, source_idx, target_idx, weight0, weight1)
        G.DVpos[connection.get_id()] = distance_vectors
        print_neuronSeq_connections()
        
        nn_conn_str="Neurons:\n"
        for nnote in neuronSeq.nnotes:
            nn_conn_str += str(nnote.id) + ": " + str(nnote.channel) + " " + str(nnote.note) + " " + str(nnote.velocity) + " " + str(nnote.duration) + "\n"
        nn_conn_str += "\nConnections:\n"
        for connection in neuronSeq.connections:
            nn_conn_str += str(connection.name) + ": " + str(connection.source.id) + "->" + str(connection.destination.id) + str(connection.weight_0_to_1)+" "+str(connection.weight_1_to_0)+"\n"
        self.master.nn_conn_label.config(text=nn_conn_str)
        self.close_window()
        return

def openAddNeuronWindow():
    global addNeuronWindow, neuronSeq_window
    addNeuronWindow=AddNeuronWindow(neuronSeq_window)
    return

def openAddConnectionWindow():
    global addConnectionWindow, neuronSeq_window
    addConnectionWindow=AddConnectionWindow(neuronSeq_window)
    return

class NeuronSeqWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("NeuronSeq")
        self.geometry("1024x800")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.create_widgets()
        self.bind('<Key>', self.key_press)

    def create_widgets(self):
        global openAddNeuronWindow, openAddConnectionWindow, print_neuronSeq_nnotes, print_neuronSeq_connections
        
        self.add_neuron_button = tk.Button(self, text="Add Neuron", command=openAddNeuronWindow)
        self.add_neuron_button.grid(row=0, column=0, padx=10, pady=10)
        self.add_connection_button = tk.Button(self, text="Add Connection", command=openAddConnectionWindow)
        self.add_connection_button.grid(row=1, column=0, padx=10, pady=10)
        self.nn_conn_label = tk.Label(self, text="Add neurons and connections to start.")
        self.nn_conn_label.grid(row=0, column=4, rowspan=3, padx=10, pady=10)
        self.canvas = NetworkCanvas()
        self.canvas.set_edge_color((0, 0, 0))
        return

    def key_press(self, event):
        if event.char == 'w':
            self.canvas.zoom_in()
        elif event.char == 's':
            self.canvas.zoom_out()
        elif event.char == 'a':
            self.canvas.pan_left()
        elif event.char == 'd':
            self.canvas.pan_right()
        elif event.char == 'q':
            self.canvas.pan_up()
        elif event.char == 'e':
            self.canvas.pan_down()
        elif event.char == 'r':
            self.canvas.set_angle(0.1)
        elif event.char == 'f':
            self.canvas.set_angle(-0.1)
        return
    
    def close_window(self):
        global running
        running = False
        global neuronSeq
        neuronSeq.stop()
        time.sleep(0.1)    
        self.destroy()

class NetworkCanvas(tk.Canvas):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height)
        self.zoom_factor = 1.0
        self.pan_offset = [0, 0]

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.update_canvas()

    def zoom_out(self):
        self.zoom_factor -= 0.1
        self.update_canvas()

    def pan_left(self):
        self.pan_offset[0] -= 20
        self.update_canvas()

    def pan_right(self):
        self.pan_offset[0] += 20
        self.update_canvas()

    def pan_up(self):
        self.pan_offset[1] -= 20
        self.update_canvas()

    def pan_down(self):
        self.pan_offset[1] += 20
        self.update_canvas()

    def set_angle(self, angle):
        global G
        G.rotate(angle)
        self.update_canvas()

    def set_edge_color(self, edge_color):
        tk_rgb = "#%02x%02x%02x" % edge_color
        self.edge_color = tk_rgb

    def update_canvas(self):
        zoom_factor = self.zoom_factor
        pan_offset = self.pan_offset
        global width, height
        global G
        self.delete('all')
        for connection in neuronSeq.connections:
            source = connection.source
            target = connection.destination
            source_pos = G.DVpos[source.get_id()]
            target_pos = G.DVpos[target.get_id()]
            source_x = source_pos.get_coordinates()[0] * zoom_factor + pan_offset[0]
            source_y = source_pos.get_coordinates()[1] * zoom_factor + pan_offset[1]
            target_x = target_pos.get_coordinates()[0] * zoom_factor + pan_offset[0]
            target_y = target_pos.get_coordinates()[1] * zoom_factor + pan_offset[1]

            self.create_line(source_x, source_y, target_x, target_y, fill=self.edge_color)
            self.create_text(source_x, source_y, text=source.get_id())
            self.create_text(target_x, target_y, text=target.get_id())

        for nnote in neuronSeq.nnotes:
            pos = G.DVpos[nnote.get_id()]
            x = pos.get_coordinates()[0] * zoom_factor + pan_offset[0]
            y = pos.get_coordinates()[1] * zoom_factor + pan_offset[1]
            self.create_oval(x-5, y-5, x+5, y+5, fill="red")
        self.update()
        return


class NeuronSeqWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("NeuronSeq")
        self.geometry("1024x800")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.create_widgets()
        self.bind('<Key>', self.key_press)

    def create_widgets(self):
        global openAddNeuronWindow, openAddConnectionWindow, print_neuronSeq_nnotes, print_neuronSeq_connections
        
        self.add_neuron_button = tk.Button(self, text="Add Neuron", command=openAddNeuronWindow)
        self.add_neuron_button.grid(row=0, column=0, padx=10, pady=10)
        self.add_connection_button = tk.Button(self, text="Add Connection", command=openAddConnectionWindow)
        self.add_connection_button.grid(row=1, column=0, padx=10, pady=10)
        self.nn_conn_label = tk.Label(self, text="Add neurons and connections to start.")
        self.nn_conn_label.grid(row=0, column=4, rowspan=3, padx=10, pady=10)
        self.network_canvas = NetworkCanvas(self, width=800, height=800)
        self.network_canvas.grid(row=4, column=0, columnspan=8, padx=10, pady=10)

    def key_press(self, event):
        # Handle key presses for zoom and pan
        # Update the canvas based on key presses
        if event.char == 'w':
            self.network_canvas.zoom_in()
        elif event.char == 's':
            self.network_canvas.zoom_out()
        elif event.char == 'a':
            self.network_canvas.pan_left()
        elif event.char == 'd':
            self.network_canvas.pan_right()
        elif event.char == 'q':
            self.network_canvas.pan_up()
        elif event.char == 'e':
            self.network_canvas.pan_down()
        elif event.char == 'r':
            self.network_canvas.set_angle(0.1)
        elif event.char == 'f':
            self.network_canvas.set_angle(-0.1)
        return
    

    def close_window(self):
        global running
        running = False
        global neuronSeq
        neuronSeq.stop()
        time.sleep(0.1)
        self.destroy()

class NetworkRunner:
    def __init__(self, neuronSeq_window):
        global width, height
        global G
        global zoom_factor, pan_offset
        self.neuronSeq_window = neuronSeq_window
        self.canvas = neuronSeq_window.network_canvas

    def update(self):
        global running
        global width, height
        global G
        global zoom_factor, pan_offset

        if running:
            random_rgb = np.random.randint(0, 255, 3)
            self.canvas.set_edge_color(tuple(random_rgb))
            self.canvas.update_canvas()
            self.neuronSeq_window.after(10, self.update)
        return




# Initial values for zoom and pan
zoom_factor = 1.0
pan_offset = [0, 0]

neuronSeq_window = NeuronSeqWindow()
network_runner = NetworkRunner(neuronSeq_window)
network_runner.update()
neuronSeq_window.mainloop()
