import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and len(self.cells)>0:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if len(self.cells)>0 and self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        mcount=0
        cellstoremove=[]
        for c in self.cells:
            if c[0] == cell[0] and c[1] == cell[1]:
                cellstoremove.append(c)
                mcount = mcount+1

        for c in cellstoremove:
            self.cells.remove(c)
        self.count = self.count - mcount


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        cellstoremove = []
        # mcount = 0
        for c in self.cells:
            if c[0] == cell[0] and c[1] == cell[1]:
                cellstoremove.append(c)
                # mcount = mcount + 1

        for c in cellstoremove:
            self.cells.remove(c)
    def getcells(self):
        return self.cells
    def getcount(self):
        return self.count
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        # print("Adding safe -" , cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)
        print("marked safe",cell)
        cellstobeadded = set()


        for i in range(cell[0]-1,cell[0]+2):
            for j in range(cell[1]-1,cell[1]+2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (not self.checkknownmines(i,j)) and (not self.checkknownsafes(i,j)):
                        print("cellstobeadded",i,j,count)
                        cellstobeadded.add((i, j))

        if len(cellstobeadded)>0:
            # print("adding sentence" , Sentence(cellstobeadded,count))
            cmcount = self.getneighboringminecount(cell)
            if cmcount > 0:
                # print("adding sentence with revised count", Sentence(cellstobeadded, count-cmcount))
                pass
            self.knowledge.append(Sentence(cellstobeadded,count-cmcount))
        for se in self.knowledge:
            if len(se.getcells()) > 0:
                # print("print sentence",se)
                pass

        # print("current cell", cell)
        minestobeadded = []
        safestobeadded = []
        for s in self.knowledge:

            if s.known_safes() is not None:
                # print("known safe",s)
                for cell in s.known_safes():
                    if len(self.safes)>0:
                        bfoundexisting = False
                        for csafe in self.safes:

                            if csafe[0] == cell[0] and csafe[1] == cell[1]:
                                bfoundexisting = True
                                break
                        if not bfoundexisting:
                            safestobeadded.append((cell[0],cell[1]))
                            # self.mark_safe((cell[0],cell[1]))
                            # print("I added safe-",cell[0],cell[1])
                    else:
                        safestobeadded.append((cell[0], cell[1]))
                        # self.mark_safe((cell[0],cell[1]))
                        # print("I added safe as no safes added yet-",cell[0],cell[1])
            if s.known_mines() is not None:
                print("known mines",s)
                for cell in s.known_mines():
                    if len(self.mines)>0:

                        bfoundexisting = False
                        for cmine in self.mines:
                            if cmine[0] == cell[0] and cmine[1] == cell[1]:
                                bfoundexisting = True
                                break
                        if not bfoundexisting:
                            minestobeadded.append((cell[0],cell[1]))
                            # self.mark_mine((cell[0],cell[1]))
                    else:
                        # self.mark_mine((cell[0], cell[1]))
                        minestobeadded.append((cell[0],cell[1]))
        for m in minestobeadded:
            self.mark_mine(m)
        for s in safestobeadded:
            self.mark_safe(s)
        sentencestobeadded = self.checksubsets()
        if sentencestobeadded is not None and len(sentencestobeadded)> 0:
            for st in sentencestobeadded:
                if st.getcount() == 0:
                    for cell in st.getcells():
                        self.mark_safe(cell)
                if st.getcount() == len(st.getcells()) and len(st.getcells()) > 1:
                    for cell in st.getcells():
                        self.mark_mine(cell)



    def checksubsets(self):
        sentencestobeadded = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 != s2 :
                    cnt=0
                    if (0 < len(s1.getcells()) <= len(s2.getcells())) and (s1.getcount() <= s2.getcount()):
                        for c1 in s1.getcells():
                            bfound = False
                            for c2 in s2.getcells():
                                if c1[0] == c2[0] and c1[1] == c2[1]:
                                    bfound=True
                                    cnt = cnt + 1
                                    break
                        if cnt == len(s1.getcells()) and cnt > 0:
                            tempset = set()
                            for c3 in s2.getcells():
                                bf = False
                                for c4 in s1.getcells():
                                    if c3[0] == c4[0] and c3[1] == c4[1]:
                                        bf=True
                                        break
                                if not bf:
                                    tempset.add((c3[0], c3[1]))
                            # if not self.checkSentenceExists(tempset):
                            sentencestobeadded.append(Sentence(tempset, s2.getcount() - s1.getcount()))
        return sentencestobeadded
        # for osent in sentencestobeadded:
        #     # print("adding sentence",osent)
        #     self.knowledge.append(osent)




    def checkknownmines(self,i,j):
        for cell in self.mines:
            if cell[0] == i and cell[1] == j:
                return True
        return False
    def checkknownsafes(self,i,j):
        for cell in self.safes:
            if cell[0] == i and cell[1] == j:
                return True
        return False
    def getneighboringminecount(self,cell):
        mcount = 0
        for i in range(cell[0]-1,cell[0]+2):
            for j in range(cell[1]-1,cell[1]+2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    for m in self.mines:
                        if i == m[0] and j == m[1]:
                            mcount = mcount +1
                            break
        return mcount
    def checkSentenceExists(self,sgiven):
        for c1 in sgiven:
            for s in self.knowledge:
                cnt=0
                for c2 in s.getcells():
                    if c1[0] == c2[0] and c1[1] == c2[1]:
                        cnt = cnt+1
                if cnt == len(sgiven):
                    return True
        return False


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # for cell1 in self.safes:
        #     print("safe move list - ",cell1[0],cell1[1])
        for cell1 in self.safes:

            for cell2 in self.moves_made:
                bfound = False
                if cell1[0] == cell2[0] and cell1[1] == cell2[1]:
                    bfound=True
                    break
            if not bfound:
                print("safe move",cell1[0],cell1[1])
                return cell1
        return None




    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                bfound = False
                for cell in self.moves_made:
                    if i == cell[0] and j == cell[1]:
                        bfound=True
                        break
                if not bfound:
                    bminefound = False
                    for c2 in self.mines:
                        if c2[0] == i and c2[1] == j:
                            bminefound=True
                            break
                    if not bminefound:
                        return (i,j)
        return None



