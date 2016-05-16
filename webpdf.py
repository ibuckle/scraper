import requests
from bs4 import BeautifulSoup
from wkhtmltopdf import WKHtmlToPdf

class UL_Interogator(object):

	base_url = "http://database.ul.com"
	form_page = "/cgi-bin/XYV/cgifind/LISEXT/1FRAME/srchres.html"

	def __init__(self, file):

	# File that contains the list of CCNs and File Numbers

		self.file = file

	# These are the form fields that need to be send as post data to the page

		self.form_data = {
			'SORT_BY':'textlines:asc,ccnshorttitle:asc',
			'collection':'/data3/verity_collections/lisext',
			'vdkhome':'/pdm/tools/K2/k2/common',
			'query':'ccn<IN>CCN and filenmbr<IN>File_Number',
			'Company':'',
			'City':'',
			'State':'Select+a+state',
			'Zip':'',
			'Country':'=Select+a+country',
			'Region':'=Select+a+region',
			'Province':'=Select+a+province',
			'Postal':'',
			'CCN':'ccn',
			'Filenbr':'filenmbr',
			'Fulltext':''
		}

		self.search_param_list = []


	def import_from_file(self):

		"""
		Function to get data from the referenced file and return a list
		that contains lists of CCNs and UL file numbers to look up in the 
		OCD
		"""

		self.search_param_list = []	# This is overall list that I'm going to return, but I can't think of a good name for it.

		f = open("./" + self.file)		# Open the file with the data to check
		lines = f.readlines()		# Read the lines into an array
		f.close()

		for line in lines:

			search_params = line.split(",")		# split the csv lines into a list
			search_params = search_params[:2]
			self.search_param_list.append(search_params)
	

	def print_pdf(self):

		# print "Debug data from print_pdf function :\n"
		
		for search_param in self.search_param_list:

			self.form_data['CCN'] = search_param[0]
			self.form_data['Filenbr'] = search_param[1]

			# print "--------------------------"
			# print  "CCN: " + search_param[0] + " - " + "File Number: " + search_param[1]

			if search_param[0] != "" and search_param[1] != "":
				self.form_data['query'] = search_param[0] + "<IN>CCN and " + search_param[1] + "<IN>File_Number"
			elif search_param[0] =="" and search_param[1] != "":
				self.form_data['query'] = search_param[1] + "<IN>File_Number"
			else:
				return False
					
			# print search_data_base
			self.get_ul_page()

	def get_ul_page(self):

		search_url = self.base_url + self.form_page

		r = requests.post(search_url, self.form_data)
		html_doc = r.text

		# print "++++++++++++++++++++++++++++++"
		# print search_url

		url_list =[]

		soup = BeautifulSoup(html_doc, 'html.parser')

		result_string = soup.find_all('td')

		lines_with_urls = []

		for line in result_string:
			# print type(line.contents[0].name)

			if line.contents[0].find('script'):
				# print type(line.contents[0])
				tag_text = line.text
				# print "**********************************"
				# print tag_text
				lines_with_urls.append(tag_text)
			
		# print "finished"
		# print lines_with_urls[1]

		for line in lines_with_urls:
		
			pos_quote1 = line.find('"')
			pos_quote2 = line.find('"', pos_quote1+1)

			filename = line[pos_quote1+1:pos_quote2]

			# print filename
			if filename == "<B>Refine Your Search</B>.":
				continue

			line = line[(line.find('/')):]

			while (line.find('+') > 0):
				pos_quote1 = line.find('"')
				# print pos_quote1
				pos_quote2 = line.find('"', pos_quote1+1)
				# print pos_quote2
				start_of_line = line[:pos_quote1]
				end_of_line = line[pos_quote2+1:]
				# print start_of_line
				# print end_of_line
				line = start_of_line + end_of_line
				# print line

			pos_quote1 = line.find('"')
			line = line[:pos_quote1]

			while (line.find(' ')>0):
				pos_space = line.find(' ')
				start_of_line = line[:pos_space]
				end_of_line = line[pos_space+1:]
				line = start_of_line + '+' + end_of_line

			target = 'http://database.ul.com' + line

			# print "Final URL is : \n"
			# print target



			wkhtmltopdf = WKHtmlToPdf(
			    url=target,
			    output_file='./' + filename + '.pdf',
			)
			wkhtmltopdf.render()	


# *****************************************************************************************
# *****************************************************************************************

myInterogator = UL_Interogator('filecheck.txt')

myInterogator.import_from_file()

myInterogator.print_pdf()
