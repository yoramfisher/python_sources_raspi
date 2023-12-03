#!/usr/bin/python3
#
# File scanfiles_rp.py
# Scan the 'Z' drive, running on the Raspberry Pi Server
# Copy the file names to text file
# then upload to Baserow

#
#   ScanFiles - Generate a list of matching files by searching directory and
#     all of its contained sub dirs. Output is list of full paths.
#
# Version History
# v1.0 4/2/23 - Create
#   Future me: Add a time to run entry
#      Also - copy directly to a file on google drive so can skip the manual step of copy and paste
#
# v1.1 8/13/23 Add Names of all the four z:\projects_###-### to DocScan  
# TODO: 
#  * Copy Failure Report log and and IEMR Report log to drive and add to the live query search
#  *   
#  * Copy the output txt files to backup, then run.
#  If any file has changed - log it and copy to google.
#   
kVERSION="1.2"
ZDRIVE = r'/home/sydor/smb_share/' 
VERBOSE =1
global_counter = 1
OUTPUT_DIR = r'/home/sydor/python_src/outputs/'

import os
import datetime

# CONFIGURATION

# EXAMPLES

# INSTRUCTIONS

def print_in_place( item ):
    import shutil
    terminal_width, _ = shutil.get_terminal_size()  
    truncated_name =  item[-(terminal_width - 15):]  if len(item) > terminal_width - 15 else item
    print(f"\033[K{truncated_name} ", end="\r")
      
#
#
#
def createHeader(dir, extension):
    """
    """
    lines = []
    lines.append(f"Created with ScanFiles Ver {kVERSION}  Date:{datetime.date.today()}:\n")
    lines.append(f"Called with dir:{dir} and extension:{extension}\n")
    
    lines.append("#\tNA\tFilepath\tModDate\n")
    return lines

#
# Slow as F
#
def scan_files(dir_path, output_file, extension = None, foldername = None ):
    global global_counter
    skipped = {} # Create empty dictionary

    # Append to Log
    with open(OUTPUT_DIR+'log.txt', 'a') as filelog:
        filelog.writelines(f"Scanfiles run on Date:{datetime.date.today()} "\
            "with: {dir_path} {output_file}\n")
    

    # Overwrite file
    with open(OUTPUT_DIR+output_file, 'w') as file:
        header = createHeader(dir_path, extension)
        file.writelines(header)
        for root, dirs, files in os.walk(dir_path):

            # Calculate the depth of the current directory relative to the starting directory
            depth = root[len(dir_path):].count(os.path.sep)
            print_in_place(f" root{root} Depth:{depth} ")

            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            if foldername:
                if '/'+foldername+'/'  in root:
                    print( "Found subdir.")
                else:
                    continue    

            for name in files:


                try:
                    # Exclude hidden files
                    if not name.startswith('.') and not name.startswith('~') and \
                    (extension is None or any(name.lower().endswith(f".{ext}") for ext in extension)):
                        
                        # Get the full path of the file
                        file_path = os.path.join(root, name)
                        rel_path = file_path[len(dir_path):]
                        # Get the modification time of the file and convert to a readable format
                        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                        # Write the full path and modification time to the output file

                        str_en = rel_path.encode("ascii", "ignore")

                        str_en = str_en.decode()
                        str_en.replace('\t','')
                        str_en.replace(',','_')

                        
                        file.write(f"{global_counter}\t \t{str_en}\t{mod_time}\n")
                        global_counter += 1

                    else:
                        if VERBOSE:
                            
                            ext = os.path.splitext(name)[1]
                            if ext in skipped:
                                skipped[ext] += 1
                            else:
                                skipped[ext]  = 1

                            print(f"Skip: {name}")    
                except:
                    print(f"Exception caught with {name}")


    # Show extenstions of all files skipped
    if skipped:
        print("Extensions skipped")
    for k in skipped:
        print( f"{k} : {skipped[k]} ")

#
#
#
def list_directories(start_dir):
    try:

        with os.scandir(start_dir) as entries:
            for entry in entries:
            
                if entry.is_dir() and not entry.name.startswith('!'):
                        yield entry.path
                
    except:
        print(f"Exception: {start_dir} ")       


def write_to_file( dir_path, output_file,  extensions, fileslist ):
    with open(OUTPUT_DIR + output_file, 'w') as file:
        header = createHeader(dir_path, extensions)
        file.writelines(header)
        i=0
        for f in fileslist:

             # Get the modification time of the file and convert to a readable format
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M:%S')
            # Write the full path and modification time to the output file

            str_en = f.encode("ascii", "ignore")

            str_en = str_en.decode()
            file.write(f"{i}\t\t{str_en}\t{mod_time}\n")
            i += 1

#
# Hopefully faster
#
def list_files(start_dir, extension=None, max_depth=None, foldername=None):
    """
    Recursively list all files in a directory tree that match a given extension and are not hidden.
    """
    if max_depth is not None:
        max_depth -= 1
        if max_depth < 0:
            return

    try:

        with os.scandir(start_dir) as entries:
            for entry in entries:
                
                ext = os.path.splitext(entry.name.lower())[1][1:]
                if entry.is_file() and (extension is None or (ext in extension) \
                    and not entry.name.startswith('.') \
                    and not entry.name.startswith('~')   ):
                    if '/' + foldername+ '/'  in entry.path:
                        yield entry.path
                elif entry.is_dir() and not entry.name.startswith('.'):
                    yield from list_files(entry.path,  
                        extension=extension, max_depth=max_depth, foldername=foldername)
    except:
        print(f"Exception: {start_dir} ")   

        
 

if __name__ == "__main__":


    if 1:
        global_counter = 1
        scan_files(ZDRIVE + r"Documentation/Testing/Test Procedures, Test Data Sheets", "TestProcs.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'] )
    
     # MECHANICAL PDFS
    if 1:
        global_counter = 1
        scan_files(ZDRIVE + r"Documentation/Drawings/Mechanical PDFs", "MechanicalDrawings.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'] )
    

    # CHECK-OFF LISTS
    if 1:
        global_counter = 1
        scan_files(ZDRIVE + r"Documentation/Check-off Lists", "CheckoffLists.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'] )

    # DATASHEETS
    if 1:
        global_counter = 1
        scan_files(ZDRIVE + r"Documentation/Datasheets", "Datasheets.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'] )

    # FYI takes a stupid amount of time
    # MANUALS
    # This one scans from root, but only searches within directories named 'Manuals'
    if 1:
        global_counter = 1
        scan_files(ZDRIVE + r"", "Manuals.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'],
                foldername='Manuals' )


    # ASSEMBLY_PROCEDURES
    # This one scans from root, but only searches within directories named 'Assembly Procedures'
    if 1:
        scan_files(ZDRIVE + r"", "AssyProcedures.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'],
                foldername='Assembly Procedures' )


    # Faster - but there are not enough ASSEMBLY PROCEDURES on Z to warrant a separate file
    if 0: # Leave this disabled
        # Test new code faster?
        dir_path = ZDRIVE
        exts = ['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt']
        files = list(list_files(dir_path,
                    extension=exts,
                    max_depth=6, foldername='Assembly Procedures'))
        
        write_to_file( dir_path, "AssyProcedures.txt",  exts, files )
    

     # Scan ALL the folders in Z:\Documentation except ones listed
    if 1:
        skippaths = ["!Anchor", "3D_PDF", "Archive", "Check-off Lists", "Drawings",
                     "Manuals", "Testing"]

        global_counter = 1   
        dir_path = ZDRIVE + "Documentation/"
        exts = ['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt']

        try:

            with os.scandir(dir_path) as entries:
                for entry in entries:
                    x = entry.path[ len(dir_path):]
                    if x in skippaths:
                       continue 
        
                    scan_files(entry.path , "Documentation.txt", 
                        extension=exts
                    )

        except:
            print(f"Exception caught with {dir_path}")     


     # Scan Project # folder names
    if 1:
        global_counter = 1   
        dir_path = ZDRIVE 
        proj_paths = [r"Project#_1000_1299", r"Project#_1300_1499", 
                      r"Project#_7000_7999", r"PROJECTS_Old_2000_to_2014",
                      r"Projects_With_No_Number_Yet"]


        exts = []
        for pp in proj_paths:
            dp = dir_path + '/' + pp 
            files = list(list_directories(dp) )
                         
            write_to_file( dp, "Projects.txt",  exts, files )


    # PRODUCTS
    if 1: 
        global_counter = 1
        scan_files(ZDRIVE + r"PRODUCTS", "Products.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'] )
    
    #ROSS
    if 1: 
        global_counter = 1
        scan_files(ZDRIVE + r"ROSS", "Ross.txt", 
               extension=['doc', 'docx', 'pdf','xls','xlsx','jpeg','bmp','jpg','pptx','ppt'] )
    
                 