import sys
import pickle as pkl
import array
import os
import time
import timeit
import contextlib
import re
import heapq
import bitstring
from string import punctuation

toy_dir = 'toy-data'
hexchar2int = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11,
               'c': 12, 'd': 13, 'e': 14, 'f': 15}
int2hexchar = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'a', 11: 'b',
               12: 'c', 13: 'd', 14: 'e', 15: 'f'}


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


class UncompressedPostings:

    @staticmethod
    def encode(postings_list):
        """Encodes postings_list into a stream of bytes

        Parameters
        ----------
        postings_list: List[int]
            List of docIDs (postings)

        Returns
        -------
        bytes
            bytearray representing integers in the postings_list
        """
        return array.array('L', postings_list).tobytes()

    @staticmethod
    def decode(encoded_postings_list):
        """Decodes postings_list from a stream of bytes

        Parameters
        ----------
        encoded_postings_list: bytes
            bytearray representing encoded postings list as output by encode
            function

        Returns
        -------
        List[int]
            Decoded list of docIDs from encoded_postings_list
        """

        decoded_postings_list = array.array('L')
        decoded_postings_list.frombytes(encoded_postings_list)
        return decoded_postings_list.tolist()


class InvertedIndex:
    """A class that implements efficient reads and writes of an inverted index
    to disk

    Attributes
    ----------
    postings_dict: Dictionary mapping: termID->(start_position_in_index_file,
                                                number_of_postings_in_list,
                                               length_in_bytes_of_postings_list)
        This is a dictionary that maps from termIDs to a 3-tuple of metadata
        that is helpful in reading and writing the postings in the index file
        to/from disk. This mapping is supposed to be kept in memory.
        start_position_in_index_file is the position (in bytes) of the postings
        list in the index file
        number_of_postings_in_list is the number of postings (docIDs) in the
        postings list
        length_in_bytes_of_postings_list is the length of the byte
        encoding of the postings list

    terms: List[int]
        A list of termIDs to remember the order in which terms and their
        postings lists were added to index.

        After Python 3.7 we technically no longer need it because a Python dict
        is an OrderedDict, but since it is a relatively new feature, we still
        maintain backward compatibility with a list to keep track of order of
        insertion.
    """

    def __init__(self, index_name, postings_encoding=None, directory=''):
        """
        Parameters
        ----------
        index_name (str): Name used to store files related to the index
        postings_encoding: A class implementing static methods for encoding and
            decoding lists of integers. Default is None, which gets replaced
            with UncompressedPostings
        directory (str): Directory where the index files will be stored
        """

        self.index_file_path = os.path.join(directory, index_name + '.index')
        self.metadata_file_path = os.path.join(directory, index_name + '.dict')

        if postings_encoding is None:
            self.postings_encoding = UncompressedPostings
        else:
            self.postings_encoding = postings_encoding
        self.directory = directory

        self.postings_dict = {}
        self.terms = []  # Need to keep track of the order in which the
        # terms were inserted. Would be unnecessary
        # from Python 3.7 onwards

    def __enter__(self):
        """Opens the index_file and loads metadata upon entering the context"""
        # Open the index file
        self.index_file = open(self.index_file_path, 'rb+')

        # Load the postings dict and terms from the metadata file
        with open(self.metadata_file_path, 'rb') as f:
            self.postings_dict, self.terms = pkl.load(f)
            self.term_iter = self.terms.__iter__()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Closes the index_file and saves metadata upon exiting the context"""
        # Close the index file
        self.index_file.close()

        # Write the postings dict and terms to the metadata file
        with open(self.metadata_file_path, 'wb') as f:
            pkl.dump([self.postings_dict, self.terms], f)


class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map(IdMap): For mapping terms to termIDs
    doc_id_map(IdMap): For mapping relative paths of documents (eg
        0/3dradiology.stanford.edu_) to docIDs
    data_dir(str): Path to data
    output_dir(str): Path to output index files
    index_name(str): Name assigned to index
    postings_encoding: Encoding used for storing the postings.

    The default (None) implies UncompressedPostings
    """

    def __init__(self, data_dir, output_dir, index_name="BSBI",
                 postings_encoding=None):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Stores names of intermediate indices
        self.intermediate_indices = []

    def save(self):
        """Dumps doc_id_map and term_id_map into output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pkl.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pkl.dump(self.doc_id_map, f)

    def load(self):
        """Loads doc_id_map and term_id_map from output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
            self.term_id_map = pkl.load(f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
            self.doc_id_map = pkl.load(f)

    def index(self):
        """Base indexing code

        This function loops through the data directories,
        calls parse_block to parse the documents
        calls invert_write, which inverts each block and writes to a new index
        then saves the id maps and calls merge on the intermediate indices
        """
        for block_dir_relative in sorted(next(os.walk(self.data_dir))[1]):
            td_pairs = self.parse_block(block_dir_relative)
            index_id = 'index_' + block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, directory=self.output_dir,
                                     postings_encoding=
                                     self.postings_encoding) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
        self.save()
        with InvertedIndexWriter(self.index_name, directory=self.output_dir,
                                 postings_encoding=
                                 self.postings_encoding) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(
                    InvertedIndexIterator(index_id,
                                          directory=self.output_dir,
                                          postings_encoding=
                                          self.postings_encoding))
                    for index_id in self.intermediate_indices]
                self.merge(indices, merged_index)


class BSBIIndex(BSBIIndex):
    def parse_block(self, block_dir_relative):
        """Parses a tokenized text file into termID-docID pairs

        Parameters
        ----------
        block_dir_relative : str
            Relative Path to the directory that contains the files for the block

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block

        Should use self.term_id_map and self.doc_id_map to get termIDs and docIDs.
        These persist across calls to parse_block
        """
        # my code
        td_pairs = []
        dir = self.data_dir + '/' + block_dir_relative + '/'
        filename_list = os.listdir(dir)
        for filename in filename_list:
            f = open(dir + filename)
            text = f.read()
            # text = re.sub(r"[{}]+".format(punctuation[0:6]+punctuation[7:26]+punctuation[27:32]), " ", text)  # 将标点符号转化为空格
            # text = text.lower()  # 全部字符转为小写
            # words = nltk.word_tokenize(text)  # 分词
            words = text.split()
            for word in words:
                td_pairs.append((self.term_id_map.__getitem__(word),
                                 self.doc_id_map.__getitem__(block_dir_relative + '/' + filename)))
        return td_pairs

    def invert_write(self, td_pairs, index):
        """Inverts td_pairs into postings_lists and writes them to the given index

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index on disk corresponding to the block
        """
        # my code
        td_pairs.sort(key=lambda x: (x[0], x[1]))
        now_pair = [-1, []]
        inverted_pairs_to_write = []
        for td_pair in td_pairs:
            if td_pair[0] != now_pair[0]:
                if now_pair[0] != -1:
                    inverted_pairs_to_write.append(now_pair)
                now_pair = [-1, []]
                now_pair[0] = td_pair[0]
                now_pair[1] = [td_pair[1]]
            else:
                now_pair[1].append(td_pair[1])

        for inverted_pair_to_write in inverted_pairs_to_write:
            index.append(inverted_pair_to_write[0], inverted_pair_to_write[1])

    def merge(self, indices, merged_index):
        """Merges multiple inverted indices into a single index

        Parameters
        ----------
        indices: List[InvertedIndexIterator]
            A list of InvertedIndexIterator objects, each representing an
            iterable inverted index for a block
        merged_index: InvertedIndexWriter
            An instance of InvertedIndexWriter object into which each merged
            postings list is written out one at a time
        """
        # my code
        termpostingslistpairs = []
        for indice in indices:
            while True:
                try:
                    elem = indice.__next__()
                    termpostingslistpairs.append(elem)
                except StopIteration:
                    break
        termpostingslistpairs.sort(key=lambda k: k[0])
        now_mergelist = []
        for pair in termpostingslistpairs:
            if now_mergelist == []:
                now_mergelist.append(pair[0])
                now_mergelist.append(pair[1])
            elif now_mergelist[0] == pair[0]:
                now_mergelist = self.merge_termpostingspair(now_mergelist, pair)
            else:
                merged_index.append(now_mergelist[0], now_mergelist[1])
                now_mergelist = []
                now_mergelist.append(pair[0])
                now_mergelist.append(pair[1])

    def merge_termpostingspair(self, pair1, pair2):
        # my code
        if pair1[0] != pair2[0]:
            raise ValueError("termid not pair!")
        files1 = pair1[1]
        files2 = pair2[1]
        result = []
        ptr1 = 0
        ptr2 = 0
        while ptr1 < len(files1) or ptr2 < len(files2):
            if ptr2 >= len(files2):
                result.append(files1[ptr1])
                ptr1 += 1
            elif ptr1 >= len(files1):
                result.append(files2[ptr2])
                ptr2 += 1
            elif files1[ptr1] < files2[ptr2]:
                result.append(files1[ptr1])
                ptr1 += 1
            elif files1[ptr1] > files2[ptr2]:
                result.append(files2[ptr2])
                ptr2 += 1
            elif files1[ptr1] == files2[ptr2]:
                result.append(files1[ptr1])
                ptr1 += 1
                ptr2 += 1
        return [pair1[0], result]

    def retrieve(self, query):
        """Retrieves the documents corresponding to the conjunctive query

        Parameters
        ----------
        query: str
            Space separated list of query tokens

        Result
        ------
        List[str]
            Sorted list of documents which contains each of the query tokens.
            Should be empty if no documents are found.

        Should NOT throw errors for terms not in corpus
        """
        if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
            self.load()
        # my code
        tokens = query.split(' ')
        ret_idlist = []
        ret_namelist = []

        with InvertedIndexMapper('BSBI', directory=self.output_dir, postings_encoding=self.postings_encoding) as index:
            ret_idlist = index.__getitem__(self.term_id_map.__getitem__(tokens[0]))
            for num in range(1, len(tokens)):
                now_postings = index.__getitem__(self.term_id_map.__getitem__(tokens[num]))
                ret_idlist = sorted_intersect(ret_idlist, now_postings)

        ret_idlist = list(set(ret_idlist))
        for doc_id in ret_idlist:
            ret_namelist.append(self.doc_id_map.__getitem__(doc_id))
        ret_namelist.sort()
        return ret_namelist


class InvertedIndexWriter(InvertedIndex):
    def __enter__(self):
        self.index_file = open(self.index_file_path, 'wb+')
        return self

    def append(self, term, postings_list):
        """Appends the term and postings_list to end of the index file.

        This function does three things,
        1. Encodes the postings_list using self.postings_encoding
        2. Stores metadata in the form of self.terms and self.postings_dict
           Note that self.postings_dict maps termID to a 3 tuple of
           (start_position_in_index_file,
           number_of_postings_in_list,
           length_in_bytes_of_postings_list)
        3. Appends the bytestream to the index file on disk

        Hint: You might find it helpful to read the Python I/O docs
        (https://docs.python.org/3/tutorial/inputoutput.html) for
        information about appending to the end of a file.

        Parameters
        ----------
        term:
            term or termID is the unique identifier for the term
        postings_list: List[Int]
            List of docIDs where the term appears
        """
        # my code
        encoded_postings_list = self.postings_encoding.encode(postings_list)

        self.terms.append(term)
        start_position_in_index_file = self.index_file.seek(0, 2) - self.index_file.seek(0, 0)
        self.index_file.seek(0, 2)  # 定位到index文件末尾
        self.index_file.write(encoded_postings_list)
        length_in_bytes_of_postings_list = len(encoded_postings_list)

        self.postings_dict[term] = (start_position_in_index_file, len(postings_list), length_in_bytes_of_postings_list)


class InvertedIndexIterator(InvertedIndex):
    def __enter__(self):
        """Adds an initialization_hook to the __enter__ function of super class
        """
        super().__enter__()
        self._initialization_hook()
        return self

    def _initialization_hook(self):
        """Use this function to initialize the iterator
        """
        # my code
        self.term_iter = iter(self.terms)

    def __iter__(self):
        return self

    def __next__(self):
        """Returns the next (term, postings_list) pair in the index.

        Note: This function should only read a small amount of data from the
        index file. In particular, you should not try to maintain the full
        index file in memory.
        """
        # my code
        term = self.term_iter.__next__()
        posting3tuple = self.postings_dict[term]
        self.index_file.seek(posting3tuple[0])
        postings_list_binarys = self.index_file.read(posting3tuple[2])
        postings_list = self.postings_encoding.decode(postings_list_binarys)
        ret = (term, postings_list)
        return ret

    def delete_from_disk(self):
        """Marks the index for deletion upon exit. Useful for temporary indices
        """
        self.delete_upon_exit = True

    def __exit__(self, exception_type, exception_value, traceback):
        """Delete the index file upon exiting the context along with the
        functions of the super class __exit__ function"""
        self.index_file.close()
        if hasattr(self, 'delete_upon_exit') and self.delete_upon_exit:
            os.remove(self.index_file_path)
            os.remove(self.metadata_file_path)
        else:
            with open(self.metadata_file_path, 'wb') as f:
                pkl.dump([self.postings_dict, self.terms], f)


class InvertedIndexMapper(InvertedIndex):
    def __getitem__(self, key):
        return self._get_postings_list(key)

    def _get_postings_list(self, term):
        """Gets a postings list (of docIds) for `term`.

        This function should not iterate through the index file.
        I.e., it should only have to read the bytes from the index file
        corresponding to the postings list for the requested term.
        """
        # my code
        if term not in self.postings_dict.keys():
            return []
        tuple3 = self.postings_dict[term]
        self.index_file.seek(tuple3[0])
        encoded_postings_list = self.index_file.read(tuple3[2])
        postings_list = self.postings_encoding.decode(encoded_postings_list)
        return postings_list


def sorted_intersect(list1, list2):
    """Intersects two (ascending) sorted lists and returns the sorted result

    Parameters
    ----------
    list1: List[Comparable]
    list2: List[Comparable]
        Sorted lists to be intersected

    Returns
    -------
    List[Comparable]
        Sorted intersection
    """
    # my code
    result = []
    ptr1 = 0
    ptr2 = 0
    while ptr1 < len(list1) and ptr2 < len(list2):
        if list1[ptr1] == list2[ptr2]:
            result.append(list1[ptr1])
            ptr1 += 1
            ptr2 += 1
        elif list1[ptr1] < list2[ptr2]:
            ptr1 += 1
        elif list1[ptr1] > list2[ptr2]:
            ptr2 += 1
    return result


class CompressedPostings:
    @staticmethod
    def encode(postings_list):
        """Encodes `postings_list` using gap encoding with variable byte
        encoding for each gap

        Parameters
        ----------
        postings_list: List[int]
            The postings list to be encoded

        Returns
        -------
        bytes:
            Bytes reprsentation of the compressed postings list
            (as produced by `array.tobytes` function)
        """
        # my code
        gaps_list = [postings_list[0]]
        for num in range(1, len(postings_list)):
            gaps_list.append(postings_list[num] - postings_list[num - 1])
        ret_bytes = bytes()
        for now_int in gaps_list:
            now_byteint_list = []
            now_byteint_list.append(now_int % 128 + 128)
            now_int = now_int // 128
            while now_int > 0:
                remainder = now_int % 128
                now_int = now_int // 128
                now_byteint_list.append(remainder)
            now_byteint_list.reverse()
            tmp = array.array('B', now_byteint_list).tobytes()
            ret_bytes = ret_bytes + tmp
        return ret_bytes

    @staticmethod
    def decode(encoded_postings_list):
        """Decodes a byte representation of compressed postings list

        Parameters
        ----------
        encoded_postings_list: bytes
            Bytes representation as produced by `CompressedPostings.encode`

        Returns
        -------
        List[int]
            Decoded postings list (each posting is a docIds)
        """
        # my code
        ret_postings_list = [0]
        decoded_postings_list = array.array('B')
        decoded_postings_list.frombytes(encoded_postings_list)
        now_docid = 0
        for now_int in decoded_postings_list:
            is_end = now_int // 128
            real_num = now_int % 128
            now_docid *= 128
            now_docid += real_num
            if is_end == 1:
                ret_postings_list.append(now_docid + ret_postings_list[-1])
                now_docid = 0
        ret_postings_list.remove(0)
        return ret_postings_list


class ECCompressedPostings:
    @staticmethod
    def encode(postings_list):
        """Encodes `postings_list`

        Parameters
        ----------
        postings_list: List[int]
            The postings list to be encoded

        Returns
        -------
        bytes:
            Bytes representation of the compressed postings list
        """
        # my code
        gaps_list = [postings_list[0]]
        for num in range(1, len(postings_list)):
            gaps_list.append(postings_list[num] - postings_list[num - 1])

        bits = ''
        for item in gaps_list:
            now_bits = ''
            item = item + 1  # gamma-encoding can't represent number 0
            now_power = len(bin(item)) - 2
            for i in range(1, now_power):
                now_bits = now_bits + '1'
            now_bits = now_bits + '0'
            now_bits = now_bits + str(bin(item)[3:])
            bits = bits + now_bits
        rem_bits_num = (8 - len(bits) % 8) % 8
        for i in range(0, rem_bits_num):
            bits = bits + '1'

        now_byteintlist = []
        for i in range(0, len(bits) // 8):
            byteint = int(bits[i * 8]) * 128 + int(bits[i * 8 + 1]) * 64 + int(bits[i * 8 + 2]) * 32 + int(
                bits[i * 8 + 3]) * 16 + int(bits[i * 8 + 4]) * 8 + int(bits[i * 8 + 5]) * 4 + int(
                bits[i * 8 + 6]) * 2 + int(bits[i * 8 + 7])
            now_byteintlist.append(byteint)

        tmp = array.array('B', now_byteintlist).tobytes()
        return tmp

    @staticmethod
    def decode(encoded_postings_list):
        """Decodes a byte representation of compressed postings list

        Parameters
        ----------
        encoded_postings_list: bytes
            Bytes representation as produced by `CompressedPostings.encode`

        Returns
        -------
        List[int]
            Decoded postings list (each posting is a docId)
        """
        # my code
        decoded_postings_list = array.array('B')
        decoded_postings_list.frombytes(encoded_postings_list)
        gap_list = []

        bits = ''
        for now_int in decoded_postings_list:
            now_bits = bin(now_int)[2:]
            round = 8 - len(now_bits)
            for i in range(0, round):
                now_bits = '0' + now_bits
            bits = bits + now_bits

        isrec = 0
        unarylen = 0
        reslen = 0
        nowint = 0
        for i in range(0, len(bits)):
            if isrec == 0:
                if bits[i] == '1':
                    unarylen += 1
                elif bits[i] == '0':
                    isrec = 1
                    reslen = unarylen
            elif isrec == 1:
                nowint <<= 1
                nowint += hexchar2int[bits[i]]
                reslen -= 1
            if reslen == 0 and isrec == 1:
                nowint += 2 ** unarylen
                gap_list.append(nowint - 1)  # 之前在decode的时候都加了1，现在减回去
                isrec = unarylen = nowint = 0

        if len(gap_list) == 0:
            return []
        postings_list = [gap_list[0]]
        for num in range(1, len(gap_list)):
            postings_list.append(postings_list[-1] + gap_list[num])

        return postings_list


if __name__ == '__main__':
    start_time = time.localtime(time.time())
    try:
        os.mkdir('testtime-mem-un-decoding')
    except FileExistsError:
        pass
    BSBI_instance_compressed = BSBIIndex(data_dir='pa1-data', output_dir='testtime-mem-un-decoding',
                                         postings_encoding=UncompressedPostings)
    BSBI_instance_compressed.index()
    for i in range(1, 9):
        with open('dev_queries/query.' + str(i)) as q:
            query = q.read()
            my_results = [os.path.normpath(path) for path in BSBI_instance_compressed.retrieve(query)]
            with open('dev_output/' + str(i) + '.out') as o:
                reference_results = [os.path.normpath(x.strip()) for x in o.readlines()]
                assert my_results == reference_results, "Results DO NOT match for query: " + query.strip()
            print("Results match for query:", query.strip())
    end_time = time.localtime(time.time())
    print("new memory un-encoding use "+str((end_time.tm_min-start_time.tm_min)*60+(end_time.tm_sec-start_time.tm_sec))+" seconds")