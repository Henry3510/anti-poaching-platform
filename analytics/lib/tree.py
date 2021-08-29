import re
from typing import Optional, Union, Container, Dict, List, Set

QueryT = Optional[Union[str, Container[str]]]

class NlpNode:
    def __init__(self, parent: Optional["NlpNode"], text: str, tree_dict: Optional[Dict[str, List["NlpNode"]]] = None):
        self.parent: Optional[NlpNode] = parent
        self.children: List[NlpNode] = []
        self.annotation: str = "UD"
        self.tree_dict: Dict[str, List[NlpNode]] = tree_dict if tree_dict is not None else {}

        # Build a tree with nodes from the phrase-structure tree of the text
        left_stack = []
        for i in range(len(text)):
            if text[i] == '(':
                left_stack.append(i)

            if text[i] == ')':
                left_index = left_stack.pop()

                if len(left_stack) == 0:
                    result = re.search(r'\(([A-Z]+) ((?!\().+?)?[\(\)]', text[left_index:i + 1])
                    self.full_text = text
                    assert result is not None
                    self.annotation = result.group(1)
                    try:
                        self.text = result.group(2)
                        if self.tree_dict.get(self.text) is None:
                            self.tree_dict[self.text] = []
                        self.tree_dict[self.text].append(self)
                    except:
                        pass

                if len(left_stack) == 1:
                    self.children.append(NlpNode(self, text[left_index:i + 1], self.tree_dict))

        if self.text is None:
            prepared_text = []
            for child in self.children:
                prepared_text.append(child.text)
            self.text = "".join(prepared_text)

    def match(self, text: QueryT = None, annotation: QueryT = None) -> bool:
        """A helper funtion to see if the current NlpNode match the given conditionals
        When both text and annotation are None, this function always returns True"""
        target_text = {text} if isinstance(text, str) else text
        target_annotation = {annotation} if isinstance(annotation, str) else annotation
        return (target_text is None or self.text in target_text) and (target_annotation is None or self.annotation in target_annotation)

    def tree_to_str(self, highlights: Optional[Set["NlpNode"]] = None) -> str:
        stack = [(0, self)]
        result = []

        def space(level: int) -> str:
            return "".join(["  " for _ in range(level)])

        while len(stack) > 0:
            level, cur_node = stack.pop()
            s = "*" if highlights and cur_node in highlights else ""
            cur_text = f"{space(level)}{s}{cur_node.annotation}{f' {cur_node.text}' if len(cur_node.children) == 0 else ''}{s}"
            if len(cur_node.children) == 1:
                stack.append((0, cur_node.children[0]))
                result.append(f"{cur_text} ")
            else:
                for child in reversed(cur_node.children):
                    stack.append((level + 1, child))
                result.append(f"{cur_text}\n")

        return "".join(result)

    def __repr__(self) -> str:
        return f"NlpNode {self.annotation} \"{self.text[:20]}{'...' if len(self.text) > 20 else ''}\""
    
    def __str__(self) -> str:
        return f"({self.annotation}{f' {self.text}' if self.text else ''})"

    def up(self, level: int) -> "NlpNode":
        """Trace upwards to a parent of the current NlpNode.
        When level=0, return the NlpNode itself"""
        assert level >= 0
        cur_node = self
        while level > 0:
            if not cur_node.parent:
                return cur_node
            cur_node = cur_node.parent
            level -= 1
        return cur_node

    def dfs_one(self, *, text: QueryT = None, annotation: QueryT = None, before: Optional["NlpNode"] = None, after: Optional["NlpNode"] = None) -> Optional["NlpNode"]:
        """A helper function to look up only one NlpNode"""
        result = self.dfs(text=text, annotation=annotation, before=before, after=after)
        return result[0] if len(result) > 0 else None

    def dfs(self, *, text: QueryT = None, annotation: QueryT = None, count: int = 1, before: Optional["NlpNode"] = None, after: Optional["NlpNode"] = None) -> List["NlpNode"]:
        """Conduct a depth first search for the first nth children matching the given conditionals"""
        stack: List["NlpNode"] = [self]
        result: List["NlpNode"] = []
        is_after = after is None

        def loop(cur_node: "NlpNode") -> bool:
            """A helper function to help us conveniently break the outer while loop"""
            for NlpNode in cur_node.children:
                if NlpNode.match(text, annotation):
                    result.append(NlpNode)
                    return False
                if len(result) >= count:
                    return False
            return True

        while len(stack) > 0:
            cur_node = stack.pop()

            if cur_node is before:
                return result

            if is_after and not loop(cur_node):
                break

            if cur_node is after:
                is_after = True

            for NlpNode in reversed(cur_node.children):
                stack.append(NlpNode)

        return result
