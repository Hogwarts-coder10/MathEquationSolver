from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

class MathEquationSolver(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Math Equation Solver")
        self.setGeometry(100, 100, 900, 650)
        self.setStyleSheet(self.load_styles())  # Apply custom dark theme

        # Layout
        self.layout = QVBoxLayout()

        # Equation Type Dropdown
        self.equation_type_label = QLabel("Equation Type:")
        self.equation_type_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.layout.addWidget(self.equation_type_label)

        self.equation_type_combo = QComboBox()
        self.equation_type_combo.addItems(["Algebraic Equation", "Differentiation", "Integration", "System of Equations"])
        self.layout.addWidget(self.equation_type_combo)

        # Equation Input
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("Enter equation(s), e.g., x + y = 5, x - y = 1")
        self.layout.addWidget(self.equation_input)

        # Solve Button
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve_equation)
        self.layout.addWidget(self.solve_button)

        # Solution Display
        self.solution_label = QLabel("Solution:")
        self.solution_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.layout.addWidget(self.solution_label)

        self.solution_output = QTextEdit()
        self.solution_output.setReadOnly(True)
        self.layout.addWidget(self.solution_output)

        # Matplotlib Graph
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

    def load_styles(self):
        """Load custom stylesheet for a modern dark theme."""
        return """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #3E3E3E;
                border: 1px solid #555555;
                padding: 5px;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QComboBox {
                background-color: #3E3E3E;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
            }
        """

    def solve_equation(self):
        eq_type = self.equation_type_combo.currentText()
        equation_str = self.equation_input.text().strip()

        if not equation_str:
            self.solution_output.setText("Please enter an equation.")
            return

        try:
            x = sp.Symbol('x')  # Single-variable equations only
            expr = sp.sympify(equation_str, evaluate=True)

            if eq_type == "Algebraic Equation":
                solutions = sp.solve(expr, x)
                formatted_solutions = self.format_step_solution(solutions)
                self.plot_graph(expr)

            elif eq_type == "Differentiation":
                derivative = sp.diff(expr, x)
                formatted_solutions = f"f'(x) = {derivative}"
                self.plot_graph(expr)

            elif eq_type == "Integration":
                integral = sp.integrate(expr, x)
                formatted_solutions = f"∫f(x) dx = {integral} + C"
                self.plot_graph(expr)

            elif eq_type == "System of Equations":
                formatted_solutions = self.solve_system(equation_str)  # Call system solver without graphing

            else:
                formatted_solutions = "Invalid selection."

            self.solution_output.setText(formatted_solutions)

        except Exception as e:
            self.solution_output.setText(f"Error: {e}")

    def format_step_solution(self, solutions):
        """Format solutions for display."""
        formatted = "Solutions:\n"
        for i, sol in enumerate(solutions):
            formatted += f"x{i+1} = {sol}     "
        return formatted

    def plot_graph(self, expr):
        """Plots the function with improved styling."""
        self.ax.clear()
        x_vals = np.linspace(-10, 10, 400)
        x_sym = sp.Symbol('x')

        try:
            f_lambdified = sp.lambdify(x_sym, expr, "numpy")
            y_vals = f_lambdified(x_vals)
            self.ax.plot(x_vals, y_vals, label=str(expr), color="cyan", linewidth=2)

        except TypeError:
            self.solution_output.setText("Error: Unable to plot the function. Please enter a valid equation.")
            return

        self.ax.axhline(0, color='white', linewidth=0.5)
        self.ax.axvline(0, color='white', linewidth=0.5)
        self.ax.set_xlabel("X-axis", color="white")
        self.ax.set_ylabel("Y-axis", color="white")
        self.ax.legend()
        self.ax.grid(color='gray')
        self.canvas.draw()

    def solve_system(self, equation_str):
        """Solves a system of equations and returns only the solutions (no graphing)."""
        try:
            equations = []
            variables = set()

            # Parse the input equations
            for eq in equation_str.split(','):
                eq = eq.strip()
                if '=' in eq:
                    left, right = eq.split('=')
                    eq = f"({left}) - ({right})"
                expr = sp.sympify(eq)
                equations.append(expr)
                variables.update(expr.free_symbols)

            variables = sorted(variables, key=lambda v: v.name)  # Sort variables (x, y, z)
            solutions = sp.linsolve(equations, *variables)

            if not solutions:
                return "No solution found."

            # Extract numerical solutions
            solution_list = list(solutions)
            if len(solution_list) == 0:
                return "No unique solution."

            numeric_solutions = [sol.evalf() for sol in solution_list[0]]  # Convert to float
            formatted_solutions = "     ".join(f"{var} = {sol}" for var, sol in zip(variables, numeric_solutions))

            return formatted_solutions
        except Exception as e:
            return f"Error solving system: {e}"

if __name__ == "__main__":
    app = QApplication([])
    window = MathEquationSolver()
    window.show()
    app.exec_()
