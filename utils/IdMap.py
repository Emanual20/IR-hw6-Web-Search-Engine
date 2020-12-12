class IdMap:
    """Helper class to store a mapping from strings to ids."""

    def __init__(self):
        self.str_to_id = {}
        self.id_to_str = []

    def __len__(self):
        """Return number of terms stored in the IdMap"""
        return len(self.id_to_str)

    def _get_str(self, i):
        """Returns the string corresponding to a given id (`i`)."""
        # my code
        return self.id_to_str[i]

    def _get_id(self, s):
        """Returns the id corresponding to a string (`s`).
        If `s` is not in the IdMap yet, then assigns a new id and returns the new id.
        """
        # my code
        if s in self.str_to_id.keys():
            return self.str_to_id[s]
        else:
            self.id_to_str.append(s)
            self.str_to_id[s] = self.__len__() - 1
            return self.__len__() - 1

    def __getitem__(self, key):
        """If `key` is a integer, use _get_str;
           If `key` is a string, use _get_id;"""
        if type(key) is int:
            return self._get_str(key)
        elif type(key) is str:
            return self._get_id(key)
        else:
            raise TypeError