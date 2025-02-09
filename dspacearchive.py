"""
This class handles the creation of a DSpace simple archive suitable for import into a dspace repository. 

See: http://www.dspace.org/1_6_2Documentation/ch08.html#N15B5D for more information about the DSpace 
Simple Archive format. 
"""

import os, csv
from itemfactory import ItemFactory
from shutil import copy, make_archive

class DspaceArchive:

    """
    Constructor:

    The constructor takes a path to a csv file. 
    It then parses the file, creates items, and adds the items to the archive.  
    """
    def __init__(self, input_path):
        self.items = []
        self.input_path = input_path
        self.input_base_path = os.path.dirname(input_path)

        with open(self.input_path, 'r') as f:
            reader = csv.reader(self.strip_csv_comments(f), delimiter=";")

            header = next(reader)

            item_factory = ItemFactory(header)

            for row in reader:
                item = item_factory.newItem(row)
                self.addItem(item)

    """
    Add an item to the archive. 
    """
    def addItem(self, item):
        self.items.append(item)

    """
    Get an item from the archive.
    """
    def getItem(self, index):
        return self.items[index]

    """
    Write the archie to disk in the format specified by the DSpace Simple Archive format.
    See: http://www.dspace.org/1_6_2Documentation/ch08.html#N15B5D
    """
    def write(self, dir = "."):
        self.create_directory(dir)

        for index, item in enumerate(self.items):

            #item directory
            name = "item_%03d" % (int(index) + 1)
            item_path = os.path.join(dir, name)
            self.create_directory(item_path)
            print("====== Writing Item: ", item_path, " ======")

            #contents file
            self.writeContentsFile(item, item_path)

            #collections_file
            self.writeCollectionsFile(item, item_path)

            #content files (aka bitstreams)
            self.copyFiles(item, item_path)

            #Metadata file
            self.writeMetadata(item, item_path)

    """
    Create a zip file of the archive. 
    """
    def zip(self, output_filename, dir_name = None):
        make_archive(output_filename, 'zip', dir_name)

    """
    Helper function to strip comments of the csv input file
    """
    def strip_csv_comments(self, file):
        for row in file:
            raw = row.split('#')[0].strip()
            if raw:
                yield raw


    """
    Create a directory if it doesn't already exist.
    """
    def create_directory(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)

    """
    Create a contents file that contains a lits of bitstreams, one per line. 
    """
    def writeContentsFile(self, item, item_path):
        contents_file = open(os.path.join(item_path, 'contents'), "w")

        files = item.getFiles()
        for index, file_name in enumerate(files):
            contents_file.write(file_name)
            if index < len(files):
                contents_file.write("\n")

        contents_file.close()

    """
    Create a collections file that contains the collection(s) for an item
    """
    def writeCollectionsFile(self, item, item_path):
        collections_file = open(os.path.join(item_path, 'collections'), "w")

        collections = item.getCollections()
        for index, collection_name in enumerate(collections):
            collections_file.write(collection_name)
            if index < len(collections):
                collections_file.write("\n")

        collections_file.close()


    """
    Copy the files that are referenced by an item to the item directory in the DSPace simple archive. 
    """
    def copyFiles(self, item, item_path):
        files = item.getFilePaths()
        for index, file_name in enumerate(files):
            copy(os.path.join(self.input_base_path, file_name), item_path)

    def writeMetadata(self, item, item_path):

        schemas = item.getUsedSchemas()

        for schema in schemas:
            xml = item.toXML(schema)
            if schema == 'dc':
                xml_filename = 'dublin_core.xml'
            else:
                xml_filename = 'metadata_' + schema + '.xml'

            metadata_file = open(os.path.join(item_path, xml_filename), "w")
            metadata_file.write(xml)
            metadata_file.close()


