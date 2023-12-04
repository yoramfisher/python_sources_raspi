#!/usr/bin/python3
# File: PytoP4
# Description: Talk to a Perforce server
# History
# V 1.0 10/24/23- Created

import re
from P4 import P4, P4Exception
from restAPI import Baserow


# Define the server IP address and port
server_ip = '192.168.11.20'
server_port = '1666'  # Replace with your Perforce server's port number



    
#
# TODO - move this to a general utlity at somep point
#
def log_list_to_file_with_headers( result_list, 
                                  filename = "out.cvs", 
                                  headers = ["H1", "H2"] ):
    # Define the output file path
    output_file = filename  

    # Open the file for writing
    with open(output_file, 'w') as file:

        # headers
        file.write(f'{headers[0]},{headers[1]}\n')

        # Write each tuple to the file with a comma separator and a newline
        for item in result_list:
            file.write(f'{item[0]},{item[1]}\n')



#
# 
#             
class sydorP4:
    def __init__(self, **kwargs):
        # Initialize the P4 connection with the server address
        p4 = P4()
        p4.port = server_ip + ':' + server_port  # Combine the IP and port
        p4.user = 'Yoram'  # Replace with your Perforce username
        p4.password = ''  # Replace with your Perforce password
        self.p4 = p4
        pass




    #
    #
    #
    def doScan(self):
    
        p4_top_level = ["//Schematics/...", "//Cables/..."]

        all_the_files = []

        for ptl in p4_top_level:

            pdf_files = []
            excel_files = []
            doc_files = []
            ppt_files = []
            p4 = self.p4

            try:
                # Connect to the Perforce server
                p4.connect()

                # Run the 'files' command to list all files in the //Schematics depot
                result = p4.run('files', f'{ptl}')

                #-e flag: May want to try.
                # Exclude deleted, purged, or archived files; the files that remain are those available for syncing or integration.
                

                # Use a list comprehension to filter files ending with '.pdf' 
                pdf_files = [item['depotFile'] for item in result 
                            if item['depotFile'].endswith('.pdf') ]

                # Use a list comprehension to filter files ending with '.xls' or '.xlsx'
                excel_files = [item['depotFile'] for item in result 
                            if item['depotFile'].endswith('.xls') or item['depotFile'].endswith('.xls')]

                # Use a list comprehension to filter files ending with ...
                doc_files = [item['depotFile'] for item in result 
                            if item['depotFile'].endswith('.doc') or item['depotFile'].endswith('.docx')]

                # Use a list comprehension to filter files ending with ...
                ppt_files = [item['depotFile'] for item in result 
                            if item['depotFile'].endswith('.ppt') or item['depotFile'].endswith('.pptx')]


                all_the_files.extend( pdf_files)
                all_the_files.extend( excel_files)
                all_the_files.extend( doc_files)
                all_the_files.extend( ppt_files)
                


            except P4Exception as e:
                print(f"Perforce error: {e}")
            finally:
                # Disconnect from the Perforce server
                p4.disconnect()

        #endfor
        # 
        #print(all_the_files)    
        # 



        # List containing items with 'SI-######' in the file name
        with_si = [item for item in all_the_files if 'SI-' in item]

        # List containing items without 'SI-######' in the file name
        without_si = [item for item in all_the_files if 'SI-' not in item]

        # Regular expression pattern to match 'SI-######'
        pattern = r'SI-\d{6}'


        # Initialize a list for tuples
        result_list = []

        # Iterate through the filenames and extract 'SI-######'
        for filename in with_si:
            match = re.search(pattern, filename)
            if match:
                extracted_text = match.group()
                result_list.append((extracted_text, filename))
                ####

        #print(result_list)

        return result_list

        
    


    def downloadFile(self, depot_file_path, local_file_path):

        # Define the depot file path of the file you want to download
        #depot_file_path = '//depot/path/to/your/file'

        # Define the local file path where you want to save the downloaded file
        #local_file_path = 'local_file_path'  # Replace with your desired local path

        res = False
        p4 = self.p4
        try:
            # Connect to the Perforce server
            p4.connect()

            # Run the 'print' command to download the file content
            result = p4.run('print', '-o', local_file_path, depot_file_path)

            print(f"File downloaded to {local_file_path}")
            res = True

        except Exception as e:
            print(f"Perforce error: {e}")

        finally:
            # Disconnect from the Perforce server
            p4.disconnect()

        return res    
    

   

#
# 
#     
if __name__ == "__main__":
    print(f"Start {__name__}")
    c = sydorP4()
    

    if 0:
        result_list = c.doScan()
        log_list_to_file_with_headers( result_list, 
                filename = "p4Files.csv",
                headers = ["Part#", "Path_on_P4"] )
    

    if 0:
        result_list = c.doScan()
        r = c.downloadFile( result_list[0][1], 'tempfile_p4' )
        
       

    if 1:        
        br = Baserow('', table_id = '546', base_url = "http://192.168.11.88:8080" )
        file = 'tempfile_p4.pdf'
        resp = br.uploadFile( file, '1')  # row_id = 1 hardcoded for testing

    print("Done.")
