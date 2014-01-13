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
def getCoursesForParameters(year, allList, d1List, d2List, d3List):
	httpCall="http://courses.rice.edu/admweb/!SWKSECX.main?term="+year+"&subj=COMP"
	response = urllib2.urlopen(httpCall)
	root = ET.fromstring(response.read())
	for course in root:
		group = course.find("distribution-group")
		allList.append(course)
		if group != None:
			if "Distribution Group I" in group.text and "II" not in group.text:
				d1List.append(course)
			if "Distribution Group II" in group.text and "III" not in group.text:
				d2List.append(course)
			if "Distribution Group III" in group.text:
				d3List.append(course)
	
def getData(year, type): 
	lines=[]
	
	f = open(".\\"+year+type+".txt", "r")

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
			courseName = course.find("subject").text + " " + course.find("course-number").text + " "+course.find("section").text
			
			crn = course.find("crn").text
			if dat[0] == courseName and not crn in addedCourses:
				addedCourses.append(crn);
				
				timeText = ""
				if not course.find("meeting-days") == None:
					timeText = timeText + course.find("meeting-days").text + " " 
				if not course.find("start-time") == None:
					timeText = timeText + course.find("start-time").text
				if not course.find("end-time") == None:
					timeText = timeText + "-"+course.find("end-time").text
				instructorText = ""
				if not course.find("instructor") == None:
					instructorText = course.find("instructor").text;
				dataToDisplay=(dat[0], course.find("title").text.title(), dat[1], crn, instructorText, timeText);
				resultList.append(dataToDisplay)
	return resultList

		
def dataToHTML(data, type):
	headerInfo = ("Course", "Name", type.title(), "CRN", "Instructor", "Time")
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

def getYearForNumber(num):
	result = ""
	if num[-2:] == "10":
		result = result + "Fall "
	if num[-2:] == "20":
		result = result + "Spring "
	if num[-2:] == "30":
		result = result + "Summer "
	result += num[:4]
	return result
def getHeader(curYear, whichDist, type, yearList):
	yearDropDownOptions=""
	distDropDownOptions=""
	sortByDropDownOptions=""
	
	for year in yearList:
		if year == curYear:
			yearDropDownOptions = yearDropDownOptions + '<option value='+year+' selected="selected">'+getYearForNumber(year)+'</option>'
		else:
			yearDropDownOptions = yearDropDownOptions + '<option value='+year+'>'+getYearForNumber(year)+'</option>'
	if whichDist == 0:
		distDropDownOptions = distDropDownOptions + '<option value="none" selected="selected">None</option>'
	else:
		distDropDownOptions = distDropDownOptions + '<option value="none">None</option>'
	if whichDist == 1:
		distDropDownOptions = distDropDownOptions + '<option value="d1.html" selected="selected">I</option>'
	else:
		distDropDownOptions = distDropDownOptions + '<option value="d1">I</option>'
	if whichDist == 2:
		distDropDownOptions = distDropDownOptions + '<option value="d2" selected="selected">II</option>'
	else:
		distDropDownOptions = distDropDownOptions + '<option value="d2">II</option>'
	if whichDist == 3:
		distDropDownOptions = distDropDownOptions + '<option value="d3" selected="selected">III</option>'
	else:
		distDropDownOptions = distDropDownOptions + '<option value="d3" >III</option>'
	
	if type == "workload":
		sortByDropDownOptions = sortByDropDownOptions  + '<option value="workload" selected = "selected">Workload</option>'
	else:
		sortByDropDownOptions = sortByDropDownOptions  + '<option value="workload">Workload</option>'
	if type == "quality":
		sortByDropDownOptions = sortByDropDownOptions  + '<option value="quality" selected="selected">Quality</option>'
	else:
		sortByDropDownOptions = sortByDropDownOptions  + '<option value="quality">Quality</option>'
	
	
	return '<div id="divBottom" style=" width:400px"><div id="divCourseSelection" class="leftCol" style=" min-width:375px; padding: 0px 0px; margin: 0px 0px 0px 0px; border-color:Blue; border-width:1px; border-style:solid; background-color:#FFF8DC">Semester\t<select id="semesterDropDown">'+yearDropDownOptions+'</select><br>Distribution Group\t<select id="ddlMyList">'+distDropDownOptions+'</select><br>Sort By \t<select id="sortByDropDown">'+sortByDropDownOptions+'</select><br><button type="button" onclick="navigateToSite()">Update</button></div></div><script>function navigateToSite(){var ddl = document.getElementById("ddlMyList");var dd2=document.getElementById("sortByDropDown"); var semDD = document.getElementById("semesterDropDown"); var selectedVal = "../"+semDD.options[semDD.selectedIndex].value+"/"+ddl.options[ddl.selectedIndex].value+dd2.options[dd2.selectedIndex].value+".html";window.location = selectedVal;}</script>'

def printToHTML(html, year, type, distNum, filename, yearList):
	f = open(filename, 'w')
	f.write("<html><body>")
	f.write(getHeader(year, type, distNum, yearList))
	f.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"stylesheet.css\">")
	f.write(html)
	f.write("</body></html>")
	f.close()
	
def main():
	yearList = ["201210", "201320"]
	sortList = ["quality", "workload"]
	for year in yearList:
		for type in sortList:
			allList = []
			d1List = []
			d2List = []
			d3List = []
			
			getCoursesForParameters(year, allList, d1List, d2List, d3List);
			data = getData(year, type)
			
			#gat all
			allCourses = getDataForCourses(data, allList)
			html = dataToHTML(allCourses, type)
			printToHTML(html,year, 0, type, year+"/none"+type+".html", yearList)

			#get d1
			distributionCourses = getDataForCourses(data, d1List)
			html = dataToHTML(distributionCourses, type)
			printToHTML(html,year, 1, type, year+"/d1"+type+".html", yearList)

			#get d2
			distributionCourses = getDataForCourses(data, d2List)
			html = dataToHTML(distributionCourses, type)
			printToHTML(html,year, 2, type, year+"/d2"+type+".html", yearList)
			
			#get d3
			distributionCourses = getDataForCourses(data, d3List)
			html = dataToHTML(distributionCourses, type)
			printToHTML(html,year, 3, type, year+"/d3"+type+".html", yearList)
main()