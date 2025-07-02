from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from ..backend.llir import load_module_ast
from .types import TypeInfo
from ..errors import SemanticError, SourceLocation, NameError

from ..syntax_parser.ast import (
    BinaryOp,
    FunctionCall,
    FunctionDecl,
    FuncDef,
    MethodDef,
    OperatorDef,
    ForeignFuncDecl,
    ExprStmt,
    ForInStmt,
    LoopStmt,
    UntilStmt,
    DoUntilStmt,
    BreakStmt,
    ContinueStmt,
    IfStmt,
    ReturnStmt,
    RaiseStmt,
    RaiseExpr,
    MatchExpr,
    MemberAccess,
    MemberAssign,
    AssignExpr,
    Identifier,
    Integer,
    String,
    LetStmt,
    BindingStmt,
    ImportStmt,
    Block,
    ClassDef,
    DestructorDef,
    ConstructorDef,
    Program,
    Statement,
    Expression,
    UnaryOp,
)
from ..lexer.Token import Token


@dataclass
class VarInfo:
    name: str
    type_name: str | None = None
    is_mut: bool = False


@dataclass
class SemanticAnalyzer:
    """A very small semantic analyzer checking variable usage with functions."""

    variables_stack: List[Dict[str, VarInfo]] | None = None
    functions: Set[str] | None = None
    type_registry: Dict[str, TypeInfo] | None = None
    filename: str = "<stdin>"
    source_lines: List[str] = field(default_factory=list)
    loop_depth: int = 0

    def analyze(self, program: Program, *, source: str = "", filename: str = "<stdin>") -> None:
        self.filename = filename
        self.source_lines = source.splitlines()
        self.functions = set()
        self._collect_functions(program)
        self.type_registry = {}
        self.variables_stack = [{}]
        self._visit_program(program)

    def _collect_functions(self, program: Program) -> None:
        for stmt in program.statements:
            if isinstance(stmt, (FunctionDecl, FuncDef, ForeignFuncDecl)):
                self.functions.add(stmt.name)
            elif isinstance(stmt, ImportStmt):
                try:
                    mod_ast = load_module_ast(stmt.module)
                except FileNotFoundError:
                    continue
                self._collect_functions(mod_ast)

    def _visit_program(self, program: Program) -> None:
        for stmt in program.statements:
            self._visit_statement(stmt)

    # Internal helpers -------------------------------------------------
    def _current_scope(self) -> Dict[str, VarInfo]:
        assert self.variables_stack is not None
        return self.variables_stack[-1]

    def _lookup_var(self, name: str) -> VarInfo | None:
        assert self.variables_stack is not None
        for scope in reversed(self.variables_stack):
            if name in scope:
                return scope[name]
        return None

    def _is_defined(self, name: str) -> bool:
        return self._lookup_var(name) is not None

    def _get_location(self, token: Token | None) -> SourceLocation | None:
        if token is None:
            return None
        line = token.line
        column = token.col
        source_line = self.source_lines[line - 1] if 0 <= line - 1 < len(self.source_lines) else ""
        return SourceLocation(self.filename, line, column, source_line)

    def _visit_block(self, block: Block) -> None:
        for s in block.statements:
            self._visit_statement(s)

    def _visit_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, (LetStmt, BindingStmt)):
            if stmt.name in self._current_scope():
                raise NameError(
                    f"Variable '{stmt.name}' is already defined.",
                    self._get_location(stmt.loc),
                )
            if stmt.value is not None:
                self._visit_expression(stmt.value)
            is_mut = stmt.is_mut if isinstance(stmt, LetStmt) else False
            self._current_scope()[stmt.name] = VarInfo(
                stmt.name, getattr(stmt, "type_name", None), is_mut
            )
        elif isinstance(stmt, ExprStmt):
            self._visit_expression(stmt.expr)
        elif isinstance(stmt, RaiseStmt):
            self._visit_expression(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            if stmt.value is not None:
                self._visit_expression(stmt.value)
        elif isinstance(stmt, ForInStmt):
            self._visit_expression(stmt.iterable)
            self.variables_stack.append({stmt.var: VarInfo(stmt.var, None, stmt.is_mut)})
            self.loop_depth += 1
            for s in stmt.body.statements:
                self._visit_statement(s)
            self.loop_depth -= 1
            self.variables_stack.pop()
        elif isinstance(stmt, LoopStmt):
            self.variables_stack.append({})
            self.loop_depth += 1
            for s in stmt.body.statements:
                self._visit_statement(s)
            self.loop_depth -= 1
            self.variables_stack.pop()
        elif isinstance(stmt, UntilStmt):
            self._visit_expression(stmt.condition)
            self.variables_stack.append({})
            self.loop_depth += 1
            for s in stmt.body.statements:
                self._visit_statement(s)
            self.loop_depth -= 1
            self.variables_stack.pop()
        elif isinstance(stmt, DoUntilStmt):
            self.variables_stack.append({})
            self.loop_depth += 1
            for s in stmt.body.statements:
                self._visit_statement(s)
            self.loop_depth -= 1
            self.variables_stack.pop()
            self._visit_expression(stmt.condition)
        elif isinstance(stmt, BreakStmt):
            if self.loop_depth == 0:
                raise SemanticError(
                    "break statement outside of loop",
                    self._get_location(stmt.loc),
                )
        elif isinstance(stmt, ContinueStmt):
            if self.loop_depth == 0:
                raise SemanticError(
                    "continue statement outside of loop",
                    self._get_location(stmt.loc),
                )
        elif isinstance(stmt, IfStmt):
            self._visit_if_stmt(stmt)
        elif isinstance(stmt, Block):
            self.variables_stack.append({})
            for s in stmt.statements:
                self._visit_statement(s)
            self.variables_stack.pop()
        elif isinstance(stmt, ImportStmt):
            # record alias so it can be referenced later
            if stmt.alias:
                self._current_scope()[stmt.alias] = VarInfo(stmt.alias)
            try:
                mod_ast = load_module_ast(stmt.module)
            except FileNotFoundError:
                return
            self.variables_stack.append({})
            for s in mod_ast.statements:
                self._visit_statement(s)
            self.variables_stack.pop()
        elif isinstance(stmt, (FunctionDecl, FuncDef)):
            # Enter a new scope for parameters and locals
            if isinstance(stmt, FunctionDecl):
                params = {name: VarInfo(name) for name in stmt.params}
                body = stmt.body
            else:
                params = {n: VarInfo(n) for p in stmt.signature.params for n in p.names}
                body = stmt.body.statements
            self.variables_stack.append(params)
            for s in body:
                self._visit_statement(s)
            self.variables_stack.pop()
        elif isinstance(stmt, ForeignFuncDecl):
            # no body to check
            pass
        elif isinstance(stmt, ClassDef):
            self._visit_class_def(stmt)
        else:
            raise SemanticError(
                f"Unsupported statement {type(stmt).__name__}",
                self._get_location(stmt.loc),
            )

    def _visit_if_stmt(self, stmt: IfStmt) -> None:
        self._visit_expression(stmt.condition)
        self.variables_stack.append({})
        self._visit_block(stmt.then_block)
        self.variables_stack.pop()

        if stmt.else_block is not None:
            self.variables_stack.append({})
            if isinstance(stmt.else_block, IfStmt):
                self._visit_if_stmt(stmt.else_block)
            else:
                self._visit_block(stmt.else_block)
            self.variables_stack.pop()

    def _visit_class_def(self, cls: ClassDef) -> None:
        assert self.type_registry is not None
        if cls.name in self.type_registry:
            raise SemanticError(
                f"Type '{cls.name}' is already defined.",
                self._get_location(cls.loc),
            )

        type_info = TypeInfo(name=cls.name)
        self.type_registry[cls.name] = type_info

        for member in cls.body.statements:
            if isinstance(member, DestructorDef):
                type_info.has_destructor = True
                # analyze destructor body in its own scope with 'self'
                self.variables_stack.append({"self": VarInfo("self")})
                for stmt in member.body.statements:
                    self._visit_statement(stmt)
                self.variables_stack.pop()
            elif isinstance(member, ConstructorDef):
                type_info.constructor = member.signature
                self.variables_stack.append({"self": VarInfo("self")})
                for stmt in member.body.statements:
                    self._visit_statement(stmt)
                self.variables_stack.pop()
            elif isinstance(member, (MethodDef, OperatorDef)):
                param_names = {n: VarInfo(n) for p in member.signature.params for n in p.names}
                param_names["self"] = VarInfo("self")
                self.variables_stack.append(param_names)
                for stmt in member.body.statements:
                    self._visit_statement(stmt)
                self.variables_stack.pop()
            elif isinstance(member, LetStmt):
                # store member type information (type name may be None)
                type_info.members[member.name] = member.type_name
            else:
                # For now, simply visit any nested statements
                self._visit_statement(member)

    def _visit_expression(self, expr: Expression) -> None:
        if isinstance(expr, Identifier):
            name = expr.name.split('.')[0]
            if not self._is_defined(name):
                raise NameError(
                    f"Undefined variable '{expr.name}'",
                    self._get_location(expr.loc),
                )
        elif isinstance(expr, Integer):
            pass
        elif isinstance(expr, String):
            pass
        elif isinstance(expr, BinaryOp):
            self._visit_expression(expr.left)
            self._visit_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self._visit_expression(expr.operand)
        elif isinstance(expr, MemberAccess):
            self._visit_expression(expr.object)
        elif isinstance(expr, MemberAssign):
            self._visit_expression(expr.object)
            self._visit_expression(expr.value)
        elif isinstance(expr, AssignExpr):
            if not isinstance(expr.target, Identifier):
                raise SemanticError(
                    "Invalid assignment target",
                    self._get_location(expr.loc),
                )
            var = self._lookup_var(expr.target.name)
            if var is None:
                raise NameError(
                    f"Undefined variable '{expr.target.name}'",
                    self._get_location(expr.target.loc),
                )
            if not var.is_mut:
                raise SemanticError(
                    f"Cannot assign to immutable variable '{expr.target.name}'",
                    self._get_location(expr.loc),
                )
            self._visit_expression(expr.value)
        elif isinstance(expr, RaiseExpr):
            self._visit_expression(expr.expr)
        elif isinstance(expr, MatchExpr):
            self._visit_expression(expr.value)
            for case in expr.cases:
                self.variables_stack.append({case.name: VarInfo(case.name)})
                if isinstance(case.body, Expression):
                    self._visit_expression(case.body)
                else:
                    for s in case.body.statements:
                        self._visit_statement(s)
                self.variables_stack.pop()
        elif isinstance(expr, FunctionCall):
            if (
                self.type_registry is not None
                and expr.name in self.type_registry
            ):
                ctor_sig = self.type_registry[expr.name].constructor
                if ctor_sig is not None:
                    expected = [n for p in ctor_sig.params for n in p.names]
                    if len(expected) != len(expr.args):
                        raise SemanticError(
                            f"Constructor for {expr.name} takes {len(expected)} arguments",
                            self._get_location(expr.loc),
                        )
                for arg in expr.args:
                    self._visit_expression(arg)
            else:
                if '.' not in expr.name and self.functions is not None and expr.name not in self.functions:
                    raise NameError(
                        f"Undefined function '{expr.name}'",
                        self._get_location(expr.loc),
                    )
                for arg in expr.args:
                    self._visit_expression(arg)
        else:
            raise SemanticError(
                f"Unsupported expression {type(expr).__name__}",
                self._get_location(expr.loc),
            )
