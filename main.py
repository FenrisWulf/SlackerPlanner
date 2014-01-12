import re 
import string	
import io
import operator
from operator import itemgetter, attrgetter
import HTML
import xml.etree.ElementTree as ET
import urllib2
from cgi import escape
import sys, os
def getCoursesForParameters(year, dist, d1List, d2List, d3List):
	httpCall="http://courses.rice.edu/admweb/!SWKSECX.main?term=201320&title=&course=&crn=&coll=&dept=&subj=COMP"
	response = urllib2.urlopen(httpCall)
	root = ET.fromstring(response.read())
	for course in root:
		group = course.find("distribution-group")
		if group != None:
			if "Distribution Group I" in group.text and "II" not in group.text:
				d1List.append(course)
				print group.text
			if "Distribution Group II" in group.text and "III" not in group.text:
				d2List.append(course)
			if "Distribution Group III" in group.text:
				d3List.append(course)
	print d3List
	
def getData(): 
	lines=[]
	f = open("C:\Users\DavidNichol\Documents\Programs\Python\CourseEvals\data.txt", "r")

	for st in f:
		aList = st.strip().split(', ')
		lines.append(aList)
	f.close()
	lines.sort(key=itemgetter(1))
	return lines

def getDataForCourses(data, courses):
	resultList = []
	addedCourses = []
	for dat in data:
		for course in courses:
			courseName = course.find("subject").text + " " + course.find("course-number").text
			crn = course.find("crn").text
			if dat[0] == courseName and not crn in addedCourses:
				addedCourses.append(crn);
				dataToDisplay=(dat[0], dat[1], crn);
				resultList.append(dataToDisplay)
	return resultList

		
def dataToHTML(data):
	headerInfo = ("Course name", "Difficuilty", "CRN")
	data.insert(0, headerInfo)
	htmlcode = HTML.table(data)
	tr = 0
	returnLines = ""
	for line in htmlcode.split('\n'):
		moddedLine = line
		if (line.strip() =="<TR>"):
			tr = tr + 1
			if (tr % 2 == 0):
				moddedLine = "<TR class=\"alt\">\r\n"
			else:
				moddedLine = line

		returnLines = returnLines + moddedLine
	return returnLines

def getHeader():

	return '<p>Semester<br><select id="semesterDropDown"><option value="none">None</option><option value="201310" selected="selected">Spring 2013</option></select><p>Distribution Group<br><select id="ddlMyList"><option value="none">None</option><option value="d1.html" selected="selected">I</option><option value="d2.html">II</option><option value="d3.html">III</option></select><button type="button" onclick="navigateToSite()">Click Me!</button><script>function navigateToSite(){var ddl = document.getElementById("ddlMyList");var semDD = document.getElementById("semesterDropDown"); var selectedVal = "../"+semDD.options[semDD.selectedIndex].value+"/"+ddl.options[ddl.selectedIndex].value;window.location = selectedVal;}</script>'

def printToHTML(html, filename):
	f = open(filename, 'w')
	f.write("<html><body>")
	f.write(getHeader())
	f.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"stylesheet.css\">")
	f.write(html)
	f.write("</body></html>")
	f.close()
	
def main():
	year="201310"
	d1List = []
	d2List = []
	d3List = []
	
	getCoursesForParameters(year, 1, d1List, d2List, d3List);
	data = getData()

	#get d1
	distributionCourses = getDataForCourses(data, d1List)
	html = dataToHTML(distributionCourses)
	printToHTML(html, year+"/d1.html")

	#get d2
	distributionCourses = getDataForCourses(data, d2List)
	html = dataToHTML(distributionCourses)
	printToHTML(html, year+"/d2.html")
	
	#get d3
	distributionCourses = getDataForCourses(data, d3List)
	html = dataToHTML(distributionCourses)
	printToHTML(html, year+"/d3.html")
main()