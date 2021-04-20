# Install PyGithub
'''
DOC for PyGithub https://readthedocs.org/projects/pygithub/downloads/pdf/stable/
'''
from github import Github , GithubException
import argparse
# import urllib.request as urllib2
import requests
import os
from pathlib import Path
from zipfile import ZipFile
import datetime
import logging
from Simulinkrepoinfo import SimulinkRepoInfoController
import sys
import time
from subprocess import Popen, PIPE
logging.basicConfig(filename='github.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

class GithubRepoDownload():
	githubURL = "https://github.com"


	def __init__(self, dir_name, token,dbname,l_flag=False):
		'''
		:args:
			dir_name : Name /Path of the directory to store all the downloaded files .

		'''
		self.gObj = Github(token)
		self.l_flag = l_flag
		# TODOS
		# Maintains count of mdl or slx files stored in each project
		self.simulinkmodels_count = {}
		# Argument check if valid
		self.dir_name = dir_name
		# Database
		self.databaseHandler = SimulinkRepoInfoController(dbname)
		if not os.path.exists(self.dir_name):
			os.mkdir(self.dir_name)
			logging.info("Directory " + self.dir_name + " Created ")

		else:
			logging.info("Directory " + self.dir_name + " already exists")

	def getDownloadLink(self, repo):
		logging.info("Downloading repository '%s' from user '%s' ..." % (repo.name, repo.owner.login))
		linkToDownloadRepo = GithubRepoDownload.githubURL + "/" + \
							 repo.owner.login + "/" + repo.name + "/" + "archive" + "/" + "master.zip"
		return linkToDownloadRepo

	def getRepositoryFromAPI(self, query):
		# UPTO 1000 results for each search
		'''
		 https://help.github.com/en/github/searching-for-information-on-github/searching-for-repositories
		 :return:
		'''
		results = self.gObj.search_repositories(query, sort='updated')
		#self.gObj.search_commits()
		logging.info("Total Search Results for %s query : %s " % ( query,str(results.totalCount)))
		return results

	def saveZipFile(self, response, filename_with_path):

		filename = filename_with_path
		# Checking if file already exist #Redundant Check
		try:
			output = open(filename, "wb")
			output.write(response.content)
			output.close()
		except Exception as e:
			logging.info("Saving to disk Failed")
			logging.info(e)
			return False
		return True

	def getQueryDates(self, startDate):
		return startDate

	def get_version_sha(self,repo):
		repoLink = GithubRepoDownload.githubURL + "/" + \
							 repo.owner.login + "/" + repo.name + ".git"
		p = Popen(['git', 'ls-remote', repoLink, '|', 'grep', 'refs/heads/master'], stdout=PIPE)
		output = p.communicate()[0].decode("utf-8")
		return output.split("\t")[0]

	def downloadAllRepository(self, query):
		'''
		Download the repositories
		 30 requests per minute for using SEARCH API
		 HENCE TIMEOUT 60 Seconds between query

		:param query: query to download repositiory
		SEE https://help.github.com/en/github/searching-for-information-on-github/searching-for-repositories
		:return:
		'''

		prev_date = datetime.date(2010, 1, 1)
		interval = datetime.timedelta(365)
		latest_date = prev_date + interval
		logging.info("Latest Date : " + str(latest_date))
		tmp = query
		query = tmp + " created:" + str(prev_date) + ".." + str(latest_date)

		repositories = self.getRepositoryFromAPI(query)

		self.counter = 0
		self.skipped_counter_known = 0
		self.skipped_counter_license = 0
		self.skipped_counter_other_error = 0
		self.skipped_counter_no_mdl = 0
		self.download_counter = 0
		# Check count and adjust the date intervals |  TODO: Also Keep Track of rate limits DO TIMEOUT
		while repositories.totalCount > 0:
			for repo in repositories:

				self.counter  += 1
				logging.info("Search Result #%d: %s" %(self.counter, repo.name))
				if (repo.id in ( 157107577,203254778,227433411,43843825)): #project ID of  SLEMI, CYEMI's slearner, SLFORGE:
					logging.info("Skipping Known research projects")
					self.skipped_counter_known += 1
					continue
				logging.info("======START %d ========="%self.counter)
				download_url = self.getDownloadLink(repo)
				# Check the repo Id in the directory before downloading to avoid duplicates
				# Check If the filename exists before downloading
				# FileName is Id  as Id provided by Github are unique for two different repo
				filename_with_path = self.dir_name + "/" + str(repo.id) + ".zip"


				has_license = 0
				license_type = ""

				if os.path.isfile(filename_with_path):
					logging.info("File %s already exists" % repo.name +"__"+ str(repo.id))
					continue
				try:
					license_type = repo.get_license().license.name
					has_license = 1
					logging.info("License Type : "+repo.get_license().license.name)
				except Exception as e:
					#Skipping the repository since it doesnot have License
					if self.l_flag == True:
						self.skipped_counter_license += 1
						logging.info("Skipping the repository : %s since it does not have License" %repo.name)
						continue
					logging.info(e)



				# getting sha and download file
				version_sha = self.get_version_sha(repo)
				response = requests.get(download_url)
				# DONE # Writing to Database using SQL ALChemy
				# INFO to store :
				# project URL , Simulink Models in a Projects, Domain, Matlab Release, Requirements ,Version, has License , created and updated date,forked

				logging.info("Downloading Project via %s" %(download_url))
				'''latest_date = repo.updated_at.date()  # TODO Assert the order
				if not (prev_date >= latest_date):
					latest_date = prev_date
					print('This is worng %d', count)
				prev_date = latest_date
				print(latest_date)'''
				if(self.saveZipFile(response, filename_with_path)):
					# Check and Delete
					model_file_count,model_file_names = self.checkIfProjecthasSimulinkModel(repo)
					if model_file_count>0:
						self.write_to_database(repo, license_type,model_file_count,model_file_names,version_sha)
						self.download_counter += 1
					else:
						self.skipped_counter_no_mdl += 1
			logging.info("================Sleeping for 60 Seconds============")
			time.sleep(60)

			prev_date = prev_date + interval
			latest_date = latest_date + interval
			query = tmp + " created:" + str(prev_date) + ".." + str(latest_date)
			repositories = self.getRepositoryFromAPI(query)

	def checkIfProjecthasSimulinkModel(self, repo):
		'''
		checks if project contains slx or mdl files.
		If not deletes the project files  .
		Update Flag in the database with no relevant files in the download projects

		:return:
		'''
		projectname = str(repo.id)
		# print(os.path.join(os.getcwd(), self.dir_name, projectname + ".zip"))
		file = os.path.join(os.getcwd(), self.dir_name, projectname + ".zip")
		count = 0
		try:
			with ZipFile(file, 'r') as zipObj:
				# Get a list of all archived file names from the zip
				listOfFileNames = zipObj.namelist()
				fileName_csv =""
				# Iterate over the file namesclear
				for fileName in listOfFileNames:
					# print(fileName)
					if fileName.endswith(".slx") or fileName.endswith(".mdl"):
						count = count + 1
						fileName_csv=fileName+","+fileName_csv

				zipObj.close()
				if count > 0:
					self.simulinkmodels_count[projectname] = count
					#self.update_model_file_info_in_db(repo.id,{"model_files":fileName_csv})
					#self.update_model_file_info_in_db(repo.id, {"has_model_files":1})
					#self.update_model_file_info_in_db(repo.id,{"num_model_file":count})
					return  count, fileName_csv
				else:
					self.skipped_counter_other_error += 1
					#self.update_model_file_info_in_db(repo.id, {"has_model_files": 0})
					os.remove(file)
					logging.info("No Model Files : Deleting %s" % file)
					return 0,""
		except Exception as e:
			os.remove(file)
			logging.info(e)
			logging.info("Deleted  BAD File %s" %(file))
			return  0, ""

	def printDict(self):
		sum = 0
		for k, v in self.simulinkmodels_count.items():
			logging.info(k + " : ", str(v))
			sum = sum + v
		logging.info("Total Simulink models : " + str(sum))
		logging.info("Total Skipped Known : %d"%self.skipped_counter_known)
		logging.info("Total Skipped License : %d"%self.skipped_counter_license )
		logging.info("Total Skipped Other : %d"%self.skipped_counter_other_error )
		logging.info("Total Skipped No model files : %d"%self.skipped_counter_no_mdl )
		logging.info("Total Downloaded : %d"%self.download_counter)
		logging.info("Total Search Results : %d" % self.counter)

	def write_to_database(self, repo,license_type,no_of_model_file, model_file_csv,version_sha):
		'''
		Insert into Database
		:param repo:
		:param license_type:
		:param has_license:
		:return:
		'''
		topic = ",".join(repo.get_topics())
		if(topic != ""):
			logging.info("Topics : "+ topic)
		self.databaseHandler.insert(repo.id,repo.name,repo.owner.login,repo.private,
									repo.html_url, repo.description, repo.fork, repo.url,
									repo.created_at, repo.updated_at, repo.pushed_at,
									repo.homepage, repo.size,
									repo.stargazers_count, repo.watchers_count, repo.language,repo.forks_count,
			   						repo.open_issues_count, repo.master_branch, repo.default_branch,
									topic,license_type, model_file_csv, no_of_model_file,version_sha)



	def update_model_file_info_in_db(self,id, col_val):
		self.databaseHandler.update(id, col_val)


parser = argparse.ArgumentParser(description='Get argument for downloading')
parser.add_argument('-q', '--query', dest="query", type=str,
					help='https://help.github.com/en/articles/understanding-the-search-syntax')
parser.add_argument('-d', '--dir', dest="dir_name", type=str,
					help='Name of directory to store downloaded files ')
parser.add_argument('-db', '--dbname', dest="db_name", type=str,
					help='Name of sqlite database to store metadata files ')
parser.add_argument('-flag', '--license', dest="l_flag", type=bool,
					help='Boolean value to determine to include only those project with license| Dont include the file if downloading all projects')
parser.add_argument("-t", '--token', dest="token", type=str,
					help = 'https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line')
args = parser.parse_args()

query = args.query
dbname = args.db_name
l_flag = args.l_flag
logging.info("Query Argument: %s " % query)

token = "<YOUR_PERSONAL_ACCESS_TOKEN>"  # BASIC AUTH OR OAUTH 5000 requests per hour ||  30 requests per minute for using SEARCH API

gitObj = GithubRepoDownload(args.dir_name,token, dbname,l_flag)
gitObj.downloadAllRepository(query)

gitObj.printDict()

