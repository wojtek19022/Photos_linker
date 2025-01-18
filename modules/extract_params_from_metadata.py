
def open_metadata_file(metadata_file):
    lines = {(i.strip()) for i in open(metadata_file, 'r').readlines()}
    metadata = {
        line.split('=')[0]: line.split('=')[1].strip("\n") for line in lines \
        if line.startswith("name") or line.startswith("version")
    }

    return metadata