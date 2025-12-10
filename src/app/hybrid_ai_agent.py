import asyncio
from playwright.async_api import async_playwright


PRODUCT_URL = "https://www.etsy.com/listing/1457510417/western-cowgirl-concert-tee-retro?ls=r&ref=hp_recent_activity_hub-2&sr_prefetch=0&pf_from=home&pro=1&content_source=1191481dc114d943f9865bcbd3a58a2f%253ALT5b88d3a931030a97ee08a60ed6cbe4ffdcd21065&logging_key=1191481dc114d943f9865bcbd3a58a2f%3ALT5b88d3a931030a97ee08a60ed6cbe4ffdcd21065"
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # bật UI cho dễ debug
        page = await browser.new_page()

        # async def handle_shopee(response):
        #     if "api/v4/recommend/product_detail_page" in response.url and response.status == 200:
        #         try:
        #             json_data = await response.json()
        #         except Exception as e:
        #             print(f"Không parse được JSON: {e}")
        #             return

        #         data = json_data.get("data") or {}
        #         # price = data.get("price")
        #         # name = data.get("name")
        #         # shopid = data.get("shopid")
        #         # itemid = data.get("itemid")

        #         print(f"Đã bắt: data={data}")
        #         # Bỏ listener sau khi đã bắt lần đầu (tùy nhu cầu)
        #         page.off("response", handle_shopee)

        # page.on("response", handle_shopee)


        async def handle_etsy(response):
            #if "gp/product/ajax/twisterDimensionSlotsDefault" in response.url and response.status == 200:
            if "api/v4/recommend/product_detail_page" in response.url and response.status == 200:
                try:
                    json_data = await response.json()
                except Exception as e:
                    print(f"Không parse được JSON: {e}")
                    return

                #data = json_data.get("data") or {}
                # price = data.get("price")
                # name = data.get("name")
                # shopid = data.get("shopid")
                # itemid = data.get("itemid")

                print(f"Đã bắt: data={json_data}")
                # Gỡ listener sau lần bắt đầu tiên; bỏ qua nếu đã bị gỡ trước đó
                try:
                    page.remove_listener("response", handle_etsy)
                except KeyError:
                    pass
            else:
                print(f"Response URL: {response.url}, Status: {response.status}")
            

        page.on("response", handle_etsy)


        # Goto: dùng domcontentloaded và tăng timeout vì Etsy nhiều request nền
        await page.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=60000)

        # Đợi thêm cho các request nền hoàn tất
        await page.wait_for_timeout(3000)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())