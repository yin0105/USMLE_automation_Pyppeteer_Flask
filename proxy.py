from asyncio.windows_events import NULL
from logging import error
import pprint
import asyncio
from pyppeteer import launch
import requests
import time
import json

users = {}
users_category = []

async def get_browser():
    return await launch({"headless": False, "defaultViewport": NULL}, args=[ '--start-maximized' ])


async def get_page(browser, exam):
    page = await browser.newPage()    
    await page.goto("https://securereg3.prometric.com/landing.aspx?prg=STEP" + str(exam + 1))
    return page


# async def extract_data(page):
#     elements = await page.xpath(
#         '//table[@class="infobox"]/tbody/tr[th and td]')
#     result = {}
#     for element in elements:
#         title, content = await page.evaluate(
#             '''(element) =>
#                 [...element.children].map(child => child.textContent)''',
#             element)
#         result.update({title: content})
#     return result


async def work(browser, exam):
    global users_category
    page = await get_page(browser, exam)
    for user_id, user in users_category[exam].items():        
        # Select Country
        selector_str = "select[id='masterPage_cphPageBody_ddlCountry']"
        option = (await page.xpath("//select[@id='masterPage_cphPageBody_ddlCountry']/option[text()='" + user['country'] + "']"))[0]
        value = await (await option.getProperty('value')).jsonValue()
        await page.select('#masterPage_cphPageBody_ddlCountry', value) 

        # Select State
        try:
            option = (await page.xpath("//select[@id='masterPage_cphPageBody_ddlStateProvince']/option[2]"))[0]
            value = await (await option.getProperty('value')).jsonValue()
            await page.select('#masterPage_cphPageBody_ddlStateProvince', value) 
        except :
            pass

        try:
            await page.click("#masterPage_cphPageBody_btnNext")
            await page.waitFor(3000)
        except:
            pass

        try:
            await page.click("img[alt='Search for available seats']")
            await page.waitFor(5000)
        except:
            print("img error")

        try:
            for key, location_list in user["locations"].items():
                for location in location_list:
                    print("location : " + location["l"] + " , center_number : " + location["c"])
                    # if time.perf_counter() - start_time >= 1800: break  # 30 minutes - replace proxy

                    elem = await page.querySelector("span[class='bodyTitles']") 
                    text = await page.evaluate('(elem) => elem.textContent', elem)
                    print("text = " + text)
                    if text.find("The page cannot be displayed") > -1 :
                        # my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                        print("The page cannot be displayed")
                        raise Exception("cannot_displayed")
                    print("1")
                    await page.waitFor(5000)
                    site_index = 0
                    # # pprint.pprint(location)
                    # my_logging(self.name, "location : " + location["l"] + " , center_number : " + location["c"])

                    # ######## break ##############
                    # if proxy_status[self.name] == 0: 
                    #     browser.close()
                    #     break

                    await page.focus('#txtSearch')
                    print("2")
                    await page.keyboard.type(location["l"])
                    print("3")
                    await page.waitFor(2000)
                    # elem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "txtSearch")))
                    # ######## break ##############
                    # if proxy_status[self.name] == 0: 
                    #     browser.close()
                    #     break

                    # elem.clear()
                    # elem.send_keys(location["l"])
                    # time.sleep(2)

                    await page.click("#btnSearch")
                    await page.waitFor(5000)

                    # elem, f = find_elem(False, browser, browser, "//*[@id='btnSearch']")
                    # if f == False : raise Exception("Not found element")
                    # elem.click()

                    
                    elem = await page.querySelector("span[class='bodyTitles']") 
                    text = await page.evaluate('(elem) => elem.textContent', elem)
                    print("text = " + text)
                    if text.find("The page cannot be displayed") > -1 :
                        # my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                        raise Exception("cannot_displayed")


                    await page.waitFor(100000)
        except:
            print("error: ")
                        
        time.sleep(200)


        await page.waitFor(10000)
    await page.close()
    return


async def main():
    global users, users_category
    browser = await get_browser()
    while True:
        response = requests.get("http://localhost:5000/api")
        print(json.dumps(response.json(), sort_keys=True, indent=4))
        users = response.json()
        users_category = []
        users_category.append({})
        users_category.append({})
        users_category.append({})
        if len(users) > 0 :
            for key, user in users.items():
                users_category[user["exam"]][key] = user
                # print(user)
            for i in range(3):
                print("exam = " + str(i))
                if len(users_category[i]) > 0 :                    
                    await work(browser, i)
                    # await browser.close()

                # for key, user in users_category[i].items():
                #     print("key = " + str(key))
                #     print(user)
        else:
            time.sleep(1)
        # browser = await get_browser()
        # result = {}
        # for name, url in languages.items():
        #     result.update(await extract(browser, name, url))
        # return result


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())