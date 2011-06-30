import struct

class CompoundFile:
    data = {}


    def add(self, filename, file_data):
        filename = str(filename)
        self.data[filename] = file_data


    def to_string(self):
        output = []

        for key in self.data:
            value = self.data[key]
            key_length = struct.pack('i', len(key))
            data_length = struct.pack('i', len(value))
            output.extend([key_length, key, data_length, value])
            #output.append(',')
            #output.append(key)
        
        return ''.join(output)
