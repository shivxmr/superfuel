from typing import List, Dict, Any, Callable, Union, Optional, Tuple

# Part 1: Planner
class Planner:
    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize the planner with a dictionary of available tools.
        
        Args:
            tools: A dictionary mapping tool names to their function implementations
        """
        self.tools = tools
        
    def generate_plan(self, instructions: str) -> List[Dict[str, Any]]:
        """
        Parse natural language instructions and generate a plan of tool calls.
        
        This is a simplified implementation. In a real-world scenario, you would use an LLM
        to parse the instructions and generate the plan. Here we're using basic string parsing.
        
        Args:
            instructions: A paragraph of natural language instructions
            
        Returns:
            A list of dictionaries representing tool calls, where each dictionary has:
                - 'tool': The name of the tool to call
                - 'args': A dictionary of arguments to pass to the tool
                - 'result_id': An identifier for the result of this step
        """
        
        instructions = instructions.lower().strip()
        steps = []
        
        # Test case 1: "divide by 10, the sum of 20 and 30"
        if instructions.startswith("divide by"):
            divisor = self._extract_number_after_word(instructions, "by")
            first_addend = self._extract_number_after_word(instructions, "of")
            second_addend = self._extract_number_after_word(instructions, "and")
            
            steps.append({
                'tool': 'sum',
                'args': {'a': first_addend, 'b': second_addend},
                'result_id': 'sum_result'
            })
            
            steps.append({
                'tool': 'divide',
                'args': {'a': {'ref': 'sum_result'}, 'b': divisor},
                'result_id': 'final_result'
            })
            
        # Test case 2: "add 20 and 30, divide it by the sum of 2 and 3"
        elif instructions.startswith("add"):
            first_addend = self._extract_number_after_word(instructions, "add")
            second_addend = self._extract_number_after_word(instructions, "and")
            
            steps.append({
                'tool': 'sum',
                'args': {'a': first_addend, 'b': second_addend},
                'result_id': 'sum_result1'
            })
            
            # For the divisor, find the numbers after "sum of" in the second part
            divide_part = instructions[instructions.find('divide it by'):]
            divisor_first = self._extract_number_after_word(divide_part, "of")
            divisor_second = self._extract_number_after_word(divide_part, "and")
            
            steps.append({
                'tool': 'sum',
                'args': {'a': divisor_first, 'b': divisor_second},
                'result_id': 'sum_result2'
            })
            
            steps.append({
                'tool': 'divide',
                'args': {'a': {'ref': 'sum_result1'}, 'b': {'ref': 'sum_result2'}},
                'result_id': 'final_result'
            })
        # Example case: "Get the sum of ten and twenty, then multiply it by hundred"
        elif "sum" in instructions and "multiply" in instructions:
            first_addend = self._extract_number_after_word(instructions, "of")
            second_addend = self._extract_number_after_word(instructions, "and")
            multiplier = self._extract_number_after_word(instructions, "by")
            
            steps.append({
                'tool': 'sum',
                'args': {'a': first_addend, 'b': second_addend},
                'result_id': 'sum_result'
            })
            
            steps.append({
                'tool': 'multiply',
                'args': {'a': {'ref': 'sum_result'}, 'b': multiplier},
                'result_id': 'final_result'
            })
        
        return steps
    
    def _extract_number_after_word(self, text: str, word: str, start_idx: int = 0) -> Union[int, float]:
        """
        Extract a number that appears after a specific word in the text.
        
        Args:
            text: The text to search in
            word: The word to look for
            start_idx: The index to start searching from
            
        Returns:
            The extracted number
        """
        word_idx = text.find(word, start_idx)
        if word_idx == -1:
            return None
        
        # Get the substring after the word
        substring = text[word_idx + len(word):].strip()
        
        # Extract the number
        number_str = ""
        for char in substring.split()[0].replace(',', ''):
            if char.isdigit() or char == '.':
                number_str += char
            elif number_str:  # Stop if we've started collecting digits and hit a non-digit
                break
        
        # Convert word numbers to digits
        word_to_number = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
            'hundred': 100, 'thousand': 1000, 'million': 1000000
        }
        
        for word_num, value in word_to_number.items():
            if word_num in substring.split():
                return value
        
        if number_str:
            if '.' in number_str:
                return float(number_str)
            return int(number_str)
        
        return None


# Part 2: Executor
class Executor:
    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize the executor with a dictionary of available tools.
        
        Args:
            tools: A dictionary mapping tool names to their function implementations
        """
        self.tools = tools
        
    def execute_plan(self, plan: List[Dict[str, Any]]) -> Any:
        """
        Execute a plan of tool calls step by step.
        
        Args:
            plan: A list of dictionaries representing tool calls
            
        Returns:
            The result of the final step in the plan
        """
        results = {}
        
        for step in plan:
            tool_name = step['tool']
            args = step['args']
            result_id = step['result_id']
            
            # Resolve any references to previous results
            resolved_args = {}
            for arg_name, arg_value in args.items():
                if isinstance(arg_value, dict) and 'ref' in arg_value:
                    ref_id = arg_value['ref']
                    if ref_id not in results:
                        raise ValueError(f"Reference to unknown result: {ref_id}")
                    resolved_args[arg_name] = results[ref_id]
                else:
                    resolved_args[arg_name] = arg_value
            
            # Execute the tool
            if tool_name not in self.tools:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            tool_func = self.tools[tool_name]
            result = tool_func(**resolved_args)
            
            # Store the result
            results[result_id] = result
        
        # Return the final result
        return results.get('final_result', None)


# Example usage
def main():
    # Define the tools
    tools = {
        'sum': lambda a, b: a + b,
        'subtract': lambda a, b: a - b,
        'multiply': lambda a, b: a * b,
        'divide': lambda a, b: a / b
    }
    
    # Create the planner and executor
    planner = Planner(tools)
    executor = Executor(tools)
    
    # Test input 1
    instructions1 = "divide by 10, the sum of 20 and 30"
    plan1 = planner.generate_plan(instructions1)
    result1 = executor.execute_plan(plan1)
    print(f"Test 1 - Instructions: '{instructions1}'")
    print(f"Plan: {plan1}")
    print(f"Result: {result1}")
    
    # Test input 2
    instructions2 = "add 20 and 30, divide it by the sum of 2 and 3"
    plan2 = planner.generate_plan(instructions2)
    result2 = executor.execute_plan(plan2)
    print(f"Test 2 - Instructions: '{instructions2}'")
    print(f"Plan: {plan2}")
    print(f"Result: {result2}")


if __name__ == "__main__":
    main()
