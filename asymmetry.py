class AsymNode:
    def __init__(self, lamb=None, asym=None, next_node=None):
        self.lamb = lamb
        self.asym = asym
        self.next_node = next_node

    def get_asym(self):
        return self.asym

    def get_data(self):
        return self.lamb, self.asym

    def get_next(self):
        return self.next_node

    def set_next(self,new_node):
        self.next_node = new_node


class AsymList:
    def __init__(self, width=None, head=None, next=None):
        self.width = width
        self.first = head
        self.next = next

    def get_width(self):
        return self.width

    def get_next(self):
        return self.next

    def set_next(self, next):
        self.next = next

    def inject_node(self, tail, asym):
        new_node = AsymNode(tail, asym)
        current = self.first
        if current is None:
            self.first = new_node
        else:
            keep_going = True
            while keep_going:
                if current.get_asym() > asym:
                    new_node.set_next(current)
                    self.first = new_node
                    keep_going = False
                elif current.get_asym() < asym:
                    if current.get_next() is None:
                        current.set_next(new_node)
                        keep_going = False
                    elif current.get_next().get_asym() > asym:
                        old_next_node = current.get_next()
                        current.set_next(new_node)
                        new_node.set_next(old_next_node)
                        keep_going = False
                else:
                    current = current.get_next()

    def find(self, asym):
        current = self.first
        if current is None:
            return "no nodes found"
        else:
            while current.get_next().get_asym() <= asym:
                current = current.get_next()
            if current.get_asym() == asym:
                return current.get_data()
            else:
                return [current.get_data(), current.get_next().get_data()]

    def return_list(self):
        current = self.first
        queue = []
        while current:
            queue.append(current.get_data())
            current = current.get_next()
        return queue


class AsymGrid:
    def __init__(self, head=None):
        self.first = head

    def inject_list(self, width):
        new_list = AsymList(width)
        current = self.first
        if current is None:
            self.first = new_list
        else:
            keep_going = True
            while keep_going:
                if current.get_width() > width:
                    new_list.set_next(current)
                    self.first = new_list
                    keep_going = False
                elif current.get_width() < width:
                    if current.get_next() is None:
                        current.set_next(new_list)
                        keep_going = False
                    elif current.get_next().get_width() > width:
                        old_next_list = current.get_next()
                        current.set_next(new_list)
                        new_list.set_next(old_next_list)
                        keep_going = False
                else:
                    current = current.get_next()

    def return_grid(self):
        current = self.first
        grid = []
        while current:
            grid.append([current.get_width(), current.return_list()])
            current = current.get_next()
        return grid

    def find(self, width):
        current = self.first
        if current is None:
            return "no lists found in grid"
        else:
            while current.get_width < width:
                current = current.get_next
            return current


if __name__ == "__main__":
    grid = AsymGrid()
    grid.inject_list(0.3)
    grid.inject_list(0.5)
    grid.inject_list(0.2)
    current = grid.first
    next = grid.first.get_next()
    current.inject_node(0.5, 1.3)
    current.inject_node(0.3, 1.6)
    current.inject_node(0.4, 1.4)
    current.inject_node(0.6, 1.2)

    next.inject_node(0.6, 1.2)
    next.inject_node(0.3, 1.4)
    next.inject_node(0.1, 1.1)
    grid.return_grid()
    current.find(1.5)

