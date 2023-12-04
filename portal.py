#
# File: portl.py
# run a Flask server - used with other windmill tasks to pull some local files
# that were  filename scrapes of the Z drive.

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def getFile():
    # Expect http://windmill.sydor.local:5000/api/filename=
    # filename is one of: CheckoffLists.txt
    #   Datasheets.txt, Documentation.txt,  Manuals.txt
    #   MechanicalDrawings.txt,  Products.txt,  Projects.txt
    #   Ross.txt,  TestProcs.txt

    allowed = [ "AssyProcedures.txt", "CheckoffLists.txt", "Datasheets.txt", \
               "Documentation.txt", "Manuals.txt", "MechanicalDrawings.txt", \
               "Products.txt", "Projects.txt", "Ross.txt", "TestProcs.txt"]
    
    # Access parameters from the request.args object
    filename = request.args.get('file') 

    if not filename:
        return jsonify({'error': 'Missing filename parameter'}), 400


    # ok ok jeez security.. Only let allowed filenames to pass
    if not filename in allowed:
         return jsonify({'error': 'Invalid filename'}), 400

    filename = r"outputs/" + filename

    try:
        # Open and read the contents of the file
        with open(filename, 'r') as file:
            file_contents = file.read()

        # Return the file contents as the response
        return jsonify({'file_contents': file_contents})
    except FileNotFoundError:
        return jsonify({'error': 'File not found:'+filename}), 404
   

@app.route('/')
def hello2():
    return "Hello World!"

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000) # works!
