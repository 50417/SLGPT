import os
import re
import argparse
def combine_all_mdl_files(sys):
	output_file = "training.txt"
	head,tail = os.path.split(sys)
	allfile = open(os.path.join(head,output_file),"w")
	cnt = 0 
	for file in os.listdir(sys):
		print(cnt)
		with open(os.path.join(sys,file),'r') as f:
			#print(f.read())
			result = f.read().strip()
			result = re.sub('\t',' ',result)
			result = re.sub(' +',' ',result)
			
			#result = result.replace(file.split('.')[0],'toy')
			allfile.write(result)
		cnt += 1
		allfile.write("\n<|endoftext|>\n")
	allfile.close()

parser = argparse.ArgumentParser(
    description='combine-all-model-to-single-file',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dataset_dir', metavar='PATH', type=str, required=True, help='directory')
args = parser.parse_args()
combine_all_mdl_files(args.dataset_dir)
