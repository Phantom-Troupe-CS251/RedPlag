""" \package MOSS With Locations
Plagiarism detector for source code files.
Detects plagiarism using Karp Rabin Hashing and winnowing
Marks overlapping hashes to exactly show the parts which where copied
"""

import numpy as np
from pygments.lexers import guess_lexer_for_filename
import pygments
import sys
import os
from .graph_utils import *
from django.conf import settings

q=1000000007

def tokenize(filename):
	"""!
	\details Tokenises a file according to it's extension. Replaces all variable identifiers by V, function names by F and strings by S
		Other words are taken as it is
		Stores starting index of each token in original and final file
	\param filename: Name of file with correct extension
	\return mapping: a list of tokens of the form [token , start index in original file, start index in tokenised file]
	"""
	with open(filename, 'r', encoding = 'utf-8') as f:
		contents = f.read()
		tokens = list(guess_lexer_for_filename(filename, contents).get_tokens(contents))
		mapping = []
		n = len(tokens)
		
		a = 0
		b = 0
		
		for i in range(n):
			if tokens[i][0] == pygments.token.Name.Variable:
				mapping.append(['V', a, b])
				b = b + 1

			elif tokens[i][0] in pygments.token.Name.Function:
				mapping.append(['F', a, b])
				b = b + 1
			
			elif tokens[i][0] in pygments.token.Literal.String:
				mapping.append(['S',a,b])
				b = b + 1

			elif tokens[i][0] != pygments.token.Text and tokens[i][0] != pygments.token.Comment:
				mapping.append([tokens[i][1], a, b])
				b = b + len(tokens[i][1])
			a = a + len(tokens[i][1])
		return mapping

def intersection(lst1, lst2):
	"""!
        
	
	\details Finds hashes that are common to both lists and stores their location in both documents
	Finds similarity that is measured by 
	sim(A,B) = number of hashes in intersection of both hash sets divided by minimum of the number of hashes in lst1 and lst2
		
	\param  lst1 : 1st list whose elements are of the form [hash, start location, end location]
	\param lst2: 2nd list whose elements are of the form [hash, start location, end location]
	\return l3: list of common hashes and their locations in both documents. This is a list whose elements are of the form 
		[common hash, [start location in 1, end location in 1], [start location in 2, end location in 2]]
	\return sim: similarity measure evaluated
	"""

	intersect_with_loc_1 = []
	intersect_with_loc_2 = []
	for h1 in lst1:
                for h2 in lst2:
                        if h1[0] == h2[0]:
                                intersect_with_loc_1 += [[h1[1][0], h1[2][0]]]
                                intersect_with_loc_2 += [[h2[1][0], h2[2][0]]]

	intersect_with_loc_1.sort(key = lambda x : x[0])
	if len(intersect_with_loc_1) == 0: return 0, 0, [], []

	intersect_with_loc_1 = intersect_with_loc_1[1:]
	p_1= [intersect_with_loc_1[0]]

	for i in range(1, len(intersect_with_loc_1)):
		if intersect_with_loc_1[i][0] >= p_1[-1][0] and intersect_with_loc_1[i][1] > p_1[-1][1] and intersect_with_loc_1[i][0] <= p_1[-1][1]:
			p_1[-1] = [p_1[-1][0],intersect_with_loc_1[i][1]]
		else: p_1 += [intersect_with_loc_1[i]]

	intersect_with_loc_2.sort(key = lambda x : x[0])
	intersect_with_loc_2 = intersect_with_loc_2[1:]
	p_2= [intersect_with_loc_2[0]]

	for i in range(1, len(intersect_with_loc_2)):
		if intersect_with_loc_2[i][0] >= p_2[-1][0] and intersect_with_loc_2[i][1] > p_2[-1][1] and intersect_with_loc_2[i][0] <= p_2[-1][1]:
			p_2[-1] = [p_2[-1][0],intersect_with_loc_2[i][1]]
		else: p_2 += [intersect_with_loc_2[i]]

	sim_1 = len(intersect_with_loc_1)/len(lst1)
	sim_2 = len(intersect_with_loc_2)/len(lst2)
	return sim_1, sim_2 , p_1, p_2


def similarity(lst1, lst2):
	"""!
		\details Evaluates similarity as done in intersection function but doesn't return locations of common hashes
	"""
	l1h = [h[0] for h in lst1] 
	l2h = [h[0] for h in lst2]
	l3h = list(set(l1h)&set(l2h))
	sim = len(l3h)/min(len(set(l1h)), len(set(l2h)))
	return sim

def GetHLoc(t,k):
	"""!
       
        
	\details Reads the file and tokenises it. Evaluate its k-grams. 
	For each k-gram, Karp-Rabin hash value is evaluated and stored in a list H. Along with the hashes, the location information given by start and end location of the k-gram in both initial and tokenized files are stored
	
	\param t: file name
	\param k: k-gram parameter
	
	\return H: The list H of hashes with their locations
	"""
	H = []
	mapping = tokenize(t)
	current_length = 0
	kgram = ""
	kgrams = []
	start_locs = []
	end_locs = []
	i = 0

	while i < len(mapping):
		if kgram == "":
			start_locs += [[mapping[i][1], mapping[i][2]]]

		if current_length + len(mapping[i][0]) > k:
			deficit = k - current_length
			kgram = kgram + mapping[i][0][:deficit]
			kgrams += [kgram]
			end_locs += [[mapping[i][1], mapping[i][2]]]
			mapping[i][0] = mapping[i][0][deficit:]
			current_length = 0
			kgram = ""

		elif current_length + len(mapping[i][0]) == k:
			kgram = kgram + mapping[i][0]
			kgrams += [kgram]
			end_locs += [[mapping[i][1], mapping[i][2]]]
			current_length = 0
			kgram = ""
			i = i + 1

		else:
			kgram = kgram + mapping[i][0]
			current_length += len(mapping[i][0])
			i = i + 1
			if i == len(mapping):
				kgrams += [kgram]
				end_locs += [[mapping[i-1][1], mapping[i-1][2]]]

	for j in range(len(kgrams)):
		h = 0
		for k in kgrams[j]: h = (256*h + ord(k))%q
		H.append([h,start_locs[j], end_locs[j]])
	return H
    
    

def Win(H,t,k):
	"""!
        \details Applies Winnowing algorithm on given list of hashes with a window size such that for every substring of length t we will pick atleast one hash.
        Also stores the locations of selected hashes
        \param H: List of (hash, document ID, location)
        \param t: Winnowing threshold parameter
        \param k: k-gram parameter used while calculating hashes
        \return HS: Selected (winnowed) hashes
	"""
	HS=[]
	w=t+1-k
	n=len(H)
	mI=-1
	pmI=-1
	if len(H) < w: HS.append(H[0])
	for i in range(0,len(H)-w+1):
		tm=9223372036854775807
		for j in range(i, i+w):
			if H[j][0]<=tm:
				mI=j
				tm=H[j][0]
		if mI != pmI:
			pmI=mI
			HS.append(H[mI])
	return HS
		

		
def moss_all_pairs(folder_path, files, t, k):
	"""!
        \details Evaluates MOSS similarity and matching portions between each pair of files
        \param files: list of files
        \param t: Winnowing threshold parameter
        \param k: k-gram parameter
        \return C: similarity matrix such that C[i][j] denotes the similarity between the ith and jth file
        \return markings: markings matrix such that markings[i][j] is a list of charavter indices where matching k-grams begin for ith and jth file"""
	
	n = len(files)
	H = [GetHLoc(f,k) for f in files]
	HS = [Win(h,t,k) for h in H]

	C = np.identity(n)
	markings = []
	for i in range(n):
		marks = []
		for j in range(n):
			marks += [[]]
		markings += [marks]
	
	for i in range(n):			
		for j in range(i+1, n):
			simi, simj, pi, pj = intersection(HS[i], HS[j])
			C[i][j] = simi
			C[j][i] = simj
			markings[i][j] += pi
			markings[j][i] += pj				

	for i in range(n):
		for j in range(n):
			infile = open(files[i], 'r',encoding = 'utf-8').read()
			if not os.path.exists(folder_path + 'locations/'):
                                os.makedirs(folder_path + 'locations/' )
			match = open(folder_path + 'locations/' + "match" + str(i)+"_"+str(j), "w+")
			pp=markings[i][j]
			space=0
			for pr in pp:
				start=infile[0:pr[0]+space]
				middle=infile[pr[0]+space:pr[1]+space+1]
				end=infile[pr[1]+1+space:]
				infile=start+"\033[1;42m" + middle + "\033[0m"+end
				space=space+12
			match.write(infile)

	return C

def moss_given_files(zip_dir):
    initial_path = os.getcwd()
    print(os.getcwd())
    os.chdir(settings.BASE_DIR)
    basename = os.path.basename(zip_dir).split('.')[0]
    folder_path = settings.MEDIA_ROOT + '/' + basename + '/'
    other_things = settings.MEDIA_ROOT + '/' + basename + 'other/'

    with zipfile.ZipFile(zip_dir,'r') as zip_ref: 
        zip_ref.extractall(folder_path)

    ## \var list $files
    ## List of files in folder which is being queried

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path,f))]

    ## \var list $paths
    ## List of paths of each file

    paths = []

    for f in files:
        paths.append(folder_path + "/" + f)

    num_files = len(files)
    ## \var $dict $num_to_files
    ## Mapping of index of file to file name
    num_to_files = {}


    for i in range(len(files)):
        num_to_files[i] = files[i]

    ## \var np.darray $correlation_matrix
    ## Similarity matrix between files
    correlation_matrix = moss_all_pairs(other_things, paths, 4,3)
    print(correlation_matrix)
    
    histogram(correlation_matrix,other_things)
    plot_heat_map(correlation_matrix,files,other_things)
    save_csv_file(correlation_matrix,num_to_files,other_things)

    os.chdir(settings.MEDIA_ROOT)
    print(os.getcwd())
    if os.path.isfile(basename + 'other' + '.zip'): os.remove(basename + 'other' + '.zip')

    zipf = zipfile.ZipFile(basename + 'other' + '.zip','w',zipfile.ZIP_DEFLATED)
    zipdir(basename + 'other/', zipf)
    zipf.close()
    print(os.getcwd())
    os.chdir(initial_path)
    os.chdir(settings.BASE_DIR)
    print(os.getcwd())
