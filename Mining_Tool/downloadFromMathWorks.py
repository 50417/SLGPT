# Python code to illustrate parsing of XML files
# importing the required modules
import csv
import requests
import xml.etree.ElementTree as ET
import logging
import os
from datetime import datetime
from zipfile import ZipFile
from MathWorksRepoInfo import MathWorksRepoInfoController
import sys

logging.basicConfig(filename='mathworksfileexchange.log', filemode='a',
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

class MathWorksFECRepoDownload():
	def __init__(self, url,dbname):
		'''

		:param url: RSS Feed URL
		:arg
		xml_tmp_file : file to store the RSS feed info
		'''
		self.models_meta_data = []
		self.url = url
		self.xml_temp_file = "rss_mathworks.xml"  # To Store RSS feed temporarily
		self.cannot_download_count = 0  # ill formed download links that lead to 404 page
		self.simulinkmodels_count = {}  # number of mdl or slx format
		# Database
		self.databaseHandler = MathWorksRepoInfoController(dbname)
		self.max_version = 10 #Used while constructing URL . Version of the project.
		# self.default_ns= "http://www.w3.org/2005/Atom"
		# self.namespace= {
		#                "openSearch" :"http://opensearch.a9.com/spec/opensearchrss/1.0/" ,
		#                "media":"http://search.yahoo.com/mrss/", "mw":"https://www.mathworks.com/"}

	def remove_namespace(self, file_content):
		'''
		Removes namespaces in RSS feed to make it easier to parse it using ElementTree
		:param file_content: content obtained from RSS feed
		:return: updated content removing all namespaces
		'''
		logging.info("Name space Content Found at Index : " + str(
			file_content.find(b'<feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom">')))

		file_content_wo_ns = file_content.replace(b'<feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom">',
												  b'<feed xml:lang="en-US">')
		file_content_wo_ns = file_content_wo_ns.replace(b'openSearch:', b'')
		file_content_wo_ns = file_content_wo_ns.replace(b'media:', b'media')
		file_content_wo_ns = file_content_wo_ns.replace(b'mw:', b'')
		return file_content_wo_ns

	def loadRSS(self, url):
		'''
		write the RSS feed on a predefined tmp file
		:param url: RSS feed url
		:return: True or False
		'''
		response = requests.get(url)

		with open(self.xml_temp_file, 'wb') as f:
			xml_content = self.remove_namespace(response.content)
			'''
			# Adding NameSpaces Missing from the file
			resp_content=resp_content.replace(b'<feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom">',
								 b'<feed xml:lang = "en-US" \
										 xmlns = "http://www.w3.org/2005/Atom"\
										 xmlns:openSearch = "http://opensearch.a9.com/spec/opensearchrss/1.0/"\
										 xmlns:media = "http://search.yahoo.com/mrss/"\
										 xmlns:mw = "https://www.mathworks.com/" >')
										 '''

			f.write(xml_content)
		f.close()
		return True

	def parseXML(self):
		'''
		parses RSS feed xml to collect meta data info
		:return: next page url for the RSS feed  parsed from current RSS feed
		'''
		tree = ET.parse(self.xml_temp_file)  # gets tree structure of xml
		root = tree.getroot()

		no_of_files = 0
		# Iterate over Entries
		for entry in root.findall('entry'):
			meta_data = {}
			download_link = '/'  # construct a download link for each repo
			category = ''

			logging.info("==========START OF ENTRY========== ")
			logging.info("MathWorks RSS Feed Url : " + self.url)
			# iterate over element of entry
			for item in entry:
				if item.tag == "link":
					meta_data['mathworks_url'] = str(item.attrib['href'])
					logging.info('Project Source :' + meta_data['mathworks_url'])
				elif item.tag == 'author':
					meta_data['author_name'] = item.find('name').text.encode('utf8').decode()
					meta_data['author_uri'] = item.find('uri').text.encode('utf8').decode()
					logging.info('Author Name :' + meta_data['author_name'])
					logging.info('Author URI :' + meta_data['author_uri'])

				elif item.tag == 'mediacontent':

					download_link = download_link.join(item.attrib['url'].split('/')[:-2])

					if download_link.find("versions") > 0:
						download_link = "https://www.mathworks.com" + download_link + "/"+str(self.max_version)+"/download/zip"
					elif download_link.find('mlc-downloads') > -1:
						download_link = "https://www.mathworks.com" + download_link + "/packages/zip"
					else:
						download_link = "https://www.mathworks.com" + download_link + "/mlc-downloads/downloads/submissions/" + \
										meta_data['id'].decode() + "/versions/"+str(self.max_version)+"/download/zip"

					meta_data["download_link"] = download_link
					logging.info('Download Link :' + download_link)
				elif item.tag == 'mediathumbnail':
					continue
				elif item.tag == "statistics":
					meta_data['no_of_comments'] = float(item.get('comments'))
					meta_data['downloads'] = float(item.get('downloads'))
					meta_data['no_of_ratings'] = float(item.get('ratings'))
					meta_data['average_rating'] = float(item.get('average'))
					logging.info('No of comments : %d\n No fo downloads : %d\n No of ratings %d\n Average Ratings : %d' \
								 % (meta_data['no_of_comments'], meta_data['downloads'], meta_data['no_of_ratings'],
									meta_data['average_rating']))

				elif item.tag == "category":
					if category == '':
						category = item.attrib['term']
					else:
						category = category + ',' + item.attrib['term']
				elif item.tag == "published" or item.tag== "updated":
					date = item.text.encode('utf8').decode().replace('T',' ').replace('Z',' ').strip()

					meta_data[item.tag] = datetime.strptime( date,"%Y-%m-%d %H:%M:%S")


				elif (item.tag == "content"):
					meta_data[item.tag] = item.text.encode('utf8').decode()
				else: #tags are id , published, created
					meta_data[item.tag] = item.text.encode('utf8')
					logging.info(str(item.tag) + ":" + str(meta_data[item.tag]))

			meta_data['category'] = category
			logging.info('Category: ' + meta_data['category'])
			logging.info("==========END OF ENTRY========== ")
			self.models_meta_data.append(meta_data)
		return self.find_next_page_url(root)

	def savetoCSV(self, filename):
		# specifying the fields for csv file
		fields = ['id', 'published', 'updated', 'mathworks_url', 'title', \
				  'summary', 'content', 'author_name', 'author_uri', 'category', \
				  'no_of_comments', 'no_of_ratings', 'average_rating', 'downloads', 'download_link']

		# writing to csv file
		with open(filename, 'w') as csvfile:
			# creating a csv dict writer object
			writer = csv.DictWriter(csvfile, fieldnames=fields)

			# writing headers (field names)
			writer.writeheader()

			# writing data rows
			writer.writerows(self.models_meta_data)

	def collect_model_metadata(self):
		'''
		Fetches RSS feed and collect metadata from the metrics.
		:return:
		'''
		start_time = datetime.now()
		logging.info('Start Time : ' + str(start_time))
		logging.info("Collecting Models Meta Data")
		while (self.url != ''):
			self.loadRSS(self.url)
			self.url = self.parseXML()
		self.savetoCSV('test.csv')
		end_time = datetime.now()
		logging.info('End Time : ' + str(end_time))
		logging.info("Time taken to collect Meta Data " + str(end_time - start_time))

		logging.info("Meta data collected for %s projects "%len(self.models_meta_data))
		logging.info("Time taken to collect Meta Data " + str(end_time - start_time))
		return self.models_meta_data

	def find_next_page_url(self, root):
		'''

		:param root: ElementTree object. Tree's root of xml
		:return: next page url of RSS feeds
		'''
		next_page_url = ''
		for link in root.iter('link'):
			if link.get('rel') == "next":
				next_page_url = "https://www.mathworks.com" + link.get('href')
		logging.info("Next Page Url : " + next_page_url)
		return next_page_url

	def download_models(self, models_meta_data,
						dir_name):
		'''
		Downloads the models based on model metric collected earlier.
		Check License | Check mdl or slx files | Write to DataBase
		:param models_meta_data:
		:param dir_name: Directory of where to store the downloaded files
		:return:
		'''
		start_time = datetime.now()
		logging.info('Start Time : ' + str(start_time))
		self.counter = 0
		#Create  a directory
		if not os.path.exists(dir_name):
			os.mkdir(dir_name)
			logging.info("Directory " + dir_name + " Created ")
		else:
			logging.info("Directory " + dir_name + " already exists")

		for metadata in models_meta_data:
			logging.info("===============START %d==============="%self.counter)
			self.counter+=1
			fileName_csv =''
			unique_file_name = str(metadata['id'].decode())
			logging.info("Checking if the file %s is already downloaded " %metadata['title'])
			if os.path.isfile(os.path.join(os.getcwd(),dir_name, unique_file_name + ".zip")):
				logging.info("File already exists")
				logging.info("File %s already exists" %unique_file_name)
				continue

			logging.info("Downloading %s : " % metadata['title'])
			logging.info("Downloading %s : " % metadata['title'])
			# download  file
			response = requests.get(metadata['download_link'])
			if response.status_code != 200:
				tmpcount = self.max_version #Version  of the projects
				while response.status_code != 200 and tmpcount <= 10 and tmpcount>0:
					tmpcount -= 1
					logging.info("Download Fail. Trying alternative Url: ")
					alternative_download_link = (metadata['download_link']).replace('/10/', '/' + str(
						tmpcount) + '/')
					logging.info("Downloading from URL : %s" % alternative_download_link)
					response = requests.get(alternative_download_link)
			else:
				logging.info("Downloading from URL : %s" % (metadata['download_link']))

			# TODO: TRY CATCH
			self.saveZipFile(response, unique_file_name, dir_name)
			fileName_csv = self.checkIfProjecthasSimulinkModel(unique_file_name, dir_name)
			if fileName_csv != '':
				license_content = self.checkIfProjecthasLicense(unique_file_name, dir_name)
				if license_content == "N/A":
					continue
				self.write_to_database(metadata, license_content,fileName_csv,len(fileName_csv.split(","))-1)#, has_license = 1 if license_content != "N/A" else 0)


		end_time = datetime.now()
		logging.info('End Time : ' + str(end_time))
		logging.info("Number of File that couldn't be downloaded  : %s" %(self.cannot_download_count))
		logging.info("Time taken to download file " + str(end_time - start_time))
		self.printDict()


	def write_to_database(self, repo, license_content,list_of_mdl_file,num_of_modelfile):#, has_license):
		'''
		Insert into Database
		:param repo:
		:param license_type:
		:param has_license:
		:return:
		'''
		self.databaseHandler.insert(int(repo['id'].decode()), repo['published'], repo['updated'], \
									repo['mathworks_url'], repo['title'].decode(),repo['summary'].decode(),\
									repo["content"], repo["author_name"],repo["author_uri"],\
								repo["category"], int(repo["no_of_comments"]), int(repo["no_of_ratings"]), \
									int(repo["average_rating"]),int(repo["downloads"]), repo["download_link"],\
									#has_license,
									license_content, list_of_mdl_file, num_of_modelfile)

	def saveZipFile(self, response, repo_name, dir_name):
		filename = dir_name + "/" + repo_name + ".zip"
		output = open(filename, "wb")
		output.write(response.content)
		output.close()
		return True

	def checkIfProjecthasLicense(self, file_name, dir_name):
		'''
		checks if project contains slx or mdl files.
		If not deletes the project files  .

		:return: boolean value
		'''

		file = os.path.join(os.getcwd(), dir_name, file_name + ".zip")
		count = 0
		with ZipFile(file, 'r') as zipObj:
				# Iterate over the file names
				for fileName in  zipObj.namelist():
					# print(fileName)
					if fileName == 'license.txt':
						with zipObj.open(fileName) as f:
							return f.read()
		os.remove(file)
		logging.info("Deleted  File: %s as it has no license file" % (file))
		logging.info("Deleted  File: %s as it has no license file" % (file))
		return "N/A"



	def checkIfProjecthasSimulinkModel(self, file_name, dir_name):
		'''
		checks if project contains slx or mdl files.
		If not deletes the project files  .

		:return: list of simulink model files
		'''

		file = os.path.join(os.getcwd(), dir_name, file_name + ".zip")
		count = 0
		try:
			with ZipFile(file, 'r') as zipObj:
				# Get a list of all archived file names from the zip
				listOfFileNames = zipObj.namelist()
				fileName_csv = ""
				license_file = False
				# Iterate over the file namesclear
				for fileName in listOfFileNames:
					# print(fileName)
					if fileName.endswith(".slx") or fileName.endswith(".mdl"):
						count = count + 1
						fileName_csv = fileName + "," + fileName_csv

				if count > 0:
					self.simulinkmodels_count[file_name] = count
					return fileName_csv
				else:
					# self.update_model_file_info_in_db(repo.id, {"has_model_files": 0})
					os.remove(file)
					logging.info("Deleted %s as it does not contain mdl or slx file or license File" % file)
					return ""
		except Exception:
			logging.exception(Exception)
			self.cannot_download_count += 1
			os.remove(file)
			logging.info("Deleted  bad File: %s" % (file))
			return ""

	def printDict(self):
		sum = 0
		for k, v in self.simulinkmodels_count.items():
			sum = sum + v
		logging.info("Total Simulink models : " + str(sum))


if __name__ == "__main__":
	directory = "dir_to_download" #UPDATE
	dbname = "xyz" #UPDATE
	rss_url = 'https://www.mathworks.com/matlabcentral/fileexchange/feed?product_family%5B%5D=simulink&type%5B%5D=models' #UPDATE
	# rss_url = 'https://www.mathworks.com/matlabcentral/fileexchange/feed?source%5B%5D=community&type%5B%5D=models'
	# rss_url = 'https://www.mathworks.com/matlabcentral/fileexchange/feed?category%5B%5D=215'

	# calling main function
	tmp = MathWorksFECRepoDownload(rss_url
		,dbname)
	models_meta_data = tmp.collect_model_metadata()
	tmp.download_models(models_meta_data, directory)
