#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog
import pdfplumber
import zipfile
import os,sys
import re
from lxml import etree
from bs4 import BeautifulSoup

#Split the filename and directory of th script file
script_files = os.path.abspath(__file__)
script_directory,script_filename = os.path.split(script_files)

def select_pdf_file():
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Select PDF File", "", "PDF Files (*.pdf)", options=options)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return file_path

#Define the function to find the pdf page number and find first line
def pdf_line(pdf_path):
    #Split the directory and filename
    directory,filename=os.path.split(pdf_path)
        
    #Split the file extension and and .txt extension
    output_file=os.path.splitext(filename)
    pageno_folder = script_directory+"/pageno/"
    #Create the pageno folder if it doesn't exist
    if not os.path.exists(pageno_folder):
        os.makedirs(pageno_folder)
    output_text=pageno_folder+output_file[0]+".txt"

    with pdfplumber.open(pdf_path) as pdf:
        numbers = 0
        line = ''
        num_pages = len(pdf.pages)  #Find number of pages in pdf
        #Loop through the each page
        for page_num in range(num_pages):
            page = pdf.pages[page_num]
            text = page.extract_text()
            first_line = text.split('\n')[0]  # Extract the first line
            digits = re.findall(r'\d+', first_line)  # Find all digits in the first line
            #Check the page is not empty
            if len(text.split('\n'))>1:
                second_line = text.split('\n')[1]  # Extract the second line
            else:
                second_line= ''

            #Find page number in top or bottom of the page
            if len(digits)==0 or page_num==0:
                last_line = text.split('\n')[-1]
                digits=re.findall(r'\d+', last_line) 
                if len(text.split('\n'))>1:
                    second_line = text.split('\n')[0]  # Extract the second line
                else:
                    second_line= ''

            if len(digits)==1:
                numbers = int(digits[0])
            elif len(digits)==0:
                numbers=int(numbers)+1
            else:
                numbers=int(numbers)+1
            #Add tag for pageno and text
            line+=f'<pageno>{numbers}</pageno><title>{second_line}</title>\n' 
        
    #Save the content in file
    with open(output_text, 'w') as file:
        file.write(line)

    return output_text

def run(bk):
    app = QApplication(sys.argv)
    pdf_file_path = select_pdf_file()

    if pdf_file_path:
        #Call the function
        output_text = pdf_line(pdf_file_path)
    else:
        print("No PDF file selected.")

    title_pattern = re.compile(r'<title>(.*?)</title>', re.IGNORECASE)
    pageno_pattern = re.compile(r'<pageno>(.*?)</pageno>', re.IGNORECASE)
    title_list=[]
    pageno_list=[]
    pageno_change=pageno_list
    pageno_store=[]

    with open(output_text, 'r') as file:
        # Read each line in the file
        for line in file:
            title_match = title_pattern.search(line)
            pageno_match = pageno_pattern.search(line)
            if title_match:
                # Process each line as needed
                title_text = title_match.group(1)  # Extract the text inside the title tag
                if title_text is not None:
                    title_list.append(title_text)
            if pageno_match:
                # Process each line as needed
                pageno_text = pageno_match.group(1)  # Extract the text inside the title tag
                if pageno_text is not None:
                    pageno_list.append(pageno_text)


    for (id, href) in bk.text_iter():
        filename = os.path.basename(id)  # Extract only the filename
        for char in filename:
            if char.isdigit():
                html = bk.readfile(id)
                soup = BeautifulSoup(html, 'html.parser')
                all_tags = soup.find_all()
                #print(all_tags)
                for tag in all_tags:
                    tag_string = str(tag)
                    if tag.name=="p" or tag.name=="li":
                        p_text = re.sub(r'<[^>]+>', '', tag_string)
                        if p_text is not None:
                            if len(title_list)!=0:
                                #Iterate through each title_list
                                for index, i in enumerate(title_list):
                                    if i.endswith("-"):
                                        i=i.split("-")
                                        i=i[0]
                                    if  "•" in i:
                                        i=i.replace("• ","")
                                    i=re.sub(r'^\d+\.+\s*',"",i)
                                    
                                    if len(i)>30:
                                        i=i[:30]
                                    if i!="":
                                        ref=i.split()
                                        reff=''
                                        if ref[0]==p_text: 
                                            i=ref[0]
                                        if len(ref)>3:
                                            reff=ref[0]+" "+ref[1]
                                            if reff==p_text:
                                                i=reff
                                        if i==p_text:
                                            if index!=0:
                                                pageno_list=pageno_list[index:]
                                                title_list=title_list[index:]
                                                pageno_store.append(pageno_list[0])
                                            tag_string = tag_string.split(i)
                                            new_text = f'{tag_string[0]}<span>{pageno_list[0]}</span>{i}{tag_string[1]}'
                                            new_text = re.sub(r'<\s*p[^>]*>', '',new_text)
                                            new_text = re.sub(r'<\s*/p[^>]*>', '',new_text)
                                            if index==0:
                                                pageno_store.append(pageno_list[0])
                                                pageno_list=pageno_list[index+1:]
                                                title_list=title_list[index+1:]
                                            tag.string = new_text
                                            break
                                        elif i in p_text:
                                            i=i.split()
                                            i_text=''
                                            for j in range(5):
                                                count=(tag_string.count(i[j]))
                                                i_text+=i[j]+" "
                                                if count==1:
                                                    break
                                            if index!=0:
                                                pageno_list=pageno_list[index:]
                                                title_list=title_list[index:]
                                                pageno_store.append(pageno_list[0])

                                            if i_text in tag_string:
                                                tag_string = tag_string.split(i_text)
                                                new_text = f'{tag_string[0]}<span>{pageno_list[0]}</span>{i_text}{tag_string[1]}'
                                                new_text = re.sub(r'<\s*p[^>]*>', '',new_text)
                                                new_text = re.sub(r'<\s*/p[^>]*>', '',new_text)
                                            else:
                                                new_text = f'<span>{pageno_list[0]}</span>{tag_string}'
                                                new_text = re.sub(r'<\s*p[^>]*>', '',new_text)
                                                new_text = re.sub(r'<\s*/p[^>]*>', '',new_text)

                                            if index==0:
                                                pageno_store.append(pageno_list[0])
                                                pageno_list=pageno_list[index+1:]
                                                title_list=title_list[index+1:]
                                            tag.string = new_text
                                            break
                
                
                bk.writefile(id, str(soup))
                #print(str(soup))
            
                # Write the updated content back to the file
                with open(filename, "w") as xhtml_f:
                    xhtml_f.write(str(soup))
                
                print("Updated content of file", filename, "to 'siva'")
                break

  

def main():
    print("This is a Sigil plugin and should not be run directly.")
    return -1

if __name__ == "__main__":
    sys.exit(main())
