from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import json
from selenium.common.exceptions import NoSuchElementException
import inquirer
import time
import math
from progress.bar import Bar
from alive_progress import alive_bar
from selenium.webdriver.edge.options import Options
from time import sleep


options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])


driver = webdriver.Edge(options=options)
driver.get("https://artofproblemsolving.com/wiki/index.php/AMC_Problems_and_Solutions")


try:
	contests_dict = json.load(open("contests.json", "r"))
except Exception as e:
	contests_dict = {}


contests = {contest_anchor.get_attribute("title").removesuffix(" Problems and Solutions"):contest_anchor for contest_anchor in driver.find_element(By.CSS_SELECTOR, ".mw-parser-output>ul").find_elements(By.TAG_NAME, "a")}

random_emoji = random.choice("🤖😼🦁🦝🐲🐢🐬🦚🐤")
contest_title = inquirer.prompt([inquirer.List("contest", message=f"૮ɦσσรε αɳ αɱ૮ ૮σɳƭεรƭ {random_emoji}", choices=list(contests.keys()))])["contest"]
contest_link = contests[contest_title].get_attribute("href")



parent_window = driver.current_window_handle

if not contest_title in contests_dict:
	contests_dict[contest_title] = {}

driver.switch_to.new_window("tab")
driver.get(contest_link)


paper_anchors = driver.find_element(By.CSS_SELECTOR, ".mw-parser-output>.wikitable,.mw-parser-output>ul").find_elements(By.TAG_NAME, "a")
problems_loaded = 0
max_number_of_problems = 0

total_number_of_problems = None
number_of_problems = None
progress_bar = None
update_progress_bar = None


for paper_anchor in paper_anchors:
	new_parent_window = driver.current_window_handle

	paper_link = paper_anchor.get_attribute("href")
	paper_title = paper_anchor.get_attribute("title")


	if contest_title in contests_dict:
		if paper_title in contests_dict[contest_title]:
			number_of_problems = len(contests_dict[contest_title][paper_title])
			problems_loaded += number_of_problems
			max_number_of_problems = max(max_number_of_problems, number_of_problems)
			continue


	problems_list = []

	driver.switch_to.new_window("tab")
	driver.get(paper_link)



	problem_anchors = driver.find_elements(By.CSS_SELECTOR, "li>a[title*='Problem ']")
	max_number_of_problems = max(max_number_of_problems, len(problem_anchors))
	
	for problem_anchor in problem_anchors:
		if total_number_of_problems == None:
			total_number_of_problems = len(paper_anchors) * len(problem_anchors)
			progress_bar = alive_bar(total_number_of_problems)
			update_progress_bar = progress_bar.__enter__()
			update_progress_bar.title = "ֆƈʀǟքɨռɢ ȶɦɛ աɛɮ 🌐"

			if problems_loaded > 0:
				update_progress_bar.__call__(problems_loaded, skipped=True)


		new_new_parent_window = driver.current_window_handle

		try:
			problem_link = problem_anchor.get_attribute("href")
			problem_title = problem_anchor.get_attribute("innerText")

			driver.switch_to.new_window("tab")
			driver.get(problem_link)


			
			problem_header = driver.find_element(By.CSS_SELECTOR, ".mw-parser-output>p")
			problem_html = ""

			while True:
				problem_html += problem_header.get_attribute("outerHTML")
				problem_header = problem_header.find_element(By.XPATH, "following-sibling::*[1]")

				if problem_header.tag_name == "h2":
					break

			solution_htmls_list = []
			
			for solution_header in driver.find_elements(By.XPATH, "//span[starts-with(@id,'Solution')]/parent::h2/following-sibling::*[1]"):
				solution_html = ""

				while True:
					solution_html += solution_header.get_attribute("outerHTML")

					try:
						solution_header = solution_header.find_element(By.XPATH, "following-sibling::*[1]")
					except NoSuchElementException:
						break

					if solution_header.tag_name != "p":
						break

				solution_htmls_list.append(solution_html)

			
			try:
				video_solution_links_list = [p.get_attribute("href") for p in driver.find_elements(By.XPATH, "//span[starts-with(@id,'Video_Solution')]/parent::h2//following-sibling::p[1]/a")]
			except NoSuchElementException:
				video_solution_links_list = []

			problems_list.append({"problem": problem_html, "solutions": solution_htmls_list, "video_solutions": video_solution_links_list})
		except NoSuchElementException:
			problems_list.append({"problem": "", "solutions": [], "video_solutions": []})


		driver.close()
		driver.switch_to.window(new_new_parent_window)
		
		update_progress_bar.__call__()
		problems_loaded += 1


	driver.close()
	driver.switch_to.window(new_parent_window)

	contests_dict[contest_title][paper_title] = problems_list
	open("contests.json", "w").write(json.dumps(contests_dict, indent=4))


driver.close()
driver.switch_to.window(parent_window)

if total_number_of_problems:
	while problems_loaded < total_number_of_problems:
		update_progress_bar.__call__()
		problems_loaded += 1

	progress_bar.__exit__(None, None, None)

random_emoji = random.choice("✅☑️✔️")
print(f"𝔻𝕠𝕟𝕖 𝕤𝕔𝕣𝕒𝕡𝕚𝕟𝕘 {random_emoji}\n")


start, end = list(inquirer.prompt([inquirer.Text("start", message="Start at 🐣"), inquirer.Text("end", message="End at 🪦")]).values())

if not start.isdigit() or not end.isdigit() or (start := int(start)) > (end := int(end)) or start < 1 or start > max_number_of_problems:
	start, end = 1, max_number_of_problems

start, end = max(1, start), min(max_number_of_problems, end)


worksheet_problems = []
worksheet_solutions = []

eligible_papers = [paper for paper in list(contests_dict[contest_title].values()) if len(paper) >= end]

for i in range(start-1, end):
	problem = ""

	while problem == "":
		paper = random.choice(eligible_papers)[i]
		problem = paper["problem"]
		solutions = paper["solutions"]

	worksheet_problems.append(problem)
	worksheet_solutions.append(solutions)


worksheet_problems_string = "\n".join([f"<li>{problem_html}</li>" for problem_html in worksheet_problems])
worksheet_solutions_string = "\n".join([f"<li>{solution_html}</li>" for solution_html in ["\n".join(worksheet_solution) for worksheet_solution in worksheet_solutions]])

worksheet_html_content = f"""<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title></title>
</head>
<body style="padding: 2em; font-family: Courier New">
	<h1 style="padding-bottom: 1em">Problems</h1>
	<ol>
	{worksheet_problems_string}
	</ol>

	<br/>
	<br/>

	<h1 style="padding-bottom: 1em">Solutions</h1>
	<ol>
	{worksheet_solutions_string}
	</ol>
</body>
</html>"""

worksheet_html_content = worksheet_html_content.replace("""src="//""", """src="https://""").replace("""href="//""", """href="https://""")

worksheet_filename = "worksheet.html"
worksheet_file = open(worksheet_filename, "w")
worksheet_file.write(worksheet_html_content)
worksheet_file.close()

random_emoji = random.choice("🎉🙌🥳🥂")
sleep(1)
print(f"\nWorksheet has been successfully generated {random_emoji} Check '{worksheet_filename}'❗")

sleep(2)
