from typing import List, Optional, Tuple


class BranchNode(object):
    current_branch = None  # type: BranchNode

    def __init__(self,
                 parent: Optional['BranchNode'] = None,
                 name: Optional[str] = None) -> None:
        self.parent = parent
        self.children = []  # type: List[BranchNode]
        self.name = name
        if parent is None:
            self.generation = 1
        else:
            self.generation = parent.generation + 1

    def newChild(self, name: Optional[str] = None) -> 'BranchNode':
        child = BranchNode(self, name)
        self.children.append(child)
        return child

    # list with all anscestors and itself
    def anscestorsList(self) -> List['BranchNode']:
        ans = [None] * self.generation
        node = self  # type: Optional[BranchNode]
        i = self.generation-1
        while node is not None:
            ans[i] = node  # type: ignore
            node = node.parent
            i -= 1
        assert i == -1, "self.generation doesn't coincide with number of ancestors"
        return ans  # type: ignore

    # this function tells us the separation of self to other
    # returns a tuple where the first element tells us how many ancestors have
    # they in common the second element tells us how many parents up in the
    # tree we need to go up, and the third element tells us how many nodes down
    # from it we need to go
    def findDistanceToNode(self, other: 'BranchNode') -> Tuple[int, int, int]:
        self_ancestors = self.anscestorsList()
        other_ancestors = other.anscestorsList()

        same_ancestors = 0
        for i in range(min(len(self_ancestors), len(other_ancestors))):
            if self_ancestors[i] == other_ancestors[i]:
                same_ancestors += 1
            else:
                break

        up   = len(self_ancestors) - same_ancestors
        down = len(other_ancestors) - same_ancestors
        return same_ancestors, up, down

    def treeInList(self, level: Optional[int] = None) -> List[Tuple[int, 'BranchNode']]:
        if level is None:
            level = len(self.anscestorsList()) - 1
        tree = [(level, self)]
        for node in self.children:
            tree.extend( node.treeInList(level+1) )  # noqa: E201, E202
        return tree

    def printTree(self) -> None:
        for level, node in self.treeInList():
            for i in range(level):
                print('| ', end='')
            print('+', node)

    def __repr__(self) -> str:
        if self.name is not None:
            return "<{}>.0x{:02x}".format(self.name, id(self))
        else:
            return "0x{:02x}".format(id(self))


global_branch = BranchNode(name='global')
BranchNode.current_branch = global_branch
