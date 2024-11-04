from llama_index.core import SimpleDirectoryReader

loader = SimpleDirectoryReader ("data",recursive=True, required_exts=[".pdf", ".txt", ".docx"], exclude=[r"E:\INTERN-BISTEC\Projects\V1\data"])

documents = loader.load_data()
for document in documents:
    print (document)
    print(document.metadata["file_name"], document.metadata["file_path"])