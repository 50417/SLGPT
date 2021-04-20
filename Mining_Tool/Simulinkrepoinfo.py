from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
Base = declarative_base()


class SimulinkRepoInfo(Base):
	'''
	model class for Simulink Repo Info
	'''
	__tablename__ = "GitHub_Projects"

	id = Column('id', Integer, primary_key=True)
	repo_name = Column('repo_name', String)
	owner = Column('owner_name', String)
	is_private = Column('is_private', Boolean)
	html_github_url = Column('project_url', String)
	description = Column('Description', String)
	is_forked = Column('is_forked', Boolean)
	api_url = Column('api_url', String)

	created_at = Column('created_at', DateTime)
	updated_at = Column('updated_at', DateTime)
	pushed_at = Column('pushed_at', DateTime)

	homepage = Column('homepage_url', String)

	size_in_kb = Column('size_in_kb', Integer)

	stargazers_count = Column('stargazers_count', Integer)  # Favorites
	watchers_count = Column('watchers_count', Integer)
	language = Column('language', String)
	forks_count = Column('forks_count', Integer)  # Forks

	open_issues_count = Column('open_issues_count', Integer)
	master_branch = Column('master_branch', String)
	default_branch = Column('default_branch', String)
	topics = Column('Topics', String)  # Domain


	license_type = Column('license', String)
	model_files = Column('model_files', String)
	num_model_file = Column('num_model_file',Integer)
	version_sha = Column('version_sha', String)

	def __init__(self, id, repo_name, owner, is_private ,
				 html_github_url, description, is_forked, api_url,
				 created_at, updated_at, pushed_at,
				 homepage, size,
				 stargazers_count, watchers_count,language,forks_count,
				 open_issues_count , master_branch, default_branch,
				 topics,license_type,
			     model_files,num_model_file,version_sha):
		self.id = id
		self.repo_name=repo_name
		self.owner = owner
		self.is_private = is_private
		self.html_github_url=html_github_url
		self.description = description


		self.is_forked = is_forked
		self.api_url = api_url
		self.created_at = created_at
		self.updated_at = updated_at
		self.pushed_at = pushed_at

		self.homepage = homepage
		self.size = size


		self.forks_count=forks_count
		self.stargazers_count=stargazers_count
		self.watchers_count=watchers_count

		self.open_issues_count = open_issues_count
		self.master_branch = master_branch
		self.default_branch = default_branch

		self.topics = topics



		self.language = language
		#self.has_license = has_license
		self.license_type = license_type
		#self.has_model_files = has_model_files
		self.model_files = model_files
		self.num_model_file = num_model_file
		self.version_sha = version_sha



class SimulinkRepoInfoController(object):
	def __init__(self,db_name):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+db_name+'.sqlite', echo=True) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, id, repo_name, owner, is_private ,
				 html_github_url, description, is_forked, api_url,
				 created_at, updated_at, pushed_at,
				 homepage, size,
				 stargazers_count, watchers_count,language,forks_count,
				 open_issues_count , master_branch, default_branch,
				 topics,license_type,
			     model_files,num_model_file,version_sha):
		'''
		creates a session and object to insert the values
		need to implement error handling
		:param id:
		:param repo_name:
		:param owner:
		:param html_github_url:
		:param language:
		:param forks_count:
		:param stargazers_count:
		:param watchers_count:
		:param topics:
		:param created_at:
		:param updated_at:
		:param has_license:
		:param has_model_files:
		:param model_files:
		:return:
		'''
		session = self.Session()
		tmpSimulinkRepoInfo = SimulinkRepoInfo( id, repo_name, owner, is_private ,
				 html_github_url, description, is_forked, api_url,
				 created_at, updated_at, pushed_at,
				 homepage, size,
				 stargazers_count, watchers_count,language,forks_count,
				 open_issues_count , master_branch, default_branch,
				 topics,license_type,
			     model_files,num_model_file,version_sha)
		session.add(tmpSimulinkRepoInfo)
		session.commit()
		session.close()

	def update(self,id,col_val): #TODO: Table is fixed , Change it to user configurable tables
		'''

		:param id:
		:param col_val: is the dictionary with {coln : updated_val }
		:return:
		'''
		session = self.Session()
		session.query(SimulinkRepoInfo).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

		session.commit()
		session.close()

	def delete(self):
		pass

	def select(self,col_name,where_clause=None): #TODO : Support for where clause AND REMOVE HARDCODED VALUES
		'''

		:param col_name:
		:param where_clause:
		:return: object corresponding to the class : Load_only(col_name) restricts objects attributes
		'''
		session = self.Session()
		count = 0
		result = session.query(SimulinkRepoInfo).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result


