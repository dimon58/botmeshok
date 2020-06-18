import asyncio
import pyppeteer
import configs

async def page_screenshot(url,xpath='/html/body/div/div/div/main/div[2]/div/div[1]',out_file_name='WolframScreen.png'):
    browser = await pyppeteer.launch()
    page = await browser.newPage()
    await page.goto(url)
    await asyncio.sleep(configs.wolfram_computation_time)
    await page.setViewport(dict(width=3840, height=2160))
    # await page.waitForXPath('/html')
    element = await page.xpath(xpath)
    await element[0].screenshot({'path': 'temp/'+out_file_name})
    await browser.close()
    return 'temp/'+out_file_name

def encode_hex_for_wl(s:str):
    res=''
    for i in s:
        if i.isalpha() or i.isdigit():
            res+=i
        else:
            if i.isspace():
                res += '+'
            else:
                res += '%' + i.encode('ascii').hex().upper()
    return res

def remove_spaces(s:str):
    res = ''
    for i in s:
        if not i.isspace():
            res+=i
    return res


# s = 'dsfsdkgsd ksdhg sdlg sdlk gsd\nsdnsdg sd s    sdf'
# print(remove_spaces(s))