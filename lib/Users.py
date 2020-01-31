import pickle
from pathlib import Path

class UsersDB:
    def __init__(self, location):
        self.db = []
        self.location = Path(location)
        if self.location.exists():
            self.load_db()
        else:
            self.location = Path('./users.pkl')
            if self.location.exists():
                self.load_db()
            else:
                self.dump_db()
    def dump_db(self):
        with open(self.location, 'wb') as f:
            pickle.dump(self.db, f)
    def load_db(self):
        with open(self.location, 'rb') as f:
            self.db = pickle.load(f)
    def add(self, chat_id):
        if chat_id not in self.db:
            self.db.append(chat_id)
            self.dump_db()
            return True
        return False
    def delete(self, chat_id):
        if chat_id in self.db:
            del self.db[self.db.index(chat_id)]
            self.dump_db()
            return True
        return False