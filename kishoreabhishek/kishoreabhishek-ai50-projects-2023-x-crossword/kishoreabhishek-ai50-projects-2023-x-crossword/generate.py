import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains.keys():
            wtoremove = set()
            for w in self.domains[v]:
                if len(w) != v.length:
                    wtoremove.add(w)
            for w in wtoremove:
                self.domains[v].remove(w)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        rev = False
        wtoremove = set()
        if self.crossword.overlaps is None:
            return rev
        else:
            olaps = self.crossword.overlaps[x, y]
        for wx in self.domains[x]:
            cnt = 0
            for wy in self.domains[y]:
                if wx[olaps[0]] == wy[olaps[1]]:
                    cnt = cnt+1
                    break
            if cnt == 0:
                wtoremove.add(wx)
                rev = True
        for w in wtoremove:
            self.domains[x].remove(w)
        return rev


    def createarcs(self):
        arcs = []
        for v in self.crossword.variables:
            for n in self.crossword.neighbors(v):
                arcs.append(tuple((v,n)))
        return arcs


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        q = []

        if arcs is None:
            arcs = self.createarcs()
        for a in arcs:
            q.append(a)
        while len(q) !=0 :
            x,y = q.pop(0)
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for n in self.crossword.neighbors(x):
                    bfound = False
                    for t in q:
                        if t[0] == n and t[1] == x:
                            bfound = True
                            break
                    if not bfound:
                        q.append(tuple((n,x)))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if assignment is not None:
            if len(assignment) != len(self.crossword.variables):
                return False
            for v in assignment.keys():
                if len(assignment[v]) == 0:
                    return False
        else:
            return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        s = set()

        kcount = 0
        for v in assignment.keys():
            if assignment[v] is not None and len(assignment[v]) > 0:
                kcount = kcount+1
                s.add(assignment[v])
            if len(assignment[v]) != v.length:
                return False
            for n in self.crossword.neighbors(v):
                o1,o2 = self.crossword.overlaps[v,n]
                if n in assignment:
                    if v in assignment and len(assignment[v]) > 0:
                        try:
                            r=None
                            r = assignment[n][o2]
                        except:
                            pass
                        if r is not None and assignment[v][o1] != r:
                            return False



        if kcount != len(s):
            return False


        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        mdict={}
        for val in self.domains[var]:
            neliminated = 0
            for n in self.crossword.neighbors(var):
                if n not in assignment:
                    if val in self.domains[n]:
                        neliminated = neliminated+1
                    o1,o2 = self.crossword.overlaps[var,n]
                    for nval in self.domains[n]:
                        if val[o1] != nval[o2]:
                            neliminated = neliminated + 1
            mdict[val] = neliminated

        return sorted(mdict)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        mrv={}
        deg = {}
        dcountlist = []
        for v in self.crossword.variables:
            if not (v in assignment) or len(assignment[v]) == 0:
                if len(self.domains[v]) not in mrv:
                    mrv[len(self.domains[v])] = []
                dcountlist.append(len(self.domains[v]))
                mrv[len(self.domains[v])].append(v)
        if len(mrv) > 0:
            lsorted = sorted(dcountlist)
            lstied = mrv[lsorted[0]]
            if len(lstied) > 1:
                for var in lstied:
                    deg[len(self.crossword.neighbors(var))] = var
                return deg[sorted(deg,reverse=True)[0]]
            else:
                return lstied[0]

        else:
            return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        if var is None:
            return None
        for val in self.order_domain_values(var,assignment):
            # for val in self.domains[var]:
            assignment[var] = val
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            else:
                assignment.pop(var)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
