


import os 

prefix_path_template = os.path.join(os.path.dirname(__file__),'template')


path_template_rawdetail = os.path.join(prefix_path_template,'rawdetail.html')
path_template_electronic = os.path.join(prefix_path_template,'electronic.html')
path_template_escape = os.path.join(prefix_path_template,'escape.html')
path_template_formatdetail = os.path.join(prefix_path_template,'formdetail.html')
path_template_case_search = os.path.join(prefix_path_template,'case_search.html')



if __name__ == "__main__":
    print(prefix_path_template)