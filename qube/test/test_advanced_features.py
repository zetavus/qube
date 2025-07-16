import pytest
import sys
import os

# Add the parent directory to the path so we can import qube
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qube.interpreter import QubeInterpreter
from qube.lexer import QubeLexer, TokenType
from qube.parser import QubeParser

class TestAdvancedFeatures:
    def setup_method(self):
        self.interpreter = QubeInterpreter()
    
    def test_match_statement(self):
        code = """
        fn main() {
            scalar x = 5;
            scalar result = match x {
                0 => "zero",
                1 => "one",
                _ => "other",
            };
            println(result);
        }
        """
        # Should not raise an exception
        self.interpreter.run(code)
    
    def test_loop_with_break(self):
        code = """
        fn main() {
            scalar count = 0;
            loop {
                count = count + 1;
                if count > 5 {
                    break;
                }
            }
            println("Final count:", count);
        }
        """
        self.interpreter.run(code)
    
    def test_quantum_if(self):
        code = """
        fn main() {
            qubit q = |+⟩;
            quantum if measure(q) == 1 {
                println("Measured 1");
            } else {
                println("Measured 0");
            }
        }
        """
        self.interpreter.run(code)
    
    def test_high_order_functions(self):
        code = """
        fn square(x: i32) -> i32 {
            return x * x;
        }
        
        fn main() {
            scalar numbers = [1, 2, 3, 4, 5];
            scalar squared = map(square, numbers);
            println("Squared:", squared);
        }
        """
        self.interpreter.run(code)
    
    def test_quantum_gates_extended(self):
        code = """
        fn main() {
            qubit q = |0⟩;
            
            q = H(q);
            println("After H:", q);
            
            q = RY(1.5708, q);  // π/2
            println("After RY(π/2):", q);
            
            q = RZ(0.7854, q);  // π/4
            println("After RZ(π/4):", q);
            
            bit result = measure(q);
            println("Measurement:", result);
        }
        """
        self.interpreter.run(code)
    
    def test_bell_state_creation(self):
        code = """
        fn main() {
            qubit q1 = |0⟩;
            qubit q2 = |0⟩;
            
            qubit bell = CNOT(H(q1), q2);
            println("Bell state:", bell);
            
            scalar ent = entanglement(bell);
            println("Entanglement measure:", ent);
        }
        """
        self.interpreter.run(code)
    
    def test_complex_numbers(self):
        code = """
        fn main() {
            scalar z1 = 3.0 + 4.0i;
            scalar z2 = 1.0 - 2.0i;
            
            scalar sum = z1 + z2;
            scalar product = z1 * z2;
            
            println("z1 =", z1);
            println("z2 =", z2);
            println("Sum =", sum);
            println("Product =", product);
        }
        """
        self.interpreter.run(code)
    
    def test_quantum_fidelity(self):
        code = """
        fn main() {
            qubit state1 = |0⟩;
            qubit state2 = |1⟩;
            qubit state3 = |0⟩;
            
            scalar fid1 = fidelity(state1, state2);
            scalar fid2 = fidelity(state1, state3);
            
            println("Fidelity |0⟩ and |1⟩:", fid1);
            println("Fidelity |0⟩ and |0⟩:", fid2);
        }
        """
        self.interpreter.run(code)

if __name__ == "__main__":
    pytest.main([__file__])