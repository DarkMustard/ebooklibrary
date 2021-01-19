

class Book():
    def __init__(self, title, author, filepath=None, isEpub = True):
        self.title = title
        self.author = author
        self.filepath = filepath
        self.completed = False
        self.favourite = False
        self.isEpub = isEpub
        
    def toggleCompleted(self):
        self.completed = not self.completed
        
    def toggleFavourite(self):
        self.favourite = not self.favourite
        
class TabModel():
    def __init__(self, books=None):
        self.books = books or []