import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
import socket
#practical 1
class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator (RPC Client)")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # RPC Configuration
        self.rpc_mode = tk.BooleanVar(value=False)
        self.server_address = ('localhost', 12345)
        
        # Calculator State
        self.current_input = tk.StringVar()
        self.history = []
        self.is_radians = True
        
        # Create UI Components
        self.create_display_frame()
        self.create_mode_toggle()
        self.create_buttons_frame()
        
        # Start with calculator view
        self.show_calculator()

    def create_display_frame(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.history_label = ttk.Label(frame, text="", anchor=tk.E)
        self.history_label.pack(fill=tk.X)
        
        self.entry = ttk.Entry(frame, textvariable=self.current_input, 
                             font=('Helvetica', 24), justify=tk.RIGHT, state='readonly')
        self.entry.pack(fill=tk.X, ipady=10)

    def create_mode_toggle(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=5, fill=tk.X)
        ttk.Checkbutton(frame, text="Remote Mode", variable=self.rpc_mode).pack(side=tk.LEFT)

    def create_buttons_frame(self):
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Updated button layout with expanded "=" and "Hist" buttons
        buttons = [
            ('⌫', 'CE', 'C', '±', '(', ')', 'π', 'e'),
            ('sin', 'cos', 'tan', 'x²', 'x^y', '10^x', 'e^x', '√'),
            ('7', '8', '9', '/', 'sinh', 'cosh', 'tanh', 'mod'),
            ('4', '5', '6', '*', 'log', 'deg', 'rad', 'hex'),
            ('1', '2', '3', '-', 'Hist', 'Hist', 'bin', 'bin'),  # Expanded Hist button
            ('0', '.', '=', '=', '=', '=', '+', '+')  # Expanded = button
        ]
        
        # Special column spans for expanded buttons
        special_spans = {
            (4, 4): 2,  # Hist button spans 2 columns
            (4, 6): 2,  # bin button spans 2 columns
            (5, 2): 4,  # = button spans 4 columns
            (5, 6): 2   # + button spans 2 columns
        }
        
        # Create buttons in grid layout
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                # Skip duplicate buttons (they'll be covered by column spans)
                if (i,j) in [(4,5), (4,7), (5,3), (5,4), (5,5), (5,7)]:
                    continue
                    
                btn = ttk.Button(self.buttons_frame, text=text, 
                               command=lambda t=text: self.on_button_click(t))
                
                # Apply column span for special buttons
                span = special_spans.get((i,j), 1)
                btn.grid(row=i, column=j, columnspan=span, sticky='nsew', padx=2, pady=2)
                
                # Configure column weights
                for col in range(j, j+span):
                    self.buttons_frame.grid_columnconfigure(col, weight=1)
            
            self.buttons_frame.grid_rowconfigure(i, weight=1)

    def show_calculator(self):
        self.buttons_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def remote_calculate(self, operation, num1, num2):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(2.0)
                message = f"{operation},{num1},{num2}"
                sock.sendto(message.encode(), self.server_address)
                result, _ = sock.recvfrom(1024)
                return result.decode()
        except Exception as e:
            return f"RPC Error: {str(e)}"

    def calculate_expression(self, expression):
        if self.rpc_mode.get():
            # Try to handle basic operations via RPC
            for op, name in [('+', 'add'), ('-', 'subtract'), ('*', 'multiply'), ('/', 'divide')]:
                if op in expression:
                    parts = expression.split(op)
                    if len(parts) == 2:
                        try:
                            num1, num2 = float(parts[0]), float(parts[1])
                            return self.remote_calculate(name, num1, num2)
                        except ValueError:
                            break
        
        # Fallback to local calculation for complex operations
        try:
            expr = expression.replace('^', '**').replace('π', str(math.pi)).replace('e', str(math.e))
            
            # Handle trigonometric functions
            for func in ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh']:
                expr = re.sub(rf'{func}\(([^)]+)\)', rf'math.{func}(\1)', expr)
            
            # Handle logarithms and roots
            expr = expr.replace('log(', 'math.log10(')
            expr = expr.replace('√(', 'math.sqrt(')
            
            # Handle angle mode
            if not self.is_radians:
                expr = re.sub(r'math\.(sin|cos|tan)\(([^)]+)\)', 
                             r'math.\1(math.radians(\2))', expr)
            
            return str(eval(expr))
        except Exception as e:
            return f"Error: {str(e)}"

    def on_button_click(self, button_text):
        current = self.current_input.get()
        
        if button_text in '0123456789':
            self.current_input.set(current + button_text)
        
        elif button_text in '+-*/^':
            if current and current[-1] not in '+-*/^':
                self.current_input.set(current + button_text)
        
        elif button_text == '.':
            if '.' not in current.split()[-1]:
                self.current_input.set(current + button_text)
        
        elif button_text == '⌫':
            self.current_input.set(current[:-1])
        
        elif button_text == 'CE':
            self.current_input.set('')
        
        elif button_text == 'C':
            self.current_input.set('')
            self.history_label.config(text='')
        
        elif button_text == '±':
            if current.startswith('-'):
                self.current_input.set(current[1:])
            elif current:
                self.current_input.set('-' + current)
        
        elif button_text == '=':
            result = self.calculate_expression(current)
            self.history.append(f"{current} = {result}")
            self.history_label.config(text="\n".join(self.history[-3:]))
            self.current_input.set(str(result))
        
        elif button_text == 'Hist':
            history = "\n".join(self.history[-10:]) if self.history else "No history yet"
            messagebox.showinfo("Calculation History", history)
        
        elif button_text == 'deg':
            self.is_radians = False
            messagebox.showinfo("Mode", "Angle mode set to Degrees")
        
        elif button_text == 'rad':
            self.is_radians = True
            messagebox.showinfo("Mode", "Angle mode set to Radians")
        
        elif button_text in ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh', 'log']:
            self.current_input.set(current + f"{button_text}(")
        
        elif button_text in ['x²', 'x^y', '10^x', 'e^x', '√', 'mod']:
            if button_text == 'x²':
                self.current_input.set(current + '^2')
            elif button_text == 'x^y':
                self.current_input.set(current + '^')
            elif button_text == '10^x':
                self.current_input.set(current + '10^')
            elif button_text == 'e^x':
                self.current_input.set(current + 'e^')
            elif button_text == '√':
                self.current_input.set(current + '√(')
            elif button_text == 'mod':
                self.current_input.set(current + 'mod')
        
        elif button_text in ['π', 'e']:
            self.current_input.set(current + button_text)
        
        elif button_text in ['(', ')']:
            self.current_input.set(current + button_text)
        
        elif button_text in ['hex', 'bin']:
            try:
                num = int(float(current))
                if button_text == 'hex':
                    self.current_input.set(hex(num))
                else:
                    self.current_input.set(bin(num))
            except:
                messagebox.showerror("Error", "Invalid number for conversion")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()