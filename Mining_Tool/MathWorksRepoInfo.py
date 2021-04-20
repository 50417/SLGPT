from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean,Float,TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, load_only
from datetime import datetime
Base = declarative_base()


class MathWorksRepoInfo(Base):
	'''
	model class for MathWorks File Exchange Repo Info

	'''
	__tablename__ = "MATC_Projects"
	id = Column('id', Integer, primary_key=True)
	repo_name = Column('title', String)
	owner = Column('author_name', String)
	repo_url = Column('mathworks_url', String)
	summary = Column('summary', String) # Brief summary
	content = Column('content', String) # Detailed Content of Summary
	category = Column('category', String)
	author_uri = Column('author_uri', String)
	created_at = Column('published', DateTime)
	updated_at = Column('updated', DateTime)

	no_of_comments = Column('no_of_comments', Integer)  # Forks
	no_of_ratings = Column('no_of_ratings', Integer)  # Favorites
	average_rating = Column('average_rating', Float) #Float
	downloads = Column('downloads', String)  # Domain


	download_link = Column('download_link', String)

	#has_license = Column('has_license', Boolean)
	license_type = Column('license', TEXT)

	model_files = Column('model_files', String)
	num_model_file = Column('num_model_file',Integer)

	def __init__(self, id, published, updated, mathworks_url, title, \
				  summary,content,author_name,author_uri,category,\
				  no_of_comments, no_of_ratings, average_rating ,downloads,download_link,\
                 #has_license,
				 license_type,model_files,num_model_file):

		self.id = id
		self.repo_name = title
		self.owner = author_name
		self.repo_url = mathworks_url
		self.summary = summary  # Brief summary
		self.content = content  # Detailed Content of Summary
		self.category = category
		self.author_uri = author_uri
		self.created_at = published
		self.updated_at = updated

		self.no_of_comments = no_of_comments  # Number of comments
		self.no_of_ratings = no_of_ratings
		self.average_rating = average_rating
		self.downloads =downloads  # Number of Download

		self.download_link = download_link

		#self.has_license = has_license
		self.license_type = license_type

		self.model_files = model_files
		self.num_model_file = num_model_file




class MathWorksRepoInfoController(object):
	def __init__(self,dbname):
		# In memory SQlite database . URI : sqlite:///:memory:
		# URL = driver:///filename or memory
		self.engine = create_engine('sqlite:///'+dbname+'.sqlite', echo=True) # Hard coded Database Name . TODO : Make it user configurable/
		#Create Tables
		Base.metadata.create_all(bind=self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def insert(self, id, published, updated, mathworks_url, title, \
				  summary,content,author_name,author_uri,category,\
				  no_of_comments, no_of_ratings, average_rating ,downloads,download_link,\
               #  has_license,
			   license_type,model_files,num_model_file):

		session = self.Session()
		tmpRepoInfo = MathWorksRepoInfo(id, published, updated, mathworks_url, title, \
				  summary,content,author_name,author_uri,category,\
				  no_of_comments, no_of_ratings, average_rating ,downloads,download_link,\
                 #has_license,
										license_type,model_files,num_model_file)
		session.add(tmpRepoInfo)
		session.commit()
		session.close()

	def update(self,id,col_val): #TODO: Table is fixed , Change it to user configurable tables
		'''

		:param id:
		:param col_val: is the dictionary with {coln : updated_val }
		:return:
		'''
		session = self.Session()
		session.query(MathWorksRepoInfo).filter_by(id=id).update(col_val) #{"name": u"Bob Marley"}

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
		result = session.query(MathWorksRepoInfo).options(load_only(col_name))#.filter_by(has_model_files=1)
		'''for row in x:
			print(row.model_files)
			count +=1
		'''
		session.close()
		return result


