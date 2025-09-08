import ast
import re
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter


@dataclass
class StaticAnalysisIssue:
    """Represents a static analysis issue found in code."""
    type: str  # "logic", "performance", "relevance", "complexity"
    category: str  # specific subcategory like "unreachable_code", "inefficient_loop", etc.
    severity: str  # "critical", "high", "medium", "low"
    line_number: int
    code_snippet: str
    description: str
    impact: str
    remediation: str
    metric_value: Optional[float] = None  # For complexity metrics


class StaticCodeAnalyzer(ast.NodeVisitor):
    """AST-based static analyzer for Python code."""
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        self.issues: List[StaticAnalysisIssue] = []
        self.defined_names: Set[str] = set()
        self.used_names: Set[str] = set()
        self.function_definitions: Dict[str, int] = {}  # name -> line number
        self.class_definitions: Dict[str, int] = {}
        self.variable_assignments: Dict[str, List[int]] = defaultdict(list)
        self.function_calls: Set[str] = set()
        self.imports: Set[str] = set()
        self.current_function: Optional[str] = None
        self.current_class: Optional[str] = None
        self.complexity_stack: List[int] = [1]  # Track cyclomatic complexity
        
    def analyze(self) -> List[StaticAnalysisIssue]:
        """Run the complete static analysis."""
        try:
            tree = ast.parse(self.code)
            self.visit(tree)
            
            # Run additional checks after AST traversal
            self._check_unused_definitions()
            self._check_performance_patterns()
            self._check_logic_patterns()
            
            return self.issues
        except SyntaxError as e:
            # If code has syntax errors, return a single issue
            return [StaticAnalysisIssue(
                type="logic",
                category="syntax_error",
                severity="critical",
                line_number=getattr(e, 'lineno', 1),
                code_snippet=self.lines[getattr(e, 'lineno', 1) - 1] if self.lines else "",
                description=f"Syntax error: {str(e)}",
                impact="Code will not execute",
                remediation="Fix the syntax error"
            )]
    
    def visit_FunctionDef(self, node):
        """Analyze function definitions."""
        func_name = node.name
        self.function_definitions[func_name] = node.lineno
        self.defined_names.add(func_name)
        
        prev_function = self.current_function
        self.current_function = func_name
        
        # Check function complexity
        self._check_function_complexity(node)
        
        # Check for unused parameters
        self._check_unused_parameters(node)
        
        self.generic_visit(node)
        self.current_function = prev_function
    
    def visit_ClassDef(self, node):
        """Analyze class definitions."""
        class_name = node.name
        self.class_definitions[class_name] = node.lineno
        self.defined_names.add(class_name)
        
        prev_class = self.current_class
        self.current_class = class_name
        
        # Check class complexity
        self._check_class_complexity(node)
        
        self.generic_visit(node)
        self.current_class = prev_class
    
    def visit_Assign(self, node):
        """Analyze variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                self.defined_names.add(var_name)
                self.variable_assignments[var_name].append(node.lineno)
        
        # Check for assignment vs equality confusion
        self._check_assignment_patterns(node)
        
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Track name usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Analyze function calls."""
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            # For method calls like obj.method()
            if hasattr(node.func, 'attr'):
                self.function_calls.add(node.func.attr)
        
        # Check for performance issues in calls
        self._check_call_performance(node)
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Track imports."""
        for alias in node.names:
            self.imports.add(alias.name)
    
    def visit_ImportFrom(self, node):
        """Track from imports."""
        if node.module:
            self.imports.add(node.module)
        for alias in node.names:
            self.imports.add(alias.name)
    
    def visit_For(self, node):
        """Analyze for loops."""
        self.complexity_stack[-1] += 1
        self._check_loop_performance(node)
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Analyze while loops."""
        self.complexity_stack[-1] += 1
        self._check_while_loop_logic(node)
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Analyze if statements."""
        self.complexity_stack[-1] += 1
        self._check_conditional_logic(node)
        self.generic_visit(node)
    
    def visit_Compare(self, node):
        """Analyze comparisons."""
        self._check_comparison_logic(node)
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        """Analyze boolean operations."""
        self._check_boolean_logic(node)
        self.generic_visit(node)
    
    def _check_function_complexity(self, node):
        """Check function complexity metrics."""
        # Count lines of code (excluding empty lines and comments)
        func_lines = []
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(self.lines)
        
        for i in range(start_line, min(end_line, len(self.lines))):
            line = self.lines[i].strip()
            if line and not line.startswith('#'):
                func_lines.append(line)
        
        loc = len(func_lines)
        
        # Save current complexity and start new count for this function
        self.complexity_stack.append(1)
        
        # Count complexity-contributing nodes
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(node)
        cyclomatic_complexity = complexity_visitor.complexity
        
        # Restore previous complexity
        self.complexity_stack.pop()
        
        # Flag complex functions
        if loc > 50:
            self.issues.append(StaticAnalysisIssue(
                type="complexity",
                category="long_function",
                severity="medium" if loc > 100 else "low",
                line_number=node.lineno,
                code_snippet=f"def {node.name}(...):",
                description=f"Function '{node.name}' is very long ({loc} lines of code)",
                impact="Difficult to understand, maintain, and test",
                remediation="Consider breaking this function into smaller, more focused functions",
                metric_value=loc
            ))
        
        if cyclomatic_complexity > 10:
            self.issues.append(StaticAnalysisIssue(
                type="complexity",
                category="high_cyclomatic_complexity",
                severity="medium" if cyclomatic_complexity > 20 else "low",
                line_number=node.lineno,
                code_snippet=f"def {node.name}(...):",
                description=f"Function '{node.name}' has high cyclomatic complexity ({cyclomatic_complexity})",
                impact="Difficult to test and understand, prone to bugs",
                remediation="Simplify control flow, extract complex logic into separate functions",
                metric_value=cyclomatic_complexity
            ))
    
    def _check_class_complexity(self, node):
        """Check class complexity."""
        method_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef))
        
        if method_count > 20:
            self.issues.append(StaticAnalysisIssue(
                type="complexity",
                category="large_class",
                severity="medium",
                line_number=node.lineno,
                code_snippet=f"class {node.name}:",
                description=f"Class '{node.name}' has too many methods ({method_count})",
                impact="Violates Single Responsibility Principle, hard to maintain",
                remediation="Consider splitting into multiple classes with focused responsibilities",
                metric_value=method_count
            ))
    
    def _check_unused_parameters(self, node):
        """Check for unused function parameters."""
        param_names = set()
        for arg in node.args.args:
            param_names.add(arg.arg)
        
        # Find which parameters are used in the function body
        used_in_function = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                used_in_function.add(n.id)
        
        unused_params = param_names - used_in_function
        for param in unused_params:
            if not param.startswith('_'):  # Ignore parameters starting with _
                self.issues.append(StaticAnalysisIssue(
                    type="relevance",
                    category="unused_parameter",
                    severity="low",
                    line_number=node.lineno,
                    code_snippet=f"def {node.name}({param}, ...):",
                    description=f"Parameter '{param}' is never used in function '{node.name}'",
                    impact="Code clutter, potential confusion",
                    remediation=f"Remove unused parameter '{param}' or prefix with underscore if intentionally unused"
                ))
    
    def _check_assignment_patterns(self, node):
        """Check for potential assignment vs equality issues."""
        # This is more of a pattern check since AST parsing means syntax is correct
        for target in node.targets:
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Compare):
                line_text = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""
                # Look for potential confusion patterns in comments or nearby code
                if "==" in line_text and line_text.count("=") == 3:  # Likely intended comparison
                    self.issues.append(StaticAnalysisIssue(
                        type="logic",
                        category="assignment_confusion",
                        severity="medium",
                        line_number=node.lineno,
                        code_snippet=line_text.strip(),
                        description="Assignment of comparison result - verify this is intentional",
                        impact="May indicate confusion between assignment (=) and equality (==)",
                        remediation="Double-check if this should be a comparison in an if statement"
                    ))
    
    def _check_call_performance(self, node):
        """Check for performance issues in function calls."""
        if isinstance(node.func, ast.Attribute):
            # Check for inefficient membership testing
            if (hasattr(node.func, 'attr') and node.func.attr == 'append' and 
                isinstance(node.func.value, ast.Name)):
                # Look for patterns like: for x in items: result.append(x) 
                # which could be result.extend(items)
                pass  # Would need more context analysis
            
            # Check for sort() followed by access patterns
            if hasattr(node.func, 'attr') and node.func.attr in ['sort', 'sorted']:
                self._flag_sort_usage(node)
    
    def _check_loop_performance(self, node):
        """Check for performance issues in loops."""
        # Check for nested loops
        nested_loops = []
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)) and child != node:
                nested_loops.append(child)
        
        if nested_loops:
            self.issues.append(StaticAnalysisIssue(
                type="performance",
                category="nested_loops",
                severity="medium",
                line_number=node.lineno,
                code_snippet=self._get_line_snippet(node.lineno),
                description="Nested loops detected - potential O(n²) or higher complexity",
                impact="May cause performance issues with large datasets",
                remediation="Consider algorithm optimization, caching, or data structure changes"
            ))
        
        # Check for list comprehension opportunities
        if isinstance(node, ast.For) and len(node.body) == 1:
            if (isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Call) and
                isinstance(node.body[0].value.func, ast.Attribute) and
                hasattr(node.body[0].value.func, 'attr') and
                node.body[0].value.func.attr == 'append'):
                
                self.issues.append(StaticAnalysisIssue(
                    type="performance",
                    category="list_comprehension_opportunity",
                    severity="low",
                    line_number=node.lineno,
                    code_snippet=self._get_line_snippet(node.lineno),
                    description="Loop could be replaced with list comprehension",
                    impact="Slightly less efficient and less Pythonic",
                    remediation="Consider using list comprehension: [expr for item in iterable]"
                ))
    
    def _check_while_loop_logic(self, node):
        """Check while loop logic for potential issues."""
        # Check for while True without break
        if (isinstance(node.test, ast.Constant) and node.test.value is True):
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.issues.append(StaticAnalysisIssue(
                    type="logic",
                    category="infinite_loop",
                    severity="high",
                    line_number=node.lineno,
                    code_snippet="while True:",
                    description="Infinite loop without break statement",
                    impact="Will cause program to hang indefinitely",
                    remediation="Add break condition or use a different loop structure"
                ))
    
    def _check_conditional_logic(self, node):
        """Check conditional logic for issues."""
        # Check for always-true or always-false conditions
        if isinstance(node.test, ast.Constant):
            if node.test.value:
                self.issues.append(StaticAnalysisIssue(
                    type="logic",
                    category="always_true_condition",
                    severity="medium",
                    line_number=node.lineno,
                    code_snippet=self._get_line_snippet(node.lineno),
                    description="Condition is always True",
                    impact="Dead code - else branch will never execute",
                    remediation="Remove the condition or fix the logic"
                ))
            else:
                self.issues.append(StaticAnalysisIssue(
                    type="logic",
                    category="always_false_condition",
                    severity="medium",
                    line_number=node.lineno,
                    code_snippet=self._get_line_snippet(node.lineno),
                    description="Condition is always False",
                    impact="Dead code - if branch will never execute",
                    remediation="Remove the condition or fix the logic"
                ))
    
    def _check_comparison_logic(self, node):
        """Check comparison logic."""
        # Check for chained comparisons that might be confusing
        if len(node.ops) > 2:
            self.issues.append(StaticAnalysisIssue(
                type="logic",
                category="complex_chained_comparison",
                severity="low",
                line_number=node.lineno,
                code_snippet=self._get_line_snippet(node.lineno),
                description="Complex chained comparison may be hard to understand",
                impact="Reduced code readability",
                remediation="Consider breaking into multiple simpler comparisons"
            ))
    
    def _check_boolean_logic(self, node):
        """Check boolean operations for potential issues."""
        line_text = self._get_line_snippet(node.lineno)
        
        # Check for & instead of 'and' (bitwise vs logical)
        if '&' in line_text and not any(op in line_text for op in ['<<', '>>', '|', '^']):
            # Might be using bitwise operator instead of logical
            self.issues.append(StaticAnalysisIssue(
                type="logic",
                category="bitwise_vs_logical",
                severity="medium",
                line_number=node.lineno,
                code_snippet=line_text,
                description="Potential use of bitwise operator (&) instead of logical operator (and)",
                impact="May cause unexpected behavior in boolean contexts",
                remediation="Use 'and' for logical operations, '&' only for bitwise operations"
            ))
    
    def _check_unused_definitions(self):
        """Check for unused functions, classes, and variables."""
        # Check unused functions
        for func_name, line_no in self.function_definitions.items():
            if func_name not in self.function_calls and not func_name.startswith('_'):
                # Special cases to ignore
                if func_name in ['main', '__init__', '__str__', '__repr__']:
                    continue
                
                self.issues.append(StaticAnalysisIssue(
                    type="relevance",
                    category="unused_function",
                    severity="low",
                    line_number=line_no,
                    code_snippet=f"def {func_name}(...):",
                    description=f"Function '{func_name}' is defined but never called",
                    impact="Code clutter, potential confusion",
                    remediation=f"Remove unused function '{func_name}' or add calls to it"
                ))
        
        # Check unused classes
        for class_name, line_no in self.class_definitions.items():
            if class_name not in self.used_names and not class_name.startswith('_'):
                self.issues.append(StaticAnalysisIssue(
                    type="relevance",
                    category="unused_class",
                    severity="medium",
                    line_number=line_no,
                    code_snippet=f"class {class_name}:",
                    description=f"Class '{class_name}' is defined but never used",
                    impact="Code clutter, maintenance overhead",
                    remediation=f"Remove unused class '{class_name}' or add usage"
                ))
        
        # Check for variables assigned but never used
        for var_name, line_nos in self.variable_assignments.items():
            if (var_name not in self.used_names and not var_name.startswith('_') and
                var_name not in ['self', 'cls']):
                
                self.issues.append(StaticAnalysisIssue(
                    type="relevance",
                    category="unused_variable",
                    severity="low",
                    line_number=line_nos[0],
                    code_snippet=f"{var_name} = ...",
                    description=f"Variable '{var_name}' is assigned but never used",
                    impact="Code clutter, potential waste of computation",
                    remediation=f"Remove unused variable '{var_name}' or add usage"
                ))
    
    def _check_performance_patterns(self):
        """Check for common performance anti-patterns."""
        code_lower = self.code.lower()
        
        # Check for inefficient membership testing
        if 'in [' in self.code or 'in(' in self.code.replace(' ', ''):
            for i, line in enumerate(self.lines):
                if ' in [' in line or 'in(' in line.replace(' ', ''):
                    self.issues.append(StaticAnalysisIssue(
                        type="performance",
                        category="inefficient_membership_test",
                        severity="medium",
                        line_number=i + 1,
                        code_snippet=line.strip(),
                        description="Using list for membership testing instead of set",
                        impact="O(n) complexity instead of O(1) for large collections",
                        remediation="Use set for membership testing: 'item in {set_items}' or 'item in set(items)'"
                    ))
        
        # Check for repeated computation in loops
        self._check_repeated_computation()
    
    def _check_repeated_computation(self):
        """Check for computations that could be moved out of loops."""
        # This is a simplified check - would need more sophisticated analysis for real cases
        for i, line in enumerate(self.lines):
            if 'for ' in line and ':' in line:
                # Look ahead for potential repeated computations
                j = i + 1
                while j < len(self.lines) and (self.lines[j].startswith('    ') or self.lines[j].strip() == ''):
                    if j < len(self.lines) and 'len(' in self.lines[j]:
                        self.issues.append(StaticAnalysisIssue(
                            type="performance",
                            category="repeated_computation",
                            severity="low",
                            line_number=j + 1,
                            code_snippet=self.lines[j].strip(),
                            description="Potential repeated computation of len() in loop",
                            impact="Unnecessary recomputation on each iteration",
                            remediation="Store len() result in variable before loop"
                        ))
                        break
                    j += 1
    
    def _check_logic_patterns(self):
        """Check for logical issues using pattern matching."""
        for i, line in enumerate(self.lines):
            line_stripped = line.strip()
            
            # Check for common logic mistakes
            if '=' in line_stripped and '==' not in line_stripped and '!=' not in line_stripped:
                # Look for assignment in what might be intended as comparison
                if line_stripped.startswith('if ') and '=' in line_stripped.split('if ')[1]:
                    # This would be caught by syntax error in most cases, but flag suspicious patterns
                    pass
            
            # Check for unreachable code after return/break/continue
            if any(keyword in line_stripped for keyword in ['return ', 'break', 'continue']):
                # Check next non-empty, non-comment line
                j = i + 1
                while j < len(self.lines):
                    next_line = self.lines[j].strip()
                    if next_line and not next_line.startswith('#'):
                        # Check if it's at the same indentation level (not a different block)
                        if (len(self.lines[j]) - len(self.lines[j].lstrip()) == 
                            len(line) - len(line.lstrip())):
                            self.issues.append(StaticAnalysisIssue(
                                type="logic",
                                category="unreachable_code",
                                severity="medium",
                                line_number=j + 1,
                                code_snippet=next_line,
                                description="Code appears to be unreachable",
                                impact="Dead code that will never execute",
                                remediation="Remove unreachable code or fix control flow"
                            ))
                        break
                    j += 1
    
    def _flag_sort_usage(self, node):
        """Flag potentially inefficient sort usage."""
        # This is a placeholder for more sophisticated sort analysis
        self.issues.append(StaticAnalysisIssue(
            type="performance",
            category="sort_analysis",
            severity="low",
            line_number=node.lineno,
            code_snippet=self._get_line_snippet(node.lineno),
            description="Sort operation detected - verify if full sort is needed",
            impact="May be inefficient if only partial ordering is needed",
            remediation="Consider heapq.nlargest/nsmallest for partial sorting, or bisect for maintaining sorted order"
        ))
    
    def _get_line_snippet(self, line_no: int) -> str:
        """Get a code snippet for the given line number."""
        if 1 <= line_no <= len(self.lines):
            return self.lines[line_no - 1].strip()
        return ""


class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity."""
    
    def __init__(self):
        self.complexity = 1
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        # Each additional condition in and/or adds complexity
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def analyze_code_static(code: str) -> List[StaticAnalysisIssue]:
    """
    Main entry point for static code analysis.
    
    Args:
        code: Python source code to analyze
        
    Returns:
        List of static analysis issues found
    """
    analyzer = StaticCodeAnalyzer(code)
    return analyzer.analyze()
