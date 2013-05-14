import os
import subprocess
import csv
import math
import argparse
import time
import datetime

def create_output_destination(file_name,output_path):
    #create output template from supplied input file path
    base =  os.path.splitext(os.path.basename(file_name))[0]
    output_name_template = base+'_part_'
    
    #create output directory
    timestamp = int(time.time())
    output_dir = os.path.join(output_path,base,str(timestamp))
    if not os.path.exists(output_dir): 
    	os.makedirs(output_dir)
    
    return output_name_template,output_dir
    
def run_command(cmd_string):
    p = subprocess.Popen(cmd_string, stdout=subprocess.PIPE,shell=True)
    (output,err) = p.communicate()
    return output,err
    
def check_row_count(file_name):
    #get line count of original file
    word_count_cmd = "wc %s" % file_name
    output,err = run_command(word_count_cmd)
    totalrows = int(output.split()[0])
    #windows encoded csvs should have exactly one row
    if totalrows <= 1:
    	raise Exception('Unable to split, file has %s rows' % str(totalrows))
    	
    return None
    
def get_list_split_files(output_name_template, output_dir):
    output_list=[]
    #get line count of all files in output directory that match template
    get_files_command = 'wc %s*' % os.path.join(output_dir,output_name_template)
    output,err = run_command(get_files_command)
    
    list_of_result_rows = output.splitlines()
    
    #record filename, line count as well as the calculated row start position
    for each in range(len(list_of_result_rows)):
        line_count,word_count,char_count,filename = list_of_result_rows[each].split()
        if each == 0:
        	row_start = 1
        else:
        	row_start = output_list[each-1][1] * each + 1
        #if statement excludes 'total' row from command response	
        if output_name_template in filename.decode('utf-8'): 
        	output_list.append([filename.decode('utf-8'),int(line_count),row_start])
    
    return output_list

def split_file(file_name, delimiter=',', row_limit=10000, parts=0, output_path='.'):
    start_time = datetime.datetime.now()
    if parts:
        print('The file splitter starting at: '+str(start_time)[:-3]+' and splitting into '+str(parts)+' parts')
    else:
        print('The file splitter starting at: '+str(start_time)[:-3]+' and splitting into '+str(row_limit)+' rows per file')
    isValid = os.path.exists(file_name) and os.path.isfile(file_name)
    if isValid is False:
        raise Exception('File not found!')
    
    check_row_count(file_name)
    #open file
    filehandler = open(file_name,'r')
    
    #store header
    reader_obj = csv.reader(open(file_name))
    header = next(reader_obj)
    
    #create copy of csv without the header
    remove_header_cmd = "sed '1d' %s > noheaders.csv" % file_name
    run_command(remove_header_cmd)
    
    #if going by parts, get total rows and define row limit
    if parts > 0:
        word_count_cmd = "wc noheaders.csv"
        output,err = run_command(word_count_cmd)

        totalrows = int(output.split()[0])
        row_limit = math.ceil(totalrows / parts) # round up for row limit
    
    #set up output location
    output_name_template,output_dir = create_output_destination(file_name,output_path)
    
    #call unix split command
    split_command = 'split -a1 -l %d noheaders.csv %s' % (row_limit, os.path.join(output_dir,output_name_template))
    run_command(split_command)
    
    #clean up
    os.remove('noheaders.csv')
    
    #save headers to output dir
    header_path = os.path.join(output_dir, 'headers.csv')
    header_writer = csv.writer(open(header_path, 'w'), delimiter=delimiter)
    header_writer.writerow(header)
    
    split_file_list = get_list_split_files(output_name_template, output_dir)

    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    print('The file splitter completed at %s with an execution time of %s for %s rows into %s files' % (str(end_time)[:-3],str(execution_time)[:-3],totalrows,len(split_file_list)))
    return split_file_list, header_path

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process file splitter args')
    parser.add_argument('inputfile',help='input file path')
    parser.add_argument('-o','--output',default='.',help='output file path')
    
    #can split only by rows or parts, not both
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r','--rows',type=int,default=10000,help='number of rows per each output file')
    group.add_argument('-p','--parts',type=int,default=0,help='number of parts to split file into, regardless of rows')
    
    args = parser.parse_args()
    print("Input file is: "+args.inputfile)
    if args.output: 
    	print("Output file path is: "+args.output)
    if args.rows and args.parts == 0: 
    	print("Rows per output file: "+str(args.rows))
    if args.parts: 
    	print("Number of output files: "+str(args.parts))
    
    split_file(args.inputfile,row_limit=args.rows,parts=args.parts,output_path=args.output)
