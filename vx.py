
import csv
import os
import re
import textmining
from tensorly.decomposition import parafac
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

class TermDocumentTensor():
    def __init__(self, directory, type="binary"):
        self.tdt = []
        self.directory = directory
        self.type = type
        
    def create_term_document_tensor(self, **kwargs):
        if self.type == "binary":
            return self.create_binary_term_document_tensor(**kwargs)
        else:
            return self.create_text_corpus(**kwargs)

    def create_text_corpus(self, **kwargs):
        doc_names = os.listdir(self.directory)
        doc_content = [open(os.path.join(self.directory, file)).read() for file in os.listdir(self.directory)]
        # Convert a collection of text documents to a matrix of token counts
        vectorizer = CountVectorizer(**kwargs)
        # Learn the vocabulary dictionary and return term-document matrix.
        x1 = vectorizer.fit_transform(doc_content).toarray()
        vocab = ["vocab"]
        vocab.extend(vectorizer.get_feature_names())
        tdm = [vocab]
        for i in range(len(doc_names)):
            row = [doc_names[i]]
            row.extend(x1[i])
            tdm.append(row)
        return tdm
    
    def create_binary_term_document_tensor(self, **kwargs):
        doc_content = []
        first_occurences_corpus = {}

        for file_name in os.listdir(self.directory):
            first_occurences = {}
            byte_count = 0
            with open(self.directory + "/" + file_name, "rb") as file:
                my_string = ""
                while True:
                    byte_count += 1
                    byte_hex = file.read(1).hex()
                    if byte_hex not in first_occurences:
                        first_occurences[byte_hex] = byte_count
                    if not byte_hex:
                        print(byte_hex)
                        break
                    my_string += byte_hex + " "
                first_occurences_corpus[file_name] = first_occurences
            doc_content.append(my_string)
        doc_names = os.listdir(self.directory)
        print(first_occurences_corpus)

        # Convert a collection of text documents to a matrix of token counts
        vectorizer = TfidfVectorizer(use_idf=False)
        # Learn the vocabulary dictionary and return term-document matrix.
        x1 = vectorizer.fit_transform(doc_content).toarray()
        vocab = ["vocab"]
        vocab.extend(vectorizer.get_feature_names())
        tdm = [vocab]
        for i in range(len(doc_names)):
            row = [doc_names[i]]
            row.extend(x1[i])
            tdm.append(row)
        tdm_first_occurences = [vocab]
        # tdm_first_occurences[0] = tdm[0]
        # Create a first occurences matrix that corresponds with the tdm
        for j in range(len(doc_names)):
            item = doc_names[j]
            this_tdm = [item]
            for i in range(0, len(tdm[0])):
                word = tdm[0][i]
                try:
                    print(first_occurences_corpus[item])
                    this_tdm.append(first_occurences_corpus[item][word])
                except:
                    this_tdm.append(0)
            # print(this_tdm)
            tdm_first_occurences.append(this_tdm)

        tdt = [tdm, tdm_first_occurences]
        self.tdt = tdt
        return self.tdt
        
    def convert_term_document_tensor_to_csv(self):
        # Converts a tdm to csv
        try:
            tdt = self.tdt
            # if the tdt is 3d or greater
            if isinstance(self.tdt[0][0], list):
                tdt = self.tdt[0]
            with open("test.csv", "w", newline='') as csv_file:
                writer = csv.writer(csv_file)
                for entry in tdt:
                    num_list = map(str, entry)
                    writer.writerow(num_list)
        except IndexError:
            print("You must create the term document tensor")
            return IndexError

    def create_term_document_tensor_text(self):
        mydoclist = []
        tdm = textmining.TermDocumentMatrix()
        files = []
        first_occurences_corpus = {}
        text_names = []
        number_files = 0
        for file in os.listdir(self.directory):
            number_files += 1
            first_occurences = {}
            words = 0
            with open(self.directory + "/" + file, "r") as shake:
                files.append(file)
                lines_100 = ""
                for i in range(2):
                    my_line = shake.readline()
                    re.sub(r'\W+', '', my_line)
                    for word in my_line.split():
                        words += 1
                        if word not in first_occurences:
                            first_occurences[word] = words
                    lines_100 += my_line
            first_occurences_corpus[file] = first_occurences
            tdm.add_doc(lines_100)
            mydoclist.append(file)
            text_names.append(file)
        tdm = list(tdm.rows(cutoff=1))
        tdt = [0, 0]
        tdm_first_occurences = []
        # tdm_first_occurences[0] = tdm[0]
        # Create a first occurences matrix that corresponds with the tdm
        for j in range(len(text_names)):
            item = text_names[j]
            this_tdm = []
            for i in range(0, len(tdm[0])):
                word = tdm[0][i]
                try:
                    this_tdm.append(first_occurences_corpus[item][word])
                except:
                    this_tdm.append(0)
            # print(this_tdm)
            tdm_first_occurences.append(this_tdm)
        tdm.pop(0)
        tdt[0] = tdm
        tdt[1] = tdm_first_occurences
        tdt = np.asanyarray(tdt)
        self.tdt = tdt
        return tdt

def main():
    tdt = TermDocumentTensor("zeus_binaries")
    tdt.create_term_document_tensor(stop_words=None)
    tdt.convert_term_document_tensor_to_csv()

main()
